"""
This module defines the user routes for creating and mapping tokens.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request

from sqlalchemy.orm import Session

from app.models.sensor_types import SensorTypes as DBSensorTypes
from app.models.token import Token as DBToken
from app.models.node import Node as DBNode
from app.database import get_session
from app.auth.auth import (
    token_required,
)


router = APIRouter()


@router.get("/get-token")
@token_required
def get_token(request: Request, session: Session = Depends(get_session), current_user=None):
    """
    Get a new token number for the specific sensor type

    request URL: /get-token?sensor_type=Kristnam

    """

    sensor_type = request.query_params.get("sensor_type")

    if sensor_type is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Sensor type not specified")

    res = session.query(DBSensorTypes).filter(
        DBSensorTypes.res_name == sensor_type).first()

    if res is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Sensor type not found")

    token_num = session.query(DBToken.token_id).filter(
        DBToken.sensor_type == res.id).order_by(DBToken.token_id.desc()).first()
    token = token_num[0] + 1 if token_num else 1

    user_id = current_user.id

    db_token = DBToken(
        sensor_type=res.id,
        token_id=token,
        assigned_to=user_id
    )
    session.add(db_token)
    session.commit()
    session.refresh(db_token)

    return {"token": token}


@router.get("/deploy-token")
@token_required
def deploy_token(request: Request, session: Session = Depends(get_session), current_user=None):
    """
    Deploy a token to a node

    request URL: /deploy-token?sensor_type=Kristnam&token=1&lat=12.345&long=67.890

    """

    _ = current_user

    sensor_type = request.query_params.get("sensor_type")
    token = request.query_params.get("token")
    lat = request.query_params.get("lat")
    long = request.query_params.get("long")

    if sensor_type is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Sensor type not specified")
    if token is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Token not specified")
    if lat is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Latitude not specified")
    if long is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Longitude not specified")

    res = session.query(DBSensorTypes).filter(
        DBSensorTypes.res_name == sensor_type).first()
    if res is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Invalid sensor type")

    token_num = session.query(DBToken).filter(
        DBToken.sensor_type == res.id, DBToken.token_id == token).first()
    if token_num is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Invalid token")

    node = session.query(DBNode).filter(
        DBNode.sensor_type_id == res.id, DBNode.lat == lat, DBNode.long == long).first()
    if node is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No such node exists")

    if node.token_num is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Node is already mapped to a token")

    token_num.status = True
    node.token_num = token
    session.commit()
    session.refresh(token_num)
    session.refresh(node)

    return {"message": "Token deployed successfully"}
