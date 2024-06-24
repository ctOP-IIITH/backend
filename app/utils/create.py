"""
This module provides a class to create various entities like vertical, sensor type and node on OM2M as well as the database.
"""

from fastapi import Depends, Request, HTTPException, status
from sqlalchemy.orm import Session
import json

from app.schemas.import_conf import Vertical, SensorType, Area
from app.utils.om2m_lib import Om2m
from app.utils.utils import (
    get_vertical_name,
    gen_vertical_code,
    get_sensor_type_id,
    get_next_sensor_node_number,
    get_node_code,
    get_sensor_type_name
)
from app.models.sensor_types import SensorTypes as DBSensorType
from app.models.vertical import Vertical as DBAE
from app.config.settings import OM2M_URL, MOBIUS_XM2MRI
from app.models.vertical import Vertical as DBVertical
from app.models.node import Node as DBNode
from app.schemas.nodes import NodeCreate
from app.database import get_session

om2m = Om2m(MOBIUS_XM2MRI, OM2M_URL)


def create_vertical(vert_name, vert_short_name, vert_description, labels, db: Session):
    vert_short_name = "AE-" + vert_short_name
    # check if vertical already exists
    res = db.query(DBAE).filter(DBAE.res_name == vert_name).first()
    if res is not None:
        return 409
    status_code, data = om2m.create_ae(vert_short_name, labels=labels)
    if status_code == 409:
        data = om2m.get_containers(vert_short_name)
        data = data.text
    if status_code == 201 or status_code == 409:
        res_id = json.loads(data)["m2m:ae"]["ri"].split("/")[-1]

        # check if vertical already exists
        res = db.query(DBAE).filter(DBAE.res_name == vert_name).first()
        if res is not None:
            return 409

        db_vertical = DBAE(
            res_name=vert_name,
            res_short_name=vert_short_name,
            labels=labels,
            orid=res_id,
            description=vert_description,
        )
        db.add(db_vertical)
        db.commit()
        return 201
    else:
        return status_code


def insert_vertical(vertical: Vertical, db: Session):
    """
    Create a vertical in the database.
    Check if the vertical already exists in the database. If it does, return it."""

    res = db.query(DBVertical).filter(DBVertical.res_name == vertical.name).first()

    if res is not None:
        return res

    orid = gen_vertical_code(vertical.name)

    try:
        _, mesg = om2m.create_ae(orid, path="", labels=vertical.labels)
        print(mesg)

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating vertical in OM2M",
        ) from e

    try:
        res_id = json.loads(mesg)["m2m:ae"]["ri"].split("/")[-1]
        print(res_id)
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating vertical in OM2M",
        ) from e

    db_vertical = DBVertical(
        res_name=vertical.name, labels=vertical.labels, orid=res_id
    )

    db.add(db_vertical)
    db.commit()
    db.refresh(db_vertical)

    return db_vertical


def insert_sensor_type(sensor_type: SensorType, db: Session, vert_id: int):
    """
    Create a sensor type in the database.
    Check if the sensor type already exists in the database. If it does, return it."""

    res = (
        db.query(DBSensorType)
        .filter(
            DBSensorType.res_name == sensor_type.name
            and DBSensorType.vertical_id == vert_id
        )
        .first()
    )

    if res is not None:
        return res

    params = list(sensor_type.parameters.keys())
    datatypes = list(sensor_type.parameters.values())
    db_sensor_type = DBSensorType(
        res_name=sensor_type.name,
        parameters=params,
        data_types=datatypes,
        labels=sensor_type.labels,
        vertical_id=vert_id,
    )
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
                vert_name,
                sensor_type_id,
                sensor.coordinates.latitude,
                sensor.coordinates.longitude,
                db,
            )
            print(res_id)

            vert_orid = gen_vertical_code(vert_name)

            try:
                _, mesg = om2m.create_container(res_id, vert_orid, labels=sensor.labels)
                print(mesg)

            except Exception as e:
                print(e)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error creating vertical in OM2M",
                ) from e

            try:
                res_id = json.loads(mesg)["m2m:cnt"]["ri"].split("/")[-1]
                print(res_id)
            except Exception as e:
                print(e)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error creating vertical in OM2M",
                ) from e

            db_node = DBNode(
                sensor_type_id=sensor_type_id,
                labels=sensor.labels,
                lat=sensor.coordinates.latitude,
                long=sensor.coordinates.longitude,
                location=loc.name,
                area=area.area,
                sensor_node_number=get_next_sensor_node_number(sensor_type_id, db),
                orid=res_id,
            )

            db.add(db_node)
            db.commit()
            print()
    return True


def create_node(
    node: NodeCreate,
    request: Request,
    session: Session = Depends(get_session),
    current_user=None,
    node_data=None,
):
    if node_data:
        node = NodeCreate(
            sensor_type_id=node_data['sensor_type_id'],
            latitude=node_data['latitude'],
            longitude=node_data['longitude'],
            area=node_data['area'],
            name=node_data['name']
        )
    _, _ = current_user, request

    try:
        con = (
            session.query(DBSensorType)
            .filter(DBSensorType.id == node.sensor_type_id)
            .first()
        )
        if con is None:
            return {"status": "error", "message": "Sensor type not found"}

        existing_node = session.query(DBNode).filter(DBNode.name == node.name).first()
        if existing_node:
            return {"status": "error", "message": f"Node: {node.name} already exists"}

        vert_name = get_vertical_name(node.sensor_type_id, session)
        if vert_name is None:
            print("vertical not found")
            return {"status": "error", "message": "Non Existing Domain, please check the sensor type"}

        print(vert_name, node.sensor_type_id, node.latitude, node.longitude)
        res_id = get_node_code(
            vert_name, node.sensor_type_id, node.latitude, node.longitude, session
        )

        response = om2m.create_container(res_id, f"{vert_name}", labels=[vert_name, res_id])
        print(response)
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
                name=node.name
            )
            print("*************************************************************************************\n")
            print(f"RESPONSE -> {response.json()['m2m:cnt']['ri'].split('/')[-1]}, NAME -> {res_id}, ORID -> {res_data.json()['m2m:cnt']['ri'].split('/')[-1]} ")
            print("*************************************************************************************\n")
            if res_data.status_code == 201 and res_desc.status_code == 201:
                session.add(new_node)
                session.commit()

                # Update token_num with the generated id
                new_node.token_num = new_node.id  # increases cnt of /cin
                session.commit()

                if con:
                    parameters = str(con.parameters)
                else:
                    return {"status": "error", "message": "Sensor type not found"}
                sensor = om2m.create_cin(
                    f"{vert_name}/{res_id}",
                    "Descriptor",
                    con=parameters,
                    lbl=[get_sensor_type_name(node.sensor_type_id, session)],
                ).status_code
                print(sensor)
                if sensor == 201:
                    if node_data:
                        return {"status": "success", "message": "Node created", "node": node_data}
                    else:
                        return {"status": "success", "message": "Node created"}
                else:
                    return {"status": "error", "message": "Error creating node"}
            else:
                return {"status": "error", "message": "Error creating node"}
        elif response.status_code == 409:
            return {"status": "error", "message": "Node already exists"}
        else:
            print(response.status_code)
            return {"status": "error", "message": "Error creating node"}

    except Exception as e:
        return {"status": "error", "message": str(e)}