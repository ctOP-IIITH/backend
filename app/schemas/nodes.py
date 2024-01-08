from pydantic import BaseModel


class NodeCreate(BaseModel):
    """
    Pydantic model for creating a new node.
    """

    node_name: str
    labels: list
    path: str


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
