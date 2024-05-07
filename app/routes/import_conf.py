"""
This module defines the user routes for importing the configuration files.
"""

import json
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session

from app.utils.om2m_lib import Om2m
from app.utils.create import (
    insert_vertical,
    insert_sensor_type,
    insert_all_node,
)

from app.schemas.import_conf import Vertical, Area
from app.models.sensor_types import SensorTypes as DBSensorType
from app.routes.nodes import create_node
from app.schemas.nodes import NodeCreate

from app.database import get_session
from app.config.settings import OM2M_URL
from app.auth.auth import (
    token_required,
    admin_required,
)


router = APIRouter()
om2m = Om2m("admin", "admin", OM2M_URL)


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

    return {"nodes" : nodes}