from app.auth.auth import (
    token_required,
    admin_required,
)
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_session
from app.utils.om2m_lib import Om2m
from app.schemas.cin import (
    ContentInstance,
    ContentInstanceGetAll,
    ContentInstanceDelete,
)
import xml.etree.ElementTree as ET
from app.models.node import Node as DBNode

router = APIRouter()

om2m = Om2m("admin", "admin", "http://localhost:8080/~/in-cse/in-name")


@router.post("/create/{token_id}")
def create_cin(
    cin: ContentInstance,
    token_id: str,
    request: Request,
    session: Session = Depends(get_session),
    current_user=None,
):
    """
    Create a CIN (Content Instance) with the given name and labels.

    Args:
        cin (ContentInstance): The content instance object containing the path, content, and labels.
        token_id (str): The token ID.
        request (Request): The HTTP request object.
        session (Session, optional): The database session. Defaults to Depends(get_session).

    Returns:
        int: The status code of the operation.

    Raises:
        HTTPException: If the node token is not found, CIN already exists, or there is an error creating CIN.
    """
    node = session.query(DBNode).filter(DBNode.token_num == token_id).first()
    if node is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Node token not found"
        )
    node_id = node.id

    response = om2m.create_cin(
        cin.path,
        node_id,
        cin.con,
        lbl=cin.lbl,
    )
    if response.status_code == 201:
        return response.status_code
    elif response.status_code == 409:
        raise HTTPException(status_code=409, detail="CIN already exists")
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating CIN",
        )


@router.get("/get-cins")
@token_required
def get_cins(
    cin: ContentInstanceGetAll,
    request: Request,
    session: Session = Depends(get_session),
    current_user=None,
):
    """
    Retrieve all Content Instances (CINs) from the specified path.

    Args:
        cin (ContentInstanceGetAll): The ContentInstanceGetAll model.
        request (Request): The request object.
        session (Session, optional): The database session. Defaults to Depends(get_session).

    Returns:
        List[Dict[str, str]]: A list of dictionaries containing the 'rn', 'ri', and 'con' attributes of each CIN.

    Raises:
        HTTPException: If there is an error retrieving the nodes.
    """
    path = cin.path
    parent = "m2m:cin"
    is_direct_child = (
        lambda element, root: element in root and len(element.findall("..")) == 0
    )

    try:
        root = ET.fromstring(om2m.get_all_containers(path).text)
        m2m_cin_elements = root.findall(
            f".//{parent}", {"m2m": "http://www.onem2m.org/xml/protocols"}
        )

        first_level_cin_elements = []
        for cin_element in m2m_cin_elements:
            if is_direct_child(cin_element, root):
                first_level_cin_elements.append(cin_element)

        cins = [
            {
                "rn": cin_element.get("rn"),
                "ri": cin_element.find("ri").text,
                "con": cin_element.find("con").text,
            }
            for cin_element in first_level_cin_elements
        ]
        return cins
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving nodes. {e}",
        )


@router.delete("/delete")
@token_required
@admin_required
def delete_cin(
    cin: ContentInstanceDelete,
    request: Request,
    session: Session = Depends(get_session),
    current_user=None,
):
    """
    Deletes a resource in OM2M.

    Parameters:
    - cin: ContentInstanceDelete object containing information about the Content Instance to be deleted.
    - request: Request object containing the HTTP request information.
    - session: Session object representing the database session.

    Raises:
    - HTTPException with status code 404 if the Node token is not found.
    - HTTPException with status code 200 if the CIN is deleted successfully.
    - HTTPException with status code 404 if the CIN is not found.
    - HTTPException with status code 500 if there is an error deleting the CIN.

    Returns:
    - None
    """
    node = session.query(DBNode).filter(DBNode.id == cin.node_id).first()
    if node is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Node token not found"
        )

    try:
        response = om2m.delete_resource(f"{cin.path}/{cin.cin_id}")
        if response.status_code == 200:
            # the CIN can be deleted from the database (CLARIFICATION REQUIRED)
            raise HTTPException(status_code=200, detail="CIN deleted Successfully")
        elif response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="CIN not found"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting CIN. {e}",
        )
