import xml.etree.ElementTree as ET
import json

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.auth.auth import (
    token_required,
    admin_required,
)

from app.database import get_session
from app.config.settings import OM2M_URL, OM2M_USERNAME, OM2M_PASSWORD
from app.utils.om2m_lib import Om2m
from app.schemas.verticals import VerticalCreate, VerticalGetAll, VerticalDelete
from app.models.vertical import Vertical as DBAE
from app.utils.utils import gen_vertical_code

router = APIRouter()

om2m = Om2m(OM2M_USERNAME, OM2M_PASSWORD, OM2M_URL)


@router.post("/create-ae")
@token_required
@admin_required
def create_ae(
    vertical: VerticalCreate,
    request: Request,
    session: Session = Depends(get_session),
    current_user=None,
):
    """
    Create an AE (Application Entity) with the given name and labels.

    Args:
        vertical (VerticalCreate): The data required to create the AE.
        request (Request): The HTTP request object.
        session (Session, optional): The database session. Defaults to Depends(get_session).

    Returns:
        int: The status code of the operation.

    Raises:
        HTTPException: If there is an error creating the AE or if the AE already exists.
    """
    _, _ = current_user, request
    assigned_name = gen_vertical_code(vertical.ae_name)
    if len(vertical.labels) == 0:
        labels = [vertical.ae_name]
    status_code, data = om2m.create_ae(assigned_name, vertical.path, labels=labels)
    print("Here too", status_code, data)
    if status_code == 201:
        res_id = json.loads(data)["m2m:ae"]["ri"].split("/")[-1]
        db_vertical = DBAE(
            res_name=assigned_name,
            labels=labels,
            orid=res_id,
            description=vertical.ae_description,
        )
        session.add(db_vertical)
        session.commit()
        print("AE created")
        raise HTTPException(status_code=201, detail="AE created")
    elif status_code == 409:
        raise HTTPException(status_code=409, detail="AE already exists")
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating AE " + str(status_code),
        )
    # return status_code


@router.get("/get-aes")
@token_required
def get_aes(
    vertical: VerticalGetAll,
    request: Request,
    current_user=None,
    session: Session = Depends(get_session),
):
    """
    Retrieves the Application Entities in a given path.

    Parameters:
    - vertical (VerticalGetAll): The vertical object containing the path to retrieve the subcontainers from.
    - request (Request): The request object.
    - current_user (optional): The current user.
    - session (Session): The database session.

    Returns:
    - list: A list of dictionaries containing the "rn" and "ri" attributes of each subcontainer.

    Raises:
    - HTTPException: If the path is not found or there is an error parsing XML.
    - Exception: If there is an error retrieving AE.
    """
    path = vertical.path
    parent = "m2m:ae"
    is_direct_child = (
        lambda element, root: element in root and len(element.findall("..")) == 0
    )

    try:
        data = om2m.get_all_containers(path).text
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Path not found"
            )
        root = ET.fromstring(data)
        m2m_ae_elements = root.findall(
            f".//{parent}", {"m2m": "http://www.onem2m.org/xml/protocols"}
        )
        first_level_ae_elements = []
        for ae_element in m2m_ae_elements:
            if is_direct_child(ae_element, root):
                first_level_ae_elements.append(ae_element)
        aes = [
            {"rn": ae_element.get("rn"), "ri": ae_element.find("ri").text}
            for ae_element in first_level_ae_elements
        ]
        return aes
    except ET.ParseError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error parsing XML",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving AE {e}")


@router.delete("/delete-ae")
@token_required
@admin_required
def delete_ae(
    vertical: VerticalDelete,
    request: Request,
    session: Session = Depends(get_session),
    current_user=None,
):
    """
    This function deletes an AE resource in OM2M.

    Args:
        vertical (VerticalDelete): The vertical object containing the AE name to be deleted.
        request (Request): The HTTP request object.
        session (Session, optional): The database session. Defaults to Depends(get_session).

    Returns:
        int: The status code of the request.
    """
    ae = session.query(DBAE).filter(DBAE.res_name == vertical.ae_name).first()
    if ae is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="AE not found"
        )
    if vertical.path == "":
        final_path = f"{vertical.ae_name}"
    else:
        final_path = f"{vertical.path}/{vertical.ae_name}"
    status_code = om2m.delete_resource(final_path).status_code
    print(status_code)
    if status_code >= 200 and status_code < 300:
        session.delete(ae)
        session.commit()
        raise HTTPException(status_code=200, detail="AE deleted")
    elif status_code == 404:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="AE not found"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting AE",
        )

    return status_code
