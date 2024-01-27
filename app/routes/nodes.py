from app.auth.auth import (
    token_required,
    admin_required,
)
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_session
from app.utils.om2m import Om2m
import xml.etree.ElementTree as ET
from app.schemas.nodes import NodeCreate, NodeGetAll, NodeDelete
from app.models.node import Node as DBNode
from app.models.sensor_types import SensorTypes as DBSensorType

router = APIRouter()

om2m = Om2m("admin", "admin", "http://localhost:8080/~/in-cse/in-name")

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
    Create an AE (Application Entity) with the given name and labels.

    Args:
        node (NodeCreate): The data required to create a new node.
        request (Request): The HTTP request object.
        session (Session): The database session.

    Returns:
        int: The status code of the operation.

    Raises:
        HTTPException: If the node already exists or if there is an error creating the node.
    """
    # ! TODO: Make the sensor type a cin in Descriptor
    node_name = node.node_name
    # ! TODO: insert a entity of DBNode
    # new_node = DBNode(orid=node_name, path=node.path)
    response = om2m.create_container(node_name, node.path, labels=[node_name])
    assigned_token_num = 0
    # ! TODO: Generate a token number
    # ! TODO: Verify the database..

    new_node = DBNode(
        node_name=node.node_name,
        labels=node.labels,
        sensor_type_id=node.sensor_type_id,
        sensor_node_number=node.sensor_node_number,
        lat=node.lat,
        long=node.long,
        location=node.location,
        landmark=node.landmark,
        area=node.area,
        orid=response.json()["m2m:ae"]["ri"].split("/")[-1],
        token_num=assigned_token_num,
    )
    if response.status_code == 201:
        res_data = om2m.create_container(
            "Data", f"{node.path}/{node_name}", labels=["Data", node_name]
        )
        res_desc = om2m.create_container(
            "Descriptor", f"{node.path}/{node_name}", labels=["Descriptor", node_name]
        )
        if res_data.status_code == 201 and res_desc.status_code == 201:
            # session.add(new_node)
            # session.commit()
            con = (
                session.query(DBSensorType)
                .filter(DBSensorType.res_name == node_name)
                .first()
            )
            if con:
                data_types = con.data_types
            else:
                raise HTTPException(status_code=404, detail="Sensor type not found")
            sensor = om2m.create_cin(node.path, "Data", con=data_types).status_code
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating node",
        )


@router.get("/get-nodes")
@token_required
def get_nodes(
    node: NodeGetAll,
    request: Request,
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
    path = node.path
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
