from app.auth.auth import (
    token_required,
    admin_required,
)
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_session
import requests
from app.utils.om2m import Om2m
from app.schemas.verticals import VerticalCreate, VerticalGetAll, VerticalDelete
import xml.etree.ElementTree as ET


router = APIRouter()

om2m = Om2m("admin", "admin", "http://localhost:8080/~/in-cse/in-name")


@router.post("/create-ae")
@token_required
@admin_required
async def create_ae(vertical: VerticalCreate, request: Request, current_user=None):
    """
    Create an AE (Application Entity) with the given name and labels.

    Args:
        request (Request): The HTTP request object.

    Returns:
        int: The status code of the operation.
    """
    ae_name = vertical.ae_name
    status_code, data = om2m.create_ae(ae_name, labels=[ae_name])
    return status_code


@router.get("/get-aes")
@token_required
async def get_aes(vertical: VerticalGetAll, request: Request, current_user=None):
    """
    Retrieves the subcontainers for a given path.

    Parameters:
    - path (str): The path to retrieve the subcontainers from.

    Returns:
    - list: A list of dictionaries containing the "rn" and "ri" attributes of each subcontainer.
    """
    path = vertical.path
    parent = "m2m:ae"
    is_direct_child = (
        lambda element, root: element in root and len(element.findall("..")) == 0
    )

    try:
        root = ET.fromstring(om2m.get_all_containers(path).text)
        m2m_ae_elements = root.findall(
            f".//{parent}", {"m2m": "http://www.onem2m.org/xml/protocols"}
        )
        first_level_ae_elements = []
        for ae_element in m2m_ae_elements:
            # print(ae_element)
            if is_direct_child(ae_element, root):
                first_level_ae_elements.append(ae_element)
        # print(first_level_ae_elements)
        aes = [
            {"rn": ae_element.get("rn"), "ri": ae_element.find("ri").text}
            for ae_element in first_level_ae_elements
        ]
        return aes
    except ET.ParseError:
        return []
    except Exception as e:
        # print(f"An error occurred: {e}")
        return []


@router.delete("/delete-ae/{ae_name}")
@token_required
@admin_required
async def delete_ae(vertical: VerticalDelete, request: Request, current_user=None):
    """
    This function deletes an AE resource in OM2M.

    Args:
        ae_name (str): The name of the AE resource.

    Returns:
        int: The status code of the request.
    """
    status_code = om2m.delete_resource(f"{vertical.ae_name}")
    return status_code
