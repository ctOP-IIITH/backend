"""
This module defines the user routes for importing the configuration files.
"""

import json
from fastapi import APIRouter, Depends, HTTPException, status, Request

from sqlalchemy.orm import Session


# from app.schemas.import_conf import SensorType
from app.schemas.import_conf import Vertical, SensorType, Area
from app.utils.om2m import Om2m
from app.utils.utils import get_vertical_name, gen_vertical_code, get_sensor_type_id, get_next_sensor_node_number, get_node_code
from app.models.vertical import Vertical as DBVertical
from app.models.sensor_types import SensorTypes as DBSensorTypes
from app.models.node import Node as DBNode
from app.database import get_session
from app.config.settings import OM2M_URL
from app.auth.auth import (
    token_required,
    admin_required,
)


router = APIRouter()

om2m = Om2m("admin", "admin", OM2M_URL)


def insert_vertical(vertical: Vertical, db: Session):
    """
    Create a vertical in the database.
    Check if the vertical already exists in the database. If it does, return it."""

    res = db.query(DBVertical).filter(
        DBVertical.res_name == vertical.name).first()

    if res is not None:
        return res

    orid = gen_vertical_code(vertical.name)

    try:
        _, mesg = om2m.create_ae(orid, labels=vertical.labels)

    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Error creating vertical in OM2M") from e

    try:
        res_id = json.loads(mesg)["m2m:ae"]["ri"] . split("/")[-1]
        print(res_id)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Error creating vertical in OM2M") from e

    db_vertical = DBVertical(res_name=vertical.name,
                             labels=vertical.labels, orid=res_id)

    db.add(db_vertical)
    db.commit()
    db.refresh(db_vertical)

    return db_vertical


def insert_sensor_type(sensor_type: SensorType, db: Session, vert_id: int):
    """
    Create a sensor type in the database.
    Check if the sensor type already exists in the database. If it does, return it."""

    res = db.query(DBSensorTypes).filter(
        DBSensorTypes.res_name == sensor_type.name and DBSensorTypes.vertical_id == vert_id).first()

    if res is not None:
        return res

    params = list(sensor_type.parameters.keys())
    datatypes = list(sensor_type.parameters.values())
    db_sensor_type = DBSensorTypes(
        res_name=sensor_type.name,
        parameters=params,
        data_types=datatypes,
        labels=sensor_type.labels,
        vertical_id=vert_id)
    db.add(db_sensor_type)
    db.commit()
    db.refresh(db_sensor_type)
    return db_sensor_type


def insert_all_node(area: Area, db: Session):
    """
    Create all the sensors of an area in the database.
    """

    for loc in area.locations:
        for sensor in loc.sensors:
            sensor_type_id = get_sensor_type_id(sensor.sensor_type, db)
            if sensor_type_id is None:
                print(f"sensor type {sensor.sensor_type} not found")
                return False  # TODO: Raise error

            vert_name = get_vertical_name(sensor_type_id, db)
            if vert_name is None:
                print("vertical not found")
                return False  # TODO: Raise error

            res_id = get_node_code(
                vert_name, sensor_type_id, sensor.coordinates.latitude, sensor.coordinates.longitude, db)
            print(res_id)

            vert_orid = gen_vertical_code(vert_name)

            try:
                _, mesg = om2m.create_container(
                    res_id, vert_orid, labels=sensor.labels)

            except Exception as e:
                print(e)
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                    detail="Error creating vertical in OM2M") from e

            try:
                res_id = json.loads(mesg)["m2m:cnt"]["ri"] . split("/")[-1]
                print(res_id)
            except Exception as e:
                print(e)
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                    detail="Error creating vertical in OM2M") from e

            db_node = DBNode(sensor_type_id=sensor_type_id,
                             labels=sensor.labels,
                             lat=sensor.coordinates.latitude,
                             long=sensor.coordinates.longitude,
                             location=loc.name,
                             landmark=loc.landmark,
                             area=area.area,
                             sensor_node_number=get_next_sensor_node_number(
                                 sensor_type_id, db),
                             orid=res_id
                             )

            db.add(db_node)
            db.commit()
            print()
    return True


@router.get("/import")
# @token_required       # TODO Uncomment later
# @admin_required
def import_conf(request: Request, db: Session = Depends(get_session)):
    """
    Import the configuration files.
    """

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

    db_vertical = insert_vertical(vertical, db)
    print("created vertical")

    for item in vertical.sensor_types:
        insert_sensor_type(item, db, db_vertical.id)

    print("created sensor types")

    insert_all_node(area, db)
    print("created all nodes")

    _ = request
    return True
