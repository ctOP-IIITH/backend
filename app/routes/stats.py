from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.models.node import Node as DBNode
from app.models.sensor_types import SensorTypes as DBSensorType
from app.models.vertical import Vertical as DBVertical
from app.database import get_session

router = APIRouter()


@router.get("/loners")
def get_major_stats(
    session: Session = Depends(get_session),
):
    """
    Get total Areas, Domains, Sensor Types and Nodes
    """
    try:
        total_domains = session.query(DBVertical).count()
        total_sensor_types = session.query(DBSensorType).count()
        total_nodes = session.query(DBNode).count()
        total_areas = session.query(DBNode.area).distinct(DBNode.area).count()

        return {
            "total_areas": total_areas,
            "total_domains": total_domains,
            "total_sensor_types": total_sensor_types,
            "total_nodes": total_nodes,
        }
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting stats",
        ) from e
