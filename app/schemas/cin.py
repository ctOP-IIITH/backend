from pydantic import BaseModel


class ContentInstance(BaseModel):
    """
    Represents a content instance.

    Attributes:
        Can be any based on the sensor type.
    """

    class Config:
        extra = "allow"


class ContentInstanceGetAll(BaseModel):
    """
    Represents a request to get all content instances.

    Attributes:
        path (str): The path to the content instances.
    """

    path: str


class ContentInstanceDelete(BaseModel):
    """
    Represents a request to delete a content instance.

    Attributes:
        path (str): The path of the content instance.
        cin_id (str): The ID of the content instance.
        node_id (str): The ID of the node associated with the content instance.
    """

    path: str
    cin_id: str
    node_id: str
