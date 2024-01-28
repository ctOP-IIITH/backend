import xml.etree.ElementTree as ET
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
    # get vertical id
    vert_id = session.query(DBVertical).filter(DBVertical.res_name == path).first()
    if vert_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vertical not found"
        )
    # get all sensor types for the vertical
    sensor_types = (
        session.query(DBSensorType).filter(DBSensorType.vertical_id == vert_id.id).all()
    )
    if sensor_types is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No sensor types found"
        )
    # get all nodes for the sensor types
    nodes = []
    for sensor_type in sensor_types:
        nodes.extend(
            session.query(DBNode).filter(DBNode.sensor_type_id == sensor_type.id).all()
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
    parent = "m2m:cnt"
    is_direct_child = (
        lambda element, root: element in root and len(element.findall("..")) == 0
    )

    try:
        root = ET.fromstring(om2m.get_all_containers(path).text)
        m2m_cnt_elements = root.findall(
            f".//{parent}", {"m2m": "http://www.onem2m.org/xml/protocols"}
        )

        first_level_cnt_elements = []
        for cnt_element in m2m_cnt_elements:
            if is_direct_child(cnt_element, root):
                first_level_cnt_elements.append(cnt_element)

        aes = [
            {"rn": cnt_element.get("rn"), "ri": cnt_element.find("ri").text}
            for cnt_element in first_level_cnt_elements
        ]
        return aes
    except ET.ParseError:
        raise HTTPException(
            status_code=500,
            detail="Error parsing XML",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving nodes. {e}",
        )


@router.delete("/delete-node")
@token_required
@admin_required
def delete_node(
    node: NodeDelete,
    request: Request,
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
    node_name = node.node_name
    path = node.path
    if not node_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Node name is missing",
        )

    if not path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Path is missing",
        )

    response = om2m.delete_resource(f"{path}/{node_name}")

    if 200 <= response.status_code < 300:
        # Delete the node from the database
        node_to_delete = (
            session.query(DBNode).filter(DBNode.node_name == node_name).first()
        )
        if node_to_delete:
            session.delete(node_to_delete)
            session.commit()
            raise HTTPException(status_code=200, detail="Node deleted")
    else:
        raise HTTPException(
            status_code=response.status_code,
            detail="Error deleting node",
        )

    return response.status_code
