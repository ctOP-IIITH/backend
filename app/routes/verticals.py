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
from app.utils.create import create_vertical

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
    # assigned_name = gen_vertical_code(vertical.ae_name)
    if len(vertical.labels) == 0:
        vertical.labels = [vertical.ae_name]

    status_code = create_vertical(
        vertical.ae_name,
        vertical.ae_short_name,
        vertical.ae_description,
        vertical.labels,
        session,
    )
    if status_code == 201:
        raise HTTPException(status_code=201, detail="AE created")
    elif status_code == 409:
        raise HTTPException(status_code=409, detail="AE already exists")
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating AE " + str(status_code),
        )
    # return status_code


@router.get("/all")
@token_required
def get_all(
    request: Request,
    current_user=None,
    session: Session = Depends(get_session),
):
    """
    Retrieves all the verticals in the database.
    """
    _, _ = current_user, request
    verticals = session.query(DBAE).all()
    return verticals


@router.delete("/delete-ae/{vert_id}")
@token_required
@admin_required
def delete_ae(
    request: Request,
    vert_id: int,
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
    _, _ = current_user, request
    ae = session.query(DBAE).filter(DBAE.id == vert_id).first()
    print(ae)
    if ae is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="AE not found"
        )
    final_path = f"{ae.res_short_name}"
    status_code = om2m.delete_resource(final_path).status_code
    print(status_code)
    if status_code >= 200 and status_code < 300:
        session.delete(ae)
        session.commit()
        raise HTTPException(status_code=204, detail="AE deleted")
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
