import ast
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.schemas.nodes import NodeCreate
from app.models.node import Node as DBNode

from app.auth.auth import (
    token_required,
    admin_required,
)
from app.database import get_session
from app.utils.om2m_lib import Om2m
from app.utils.utils import (
    get_vertical_name,
    get_sensor_type_name,
    get_next_sensor_node_number,
    get_node_code,
    create_hash,
)
from app.utils.utils import (
    get_node_coordinates_by_id,
    get_node_coordinates_by_name,
)
from app.schemas.nodes import NodeCreate, NodeAssign
from app.models.vertical import Vertical as DBVertical
from app.models.node import Node as DBNode
from app.models.user import User as DBUser
from app.models.user_types import UserType
from app.models.node_owners import NodeOwners as DBNodeOwners
from app.models.sensor_types import SensorTypes as DBSensorType
from app.config.settings import OM2M_URL, MOBIUS_XM2MRI, JWT_SECRET_KEY

router = APIRouter()

om2m = Om2m(MOBIUS_XM2MRI, OM2M_URL)


@router.post("/create-node", status_code=201)
@token_required
@admin_required
def create_node(
    node: NodeCreate,
    request: Request,
    session: Session = Depends(get_session),
    current_user=None,
    node_data=None,
):
    """
    Create an Node (Container) with the given name and labels.

    Args:
        node (NodeCreate): The data required to create a new node.
        request (Request): The HTTP request object.
        session (Session): The database session.

    Returns:
        int: The status code of the operation.

    Raises:
        HTTPException: If the node already exists or if there is an error creating the node.
    """
    if node_data:
        node = NodeCreate(
            sensor_type_id=node_data['sensor_type_id'],
            latitude=node_data['latitude'],
            longitude=node_data['longitude'],
            area=node_data['area'],
            name=node_data['name']
        )
    _, _ = current_user, request

    con = (
        session.query(DBSensorType)
        .filter(DBSensorType.id == node.sensor_type_id)
        .first()
    )
    if con is None:
        raise HTTPException(status_code=404, detail="Sensor type not found")

    existing_node = session.query(DBNode).filter(DBNode.name == node.name).first()
    if existing_node:
        raise HTTPException(status_code=409, detail=f"Node with {node.name} already exists")

    vert_name = get_vertical_name(node.sensor_type_id, session)
    if vert_name is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vertical not found",
        )

    print(vert_name, node.sensor_type_id, node.latitude, node.longitude)
    res_id = get_node_code(
        vert_name, node.sensor_type_id, node.latitude, node.longitude, session
    )

    response = om2m.create_container(res_id, f"{vert_name}", labels=[vert_name, res_id])
    print(response)
    if response.status_code == 201:
        res_data = om2m.create_container(
            "Data1", f"{vert_name}/{res_id}", labels=["Data", res_id]
        )
        res_desc = om2m.create_container(
            "Descriptor",
            f"{vert_name}/{res_id}",
            labels=["Descriptor", res_id],
        )

        new_node = DBNode(
            labels=[vert_name, res_id],
            sensor_type_id=node.sensor_type_id,
            sensor_node_number=get_next_sensor_node_number(
                node.sensor_type_id, session
            ),
            lat=node.latitude,
            long=node.longitude,
            location=node.area,
            area=node.area,
            orid=response.json()["m2m:cnt"]["ri"].split("/")[-1],
            node_name=res_id,
            node_data_orid=res_data.json()["m2m:cnt"]["ri"].split("/")[-1],
            token_num=None,
            name=node.name
        )
        print("*************************************************************************************\n")
        print(f"RESPONSE -> {response.json()['m2m:cnt']['ri'].split('/')[-1]}, NAME -> {res_id}, ORID -> {res_data.json()['m2m:cnt']['ri'].split('/')[-1]} ")
        print("*************************************************************************************\n")
        if res_data.status_code == 201 and res_desc.status_code == 201:
            session.add(new_node)
            session.commit()

            # Update token_num with the generated id
            new_node.token_num = new_node.id
            session.commit()

            if con:
                parameters = str(con.parameters)
            else:
                raise HTTPException(status_code=404, detail="Sensor type not found")
            sensor = om2m.create_cin(
                f"{vert_name}/{res_id}",
                "Descriptor",
                con=parameters,
                lbl=[get_sensor_type_name(node.sensor_type_id, session)],
            ).status_code
            print(sensor)
            if sensor == 201:
                # return 201 with node details
                return {
                    "node_name": new_node.node_name,
                    "orid": new_node.orid,
                    "node_data_orid": new_node.node_data_orid,
                    "area": new_node.area,
                    "sensor_type": get_sensor_type_name(node.sensor_type_id, session),
                    "sensor_node_number": new_node.sensor_node_number,
                    "lat": new_node.lat,
                    "long": new_node.long,
                    "token_num": new_node.token_num,
                }

            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error creating node",
                )
    elif response.status_code == 409:
        raise HTTPException(status_code=409, detail="Node already exists")
    else:
        print(response.status_code)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating node",
        )
            
@router.post("/assign-vendor")
@token_required
@admin_required
def assign_vendor(
    node: NodeAssign,
    request: Request,
    session: Session = Depends(get_session),
    current_user=None,
):
    """
    Assign a node to a vendor.

    Args:
        node (NodeAssign): The data required to assign a node to a vendor.
        request (Request): The HTTP request object.
        session (Session): The database session.

    Returns:
        int: The status code of the operation.

    Raises:
        HTTPException: If the node or vendor does not exist or if there is an error assigning the node to the vendor.
    """
    _, _ = current_user, request

    # Fetch the node from the database
    node_to_assign = (
        session.query(DBNode).filter(DBNode.node_name == node.node_id).first()
    )
    if not node_to_assign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found",
        )

    # Fetch the vendor from the database
    vendor = session.query(DBUser).filter(DBUser.email == node.vendor_email).first()
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found",
        )

    # check if user is a vendor
    if vendor.user_type != UserType.VENDOR.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not a vendor",
        )

    # Check if the node is already assigned to a vendor
    node_owner = (
        session.query(DBNodeOwners)
        .filter(DBNodeOwners.node_id == node_to_assign.id)
        .first()
    )

    if node_owner:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Node already assigned to a vendor",
        )

    # Assign the node to the vendor
    node_owner = DBNodeOwners(node_id=node_to_assign.id, vendor_id=vendor.id)

    session.add(node_owner)
    session.commit()

    raise HTTPException(status_code=201, detail="Node assigned to vendor")


@router.get("/get-vendor/{node_name}")
@token_required
def get_vendor(
    node_name: str,
    request: Request,
    session: Session = Depends(get_session),
    current_user=None,
):
    """
    Retrieves the vendor assigned to the node with the given name.

    Args:
        node_id (str): The name of the node.
        request (Request): The HTTP request object.
        session (Session, optional): The database session. Defaults to Depends(get_session).

    Returns:
        dict: The vendor object.
    """
    _, _ = current_user, request

    # Fetch the node from the database
    node = session.query(DBNode).filter(DBNode.node_name == node_name).first()
    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found",
        )

    # Fetch the vendor assigned to the node
    # send id, type, username, email
    vendor = (
        session.query(DBUser.id, DBUser.user_type, DBUser.username, DBUser.email)
        .join(DBNodeOwners, DBNodeOwners.vendor_id == DBUser.id)
        .filter(DBNodeOwners.node_id == node.id)
        .first()
    )

    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found",
        )

    # API TOKEN
    api_token = create_hash([vendor.email, node.node_data_orid], JWT_SECRET_KEY)

    return {**vendor._asdict(), "api_token": api_token}


@router.get("/{path}")
@token_required
def get_node(
    path: str,
    request: Request,
    session: Session = Depends(get_session),
    current_user=None,
):
    """
    Retrieves the node with the given name.

    Args:
        path (str): The path of the node.
        request (Request): The HTTP request object.
        session (Session, optional): The database session. Defaults to Depends(get_session).

    Returns:
        dict: The node object.
    """
    _, _ = current_user, request

    nodes = (
        session.query(DBNode)
        .join(DBSensorType, DBSensorType.id == DBNode.sensor_type_id)
        .join(DBVertical, DBVertical.id == DBSensorType.vertical_id)
        .filter(DBVertical.res_name == path)
        .with_entities(
            DBNode.node_name,
            DBNode.orid,
            DBNode.node_data_orid,
            DBNode.area,
            DBSensorType.res_name,
            DBNode.sensor_node_number,
            DBNode.lat,
            DBNode.long,
            DBNode.token_num,
            DBNode.name
        )
        .all()
    )

    return nodes


# get nodename from path parameter
@router.get("/get-node/{path}")
@token_required
def get_nodes(
    request: Request,
    path: str,
    current_user=None,
    session: Session = Depends(get_session),
):
    """
    Retrieves the subcontainers for a given path.

    Parameters:
    - node (NodeGetAll): The node object containing the path to retrieve the subcontainers from.
    - request (Request): The request object.
    - current_user (optional): The current user.
    - session (Session): The database session.

    Returns:
    - list: A list of dictionaries containing the "rn" and "ri" attributes of each subcontainer.
    """
    _, _ = current_user, request

    cur_node = (
        session.query(DBNode)
        .join(DBSensorType, DBSensorType.id == DBNode.sensor_type_id)
        .join(DBVertical, DBVertical.id == DBSensorType.vertical_id)
        .filter(DBNode.node_name == path)
        .with_entities(
            DBNode.node_name,
            DBNode.orid,
            DBNode.node_data_orid,
            DBNode.area,
            DBSensorType.res_name,
            DBSensorType.parameters,
            DBSensorType.data_types,
            DBNode.sensor_node_number,
            DBNode.lat,
            DBNode.long,
            DBNode.token_num,
            DBVertical.res_short_name,
        )
        .first()
    )
    # session.query(DBNode).filter(DBNode.node_name == path).first()
    print(path, cur_node)
    if cur_node is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found",
        )
    data_orid = cur_node.node_data_orid
    print(data_orid)
    response_ae = om2m.get_containers(
        resource_path=cur_node.res_short_name + "/" + path
    )
    response = om2m.get_containers(
        resource_path=cur_node.res_short_name + "/" + path, ri=data_orid, all=True
    )

    if response.status_code == 200:
        all_data = response.json()
        ae_node_data = response_ae.json()
        # Extract labels and content instances from the response
        labels = ae_node_data.get("m2m:cnt", {}).get("lbl", [])
        content_instances = all_data.get("m2m:rsp", {}).get("m2m:cin", [])
        # Prepare content instances data
        cins = [
            (ast.literal_eval(x["con"]), x["lt"])
            for x in content_instances
            if cur_node.parameters[0] not in x["con"]
        ]

        # Merge current node data with labels and content instances
        final_data = {**cur_node, "labels": labels, "cins": cins}
        raise HTTPException(status_code=200, detail=final_data)
    else:
        raise HTTPException(
            status_code=response.status_code,
            detail="Error getting node",
        )


@router.get("/get-node/{path}/latest")
def get_latest_cin(
    path: str,
    request: Request,
    session: Session = Depends(get_session),
    current_user=None,
):
    """
    Retrieves the latest content instance for a given path.

    Returns:
    - list: A list of dictionaries containing the "rn" and "ri" attributes of each subcontainer.
    """
    _, _ = current_user, request

    cur_node = (
        session.query(DBNode)
        .join(DBSensorType, DBSensorType.id == DBNode.sensor_type_id)
        .join(DBVertical, DBVertical.id == DBSensorType.vertical_id)
        .filter(DBNode.node_name == path)
        .with_entities(
            DBNode.node_data_orid,
            DBVertical.res_short_name,
        )
        .first()
    )
    print(path, cur_node)
    if cur_node is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found",
        )

    # /in-cse/in-name/AE-WF/WATER_QUANTITY01-0000-0001/Data/la
    # We need AE-WF/WATER_QUANTITY01-0000-0001/Data
    la_url = f"{cur_node.res_short_name}/{path}/Data"
    print(la_url)
    r = om2m.get_la_cin(la_url)
    if r.status_code == 200:
        return r.json()
    elif r.status_code == 404:
        raise HTTPException(
            status_code=r.status_code,
            detail="No CIN found",
        )
    else:
        raise HTTPException(
            status_code=r.status_code,
            detail="Error getting latest CIN",
        )


@router.delete("/delete-node/{node_name}")
@token_required
@admin_required
def delete_node(
    request: Request,
    node_name: str,
    session: Session = Depends(get_session),
    current_user=None,
):
    """
    Deletes a node with the given name.

    Args:
        node (NodeDelete): The node object containing the node name and path.
        request (Request): The HTTP request object.
        session (Session, optional): The database session. Defaults to Depends(get_session).

    Returns:
        int: The status code of the operation.
    """
    _, _ = current_user, request

    if not node_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Node name is missing",
        )

    # Fetch the node from the database
    node = session.query(DBNode).filter(DBNode.node_name == node_name).first()
    vertical = (
        session.query(DBVertical)
        .join(DBSensorType, DBSensorType.vertical_id == DBVertical.id)
        .filter(DBSensorType.id == node.sensor_type_id)
        .first()
    )

    if not node:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found",
        )
    if not vertical:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vertical not found",
        )

    # check if vendor is assigned to the node
    node_owner = (
        session.query(DBNodeOwners).filter(DBNodeOwners.node_id == node.id).first()
    )

    if node_owner:
        # delete the vendor assignment
        try:
            session.delete(node_owner)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error deleting node owner",
            ) from None

    response = om2m.delete_resource(f"{vertical.res_short_name}/{node_name}")

    if 200 <= response.status_code < 300:
        # Delete the node from the database
        node_to_delete = (
            session.query(DBNode).filter(DBNode.node_name == node_name).first()
        )
        if node_to_delete:
            session.delete(node_to_delete)
            session.commit()
            raise HTTPException(status_code=204, detail="Node deleted")
    else:
        raise HTTPException(
            status_code=response.status_code,
            detail="Error deleting node",
        )

    return response.status_code


@router.get("/meta/id/{node_id}")
def node_lat_long(
    node_id: str,
    request: Request,
    session: Session = Depends(get_session),
    current_user=None,
):
    """
    This function retrieves the latitude and longitude coordinates of a specific node.

    Args:
        node_id (str): The unique identifier of the node.
        request (Request): The HTTP request object. (not used in this function)
        session (Session): The database session object.
        current_user (Any, optional): The currently logged-in user. (not used in this function)

    Returns:
        tuple: A tuple containing the latitude and longitude coordinates of the node.

    Raises:
        HTTPException: An HTTPException with status code 500 (Internal Server Error)
        if there is an error retrieving the coordinates.
    """
    _, _ = current_user, request
    
    coordinates = get_node_coordinates_by_name(node_id, session)
    if not coordinates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Node ID not found"
        )
    return coordinates


@router.get("/meta/vendor/{vendor_username}")
def sensor_node_coordinates_all(
    vendor_username: str,
    request: Request,
    session: Session = Depends(get_session),
    current_user=None,
):
    _, _ = current_user, request
    
    vendor = session.query(DBUser).filter(DBUser.email == vendor_username).first()
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vendor not found",
        )
    vendor_id = vendor.id
    nodes_vendor = (
        session.query(DBNodeOwners)
        .filter(DBNodeOwners.vendor_id == vendor_id)
        .all()
    )
    if not nodes_vendor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No nodes assigned for the given vendor"
        )
    nodes = [i.node_id for i in nodes_vendor]
    data = []
    for i in nodes:
        data.append(get_node_coordinates_by_id(i, session))
    return data