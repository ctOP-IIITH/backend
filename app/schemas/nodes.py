from pydantic import BaseModel


class NodeCreate(BaseModel):
    """
    Pydantic model for creating a new node.
    """

    lbls: list = []
    sensor_type_id: int
    latitude: float
    longitude: float
    area: str


class NodeDelete(BaseModel):
    """
    Pydantic model for deleting a node.
    """

    node_name: str
    path: str
