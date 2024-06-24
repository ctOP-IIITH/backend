"""
This module defines the user routes for importing the configuration files.
"""
from fastapi import APIRouter, Depends, Request, File, UploadFile
from sqlalchemy.orm import Session
from app.utils.om2m_lib import Om2m
from app.utils.create import (
    insert_vertical,
    insert_sensor_type,
    insert_all_node,
)

from app.schemas.import_conf import Vertical, Area

from app.models.sensor_types import SensorTypes as DBSensorType
from app.database import get_session
from app.config.settings import OM2M_URL, MOBIUS_XM2MRI
import csv
from io import StringIO

from app.auth.auth import (
    token_required,
    admin_required,
)

from app.auth.auth import (
    token_required,
    admin_required,
)
from app.database import get_session
from app.utils.om2m_lib import Om2m
from app.utils.create import create_node
from app.schemas.nodes import NodeCreate

router = APIRouter()
om2m = Om2m(MOBIUS_XM2MRI, OM2M_URL)

@router.post("/import")
@token_required
@admin_required
def import_conf(
    request: Request, payload: dict, session: Session = Depends(get_session), current_user=None
):
    """
    Import the configuration files.
    """

    _ = current_user
    try:
        nodes = payload["nodes"]
    except KeyError:
        return {"error": "Missing 'nodes' key in the JSON payload"}

    if len(nodes) > 5000: return {"error": "Import less than 5000 nodes at one time!"}
    sensor_types = session.query(DBSensorType).all()  # get all the sensors
    # sensor type field from bulk import, convert this to id since thats what create node expects
    sensor_name_to_id = {sensor_type.res_name: sensor_type.id for sensor_type in sensor_types}

    created_nodes, failed_nodes, invalid_sensor_nodes = [], [], []

    for node in nodes:
        sensor_name = node['sensor_type']
        if sensor_name in sensor_name_to_id:
            node['sensor_type_id'] = sensor_name_to_id[sensor_name]
        else:
            print(f"{node['name']} --> {sensor_name} not found")
            invalid_sensor_nodes.append({"node": node, "error": f"Sensor type '{sensor_name}' not found"})
            continue  

        node_data = NodeCreate(
            sensor_type_id=node['sensor_type_id'],
            latitude=node['latitude'],
            longitude=node['longitude'],
            area=node['area'],
            name=node['name']
        )
        result = create_node(node_data, request, session, current_user, node_data=node)
        print(f"{node['name']} --> {result['message']}")

        if result["status"] == "success":
            created_nodes.append(result["node"])
        else:
            failed_nodes.append({"node": node, "error": result["message"]})

    return {
        "created_nodes": created_nodes,
        "failed_nodes": failed_nodes,
        "invalid_sensor_nodes": invalid_sensor_nodes
    }

@router.post("/import_csv")
@token_required
@admin_required
def import_csv(
    request: Request, file: UploadFile = File(...), session: Session = Depends(get_session), current_user=None
):
    """
    Import nodes from a CSV file.
    """
    _ = current_user
    try:
        csv_data = file.file.read().decode('utf-8')
    except Exception as e:
        return {"error": f"Error reading CSV file: {str(e)}"}

    reader = csv.DictReader(StringIO(csv_data), fieldnames=['latitude', 'longitude', 'area', 'sensor_type', 'domain', 'name'])
    nodes = list(reader)
    if len(nodes) > 5000: return {"error": "Import less than 5000 nodes at one time!"}
    
    sensor_types = session.query(DBSensorType).all()
    sensor_name_to_id = {sensor_type.res_name: sensor_type.id for sensor_type in sensor_types}

    created_nodes, failed_nodes, invalid_sensor_nodes = [], [], []

    for node in nodes:
        sensor_name = node['sensor_type']
        if sensor_name in sensor_name_to_id:
            node['sensor_type_id'] = sensor_name_to_id[sensor_name]
        else:
            invalid_sensor_nodes.append({"node": node, "error": f"Sensor type '{sensor_name}' not found"})
            continue

        node_data = NodeCreate(
            sensor_type_id=node['sensor_type_id'],
            latitude=float(node['latitude']),
            longitude=float(node['longitude']),
            area=node['area'],
            name=node['name']
        )
        result = create_node(node_data, request, session, current_user, node_data=node)

        if result["status"] == "success":
            created_nodes.append(result["node"])
        else:
            failed_nodes.append({"node": node, "error": result["message"]})

    return {
        "created_nodes": created_nodes,
        "failed_nodes": failed_nodes,
        "invalid_sensor_nodes": invalid_sensor_nodes
    }