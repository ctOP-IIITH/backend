from pydantic import BaseModel


class NodeCreate(BaseModel):
    """
    Pydantic model for creating a new node.
    """

    node_name: str
    lbls: list = []
    path: str
    sensor_type_id: int
    sensor_node_number: int
    lat: float
    long: float
    location: str
    landmark: str
    area: str


class NodeGetAll(BaseModel):
    """
    Pydantic model for getting all nodes.
    """

    path: str


class NodeDelete(BaseModel):
    """
    Pydantic model for deleting a node.
    """

    node_name: str
    path: str
