"""
This module contains Pydantic models Sensor Types.
"""
from pydantic import BaseModel


class SensorTypeCreate(BaseModel):
    """
    Represents the schema for creating a new sensor type.

    Attributes:
        res_name (str): The name of the resource.
        parameters (list): The list of parameters.
        data_types (list): The list of data types.
        labels (list): The list of labels.
        vertical_id (int): The ID of the vertical.
    """

    res_name: str
    parameters: list
    data_types: list
    labels: list = []
    vertical_id: int


class SensorTypeGetAll(BaseModel):
    """
    Represents the schema for getting all sensor types.

    Attributes:
        vertical_id (int): The ID of the vertical.
    """

    vertical_id: int


class SensorTypeDelete(BaseModel):
    """
    Represents the schema for deleting a specific sensor type.

    Attributes:
        id (int): The ID of the sensor type.
        vertical_id (int): The ID of the vertical.
    """

    id: int
    vertical_id: int
