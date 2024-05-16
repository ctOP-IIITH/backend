"""
This module defines the user routes for importing the configuration files.
"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.utils.om2m_lib import Om2m
from app.models.sensor_types import SensorTypes as DBSensorType
from app.config.settings import OM2M_URL, OM2M_USERNAME, OM2M_PASSWORD
from app.database import get_session
from app.config.settings import OM2M_URL

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
om2m = Om2m(OM2M_USERNAME, OM2M_PASSWORD, OM2M_URL)

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

    sensor_types = session.query(DBSensorType).all()  # get all the sensors
    sensor_name_to_id = {sensor_type.res_name: sensor_type.id for sensor_type in sensor_types}

    created_nodes, failed_nodes, invalid_sensor_nodes = [], [], []

    for node in nodes:
        sensor_name = node['sensor_name']
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
        result = create_node(node_data, request, session, current_user, node_data=node, bulk_import=True)
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