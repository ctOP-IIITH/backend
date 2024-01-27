"""
This module contains Pydantic models for configuration files import.
"""

from typing import Dict
from pydantic import BaseModel


# vertical.cfg

class SensorType(BaseModel):
    """
    Pydantic model for sensor type.
    """

    name: str
    parameters: Dict[str, str] = {}
    labels: list[str] = []


class Vertical(BaseModel):
    """
    Pydantic model for vertical.
    """

    name: str
    labels: list[str] = []
    sensor_types: list[SensorType] = []


# node.cfg


class Coordinates(BaseModel):
    """
    Pydantic model for coordinates.
    """

    latitude: float
    longitude: float


class Node(BaseModel):
    """
    Pydantic model for node.
    """

    coordinates: Coordinates
    sensor_type: str
    labels: list[str] = []


class Location(BaseModel):
    """
    Pydantic model for location.
    """

    name: str
    sensors: list[Node]


class Area(BaseModel):
    """
    Pydantic model for area.
    """

    area: str
    locations: list[Location]
