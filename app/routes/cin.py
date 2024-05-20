import xml.etree.ElementTree as ET
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.auth.auth import (
    token_required,
    admin_required,
)
from app.database import get_session
from app.utils.om2m_lib import Om2m
from app.utils.utils import get_vertical_name, create_hash
from app.schemas.cin import (
    ContentInstance,
    ContentInstanceGetAll,
    ContentInstanceDelete,
)
from app.models.node import Node as DBNode
from app.models.node_owners import NodeOwners as DBNodeOwners
from app.models.user import User as DBUser
from app.models.sensor_types import SensorTypes as DBSensorType
from app.config.settings import OM2M_URL, MOBIUS_XM2MRI, JWT_SECRET_KEY

router = APIRouter()

om2m = Om2m(MOBIUS_XM2MRI, OM2M_URL)


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
    _, _ = current_user, request
    node = session.query(DBNode).filter(DBNode.token_num == token_id).first()
    if node is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Node token not found"
        )

    # Check if vendor is assigned to the node
    vendor = (
        session.query(DBUser.id, DBUser.user_type, DBUser.username, DBUser.email)
        .join(DBNodeOwners, DBNodeOwners.vendor_id == DBUser.id)
        .filter(DBNodeOwners.node_id == node.id)
        .first()
    )

    if vendor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not assigned to the node",
        )

    # Check Auth
    # get Bearer Token from headers
    bearer_auth_token = request.headers.get("Authorization")
    if bearer_auth_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization token is missing",
        )
    bearer_auth_token = bearer_auth_token.split(" ")[1]

    # Hash
    hash_token = create_hash([vendor.email, node.node_data_orid], JWT_SECRET_KEY)
    if bearer_auth_token != hash_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization token is invalid",
        )

    vertical_name = get_vertical_name(node.sensor_type_id, session)
    print(node.orid, vertical_name)

    sensor_type = (
        session.query(DBSensorType)
        .filter(DBSensorType.id == node.sensor_type_id)
        .first()
    )
    print(cin, sensor_type)
    cin = cin.dict()
    con = []
    # check if all of sensor_type.paramaters are in cin
    # if not, raise error
    # if it is then check if datatype matches with sensor_type.data_tpes[idx]
    for idx, param in enumerate(sensor_type.parameters):
        print(idx, param, cin, param in cin)
        if param not in cin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing parameter " + param,
            )
        expected_type = sensor_type.data_types[idx]
        if expected_type == "str" or expected_type == "string":
            expected_type = str
        elif expected_type == "int":
            expected_type = int
        elif expected_type == "float":
            expected_type = float

        if not isinstance(cin[param], expected_type):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Wrong data type for "
                + param
                + ". Expected "
                + str(sensor_type.data_types[idx])
                + " but got "
                + str(type(cin[param])),
            )
        con.append(str(cin[param]))
        print(con)
    response = om2m.create_cin(
        vertical_name,
        node.node_name,
        str(con),
        lbl=list(cin.keys()),
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

    response = om2m.delete_resource(f"{cin.path}/{cin.cin_id}")
    print(response.status_code)
    if response.status_code == 200:
        # the CIN can be deleted from the database (CLARIFICATION REQUIRED)
        return {"status": "CIN deleted"}
    elif response.status_code == 404:
        print("CIN not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="CIN not found"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting CIN",
        )
