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

    for node in nodes:
        sensor_name = node['sensor_name']
        if sensor_name in sensor_name_to_id:
            node['sensor_type_id'] = sensor_name_to_id[sensor_name]
        else:
            return {"error": f"Sensor type '{sensor_name}' not found"}


    created_nodes = []
    for node_data in nodes:
        node = NodeCreate(
            sensor_type_id=node_data['sensor_type_id'],
            latitude=node_data['latitude'],
            longitude=node_data['longitude'],
            area=node_data['area'],
            name=node_data['name']
        )
        create_node(node, request, session, current_user,node_data=node_data, bulk_import=True, created_nodes=created_nodes)


    return {"nodes": created_nodes}