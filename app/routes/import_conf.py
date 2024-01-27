"""
This module defines the user routes for importing the configuration files.
"""

import json
from fastapi import APIRouter, Depends, Request

from sqlalchemy.orm import Session

from app.utils.om2m_lib import Om2m
from app.utils.create import (
    insert_vertical,
    insert_sensor_type,
    insert_all_node,
)

from app.schemas.import_conf import Vertical, Area

from app.database import get_session
from app.config.settings import OM2M_URL
from app.auth.auth import (
    token_required,
    admin_required,
)


router = APIRouter()
om2m = Om2m("admin", "admin", OM2M_URL)


@router.get("/import")
@token_required
@admin_required
def import_conf(
    request: Request, session: Session = Depends(get_session), current_user=None
):
    """
    Import the configuration files.
    """

    _ = current_user

    try:
        vertical_text = open("vertical.json", "r", encoding="utf-8").read()
        vertical = Vertical(**(json.loads(vertical_text)))
    except Exception as e:
        print(e)
        return e

    sensor_types = []
    for item in vertical.sensor_types:
        sensor_types.append(item.name)

    print(sensor_types)

    try:
        node_text = open("area.json", "r", encoding="utf-8").read()
        area = Area(**(json.loads(node_text)))
    except Exception as e:
        print(e)
        return e

    error = False
    for loc in area.locations:
        for sensor in loc.sensors:
            if sensor.sensor_type not in sensor_types:
                error_msg = f"sensor type {sensor.sensor_type} not found"
                print(error_msg)
                error = True
                break
            continue
        if error:
            break
    if error:
        return error_msg

    db_vertical = insert_vertical(vertical, session)
    print("created vertical")

    for item in vertical.sensor_types:
        insert_sensor_type(item, session, db_vertical.id)

    print("created sensor types")

    insert_all_node(area, session)
    print("created all nodes")

    _ = request
    return True
