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

router = APIRouter()

om2m = Om2m("admin", "admin", "http://localhost:8080/~/in-cse/in-name")

# TODO : Add the Database functions


@router.post("/create-node")
@token_required
@admin_required
def create_node(
    node: NodeCreate, request: Request, session: Session = Depends(get_session)
):
    """
    Create an AE (Application Entity) with the given name and labels.

    Args:
        request (Request): The HTTP request object.

    Returns:
        int: The status code of the operation.
    """
    node_name = node.node_name
    response = om2m.create_container(node_name, node.path, labels=[node_name])
    return response.status_code


@router.get("/get-nodes")
@token_required
def get_nodes(
    node: NodeGetAll, request: Request, session: Session = Depends(get_session)
):
    """
    Retrieves the subcontainers for a given path.

    Parameters:
    - path (str): The path to retrieve the subcontainers from.

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
        return []
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving nodes. {e}",
        )


@router.delete("/delete-node")
@token_required
@admin_required
def delete_node(
    node: NodeDelete, request: Request, session: Session = Depends(get_session)
):
    """
    Deletes a node with the given name.

    Args:
        request (Request): The HTTP request object.

    Returns:
        int: The status code of the operation.
    """
    node_name = node.node_name
    path = node.path
    response = om2m.delete_resource(f"{path}/{node_name}")
    return response.status_code
