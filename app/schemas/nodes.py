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
    name: str  # used for mapping id to a name, user is expected to give this, created during bulk import


class NodeAssign(BaseModel):
    """
    Pydantic model for assigning a node to a user.
    """

    node_id: str
    vendor_email: str
