from app.auth.auth import (
    token_required,
    admin_required,
)
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_session
from app.models.sensor_types import SensorTypes as DBSensorType
from app.schemas.sensor_types import (
    SensorTypeCreate,
    SensorTypeGetAll,
    SensorTypeDelete,
    SensorTypeGet,
)

router = APIRouter()


@router.post("/create")
@token_required
@admin_required
def create_sensor_type(
    sensor_type: SensorTypeCreate,
    request: Request,
    session: Session = Depends(get_session),
    current_user=None,
):
    _, _ = current_user, request
    try:
        sensor_type_name = sensor_type.res_name
        new_sensor_type = DBSensorType(
            res_name=sensor_type_name,
            parameters=sensor_type.parameters,
            data_types=sensor_type.data_types,
            labels=sensor_type.labels,
            vertical_id=sensor_type.vertical_id,
        )
        print(new_sensor_type)
        session.add(new_sensor_type)
        session.commit()
        return {"detail": "Sensor type created"}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating sensor type",
        ) from e


@router.get("/get-all")
@token_required
@admin_required
def get_sensor_types(
    sensor_type: SensorTypeGetAll,
    request: Request,
    session: Session = Depends(get_session),
    current_user=None,
):
    try:
        sensor_types = (
            session.query(DBSensorType)
            .filter(DBSensorType.vertical_id == sensor_type.vertical_id)
            .all()
        )
        if sensor_types is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Sensor types not found"
            )
        elif len(sensor_types) == 0:
            return {"detail": "No sensor types found"}
        else:
            return sensor_types
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting sensor types",
        )


@router.get("/get")
@token_required
def get_sensor_type(
    sensor_type: SensorTypeGet,
    request: Request,
    session: Session = Depends(get_session),
    current_user=None,
):
    try:
        sensor_type = (
            session.query(DBSensorType)
            .filter(DBSensorType.id == sensor_type.id)
            .first()
        )
        print(sensor_type)
        if sensor_type is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Sensor type not found"
            )
        else:
            return sensor_type
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting sensor type {e}",
        )


@router.delete("/delete")
@token_required
@admin_required
def delete_sensor_type(
    sensor_type: SensorTypeDelete,
    request: Request,
    session: Session = Depends(get_session),
    current_user=None,
):
    try:
        sensor_type = (
            session.query(DBSensorType)
            .filter(DBSensorType.id == sensor_type.id)
            .first()
        )
        if sensor_type is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Sensor type not found"
            )
        else:
            session.delete(sensor_type)
            session.commit()
            raise HTTPException(status_code=200, detail="Sensor type deleted")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting sensor type {e}",
        )
