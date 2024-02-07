import ast
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

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
)
from app.schemas.nodes import NodeCreate, NodeDelete
from app.models.vertical import Vertical as DBVertical
from app.models.node import Node as DBNode
from app.models.sensor_types import SensorTypes as DBSensorType
from app.config.settings import OM2M_URL, OM2M_USERNAME, OM2M_PASSWORD

router = APIRouter()

om2m = Om2m(OM2M_USERNAME, OM2M_PASSWORD, OM2M_URL)

# TODO : Add the Database functions


@router.post("/create-node")
@token_required
@admin_required
def create_node(
    node: NodeCreate,
    request: Request,
    session: Session = Depends(get_session),
    current_user=None,
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
    _, _ = current_user, request
    con = (
        session.query(DBSensorType)
        .filter(DBSensorType.id == node.sensor_type_id)
        .first()
    )
    if con is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Sensor type not found"
        )

    vert_name = get_vertical_name(node.sensor_type_id, session)
    if vert_name is None:
        print("vertical not found")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Non Existing Domain, please check the sensor type",
        )

    print(vert_name, node.sensor_type_id, node.latitude, node.longitude)
    res_id = get_node_code(
        vert_name, node.sensor_type_id, node.latitude, node.longitude, session
    )

    response = om2m.create_container(res_id, f"{vert_name}", labels=[vert_name, res_id])

    if response.status_code == 201:
        res_data = om2m.create_container(
            "Data", f"{vert_name}/{res_id}", labels=["Data", res_id]
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
        )

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
                raise HTTPException(status_code=201, detail="Node created")
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
    response = om2m.get_containers(ri=data_orid, all=True)

    if response.status_code == 200:
        all_data = response.json()

        # Extract labels and content instances from the response
        labels = all_data.get("m2m:cnt", {}).get("lbl", [])
        content_instances = all_data.get("m2m:cnt", {}).get("m2m:cin", [])

        # Prepare content instances data
        cins = [(ast.literal_eval(x["con"]), x["lt"]) for x in content_instances]

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

    cur_node = session.query(DBNode).filter(DBNode.node_name == path).first()
    print(path, cur_node)
    if cur_node is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Node not found",
        )
    data_orid = cur_node.node_data_orid
    print(data_orid)
    response = om2m.get_containers(ri=data_orid, all=True)

    if response.status_code == 200:
        la_url = response.json().get("m2m:cnt", {}).get("la", "")
        # /in-cse/in-name/AE-WF/WATER_QUANTITY01-0000-0001/Data/la
        # We need AE-WF/WATER_QUANTITY01-0000-0001/Data
        la_url = "/".join(la_url.split("/")[-4:-1])
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
