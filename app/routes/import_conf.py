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
# from app.routes.nodes import create_node
from app.schemas.nodes import NodeCreate

from app.database import get_session
from app.config.settings import OM2M_URL
from app.auth.auth import (
    token_required,
    admin_required,
)
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
    create_hash,
)
from app.schemas.nodes import NodeCreate, NodeAssign
from app.models.vertical import Vertical as DBVertical
from app.models.node import Node as DBNode
from app.models.user import User as DBUser
from app.models.user_types import UserType
from app.models.node_owners import NodeOwners as DBNodeOwners
from app.models.sensor_types import SensorTypes as DBSensorType
from app.config.settings import OM2M_URL, OM2M_USERNAME, OM2M_PASSWORD, JWT_SECRET_KEY

router = APIRouter()

om2m = Om2m(OM2M_USERNAME, OM2M_PASSWORD, OM2M_URL)

# router = APIRouter()
# om2m = Om2m("admin", "admin", OM2M_URL)

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

    HEADER_CONTENTS = ["User-Agent", "accept", "X-M2M-Origin", "Authorization"]
    headers = {x: request.headers.get(f"{x}") for x in HEADER_CONTENTS}
    print(headers)

    created_nodes = []
    print(47, nodes)
    for node_data in nodes:
        node = NodeCreate(
            sensor_type_id=node_data['sensor_type_id'],
            latitude=node_data['latitude'],
            longitude=node_data['longitude'],
            area=node_data['area']
        )

        print("iterating on-> ", node)
        try:
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
                        created_nodes.append(node_data)
                    else:
                        raise HTTPException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Error creating node",
                        )
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

        except HTTPException as e:
            return {"error": str(e.detail)}

    return {"nodes": created_nodes}