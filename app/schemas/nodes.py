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


class NodeAssign(BaseModel):
    """
    Pydantic model for assigning a node to a user.
    """

    node_id: str
    vendor_email: str
