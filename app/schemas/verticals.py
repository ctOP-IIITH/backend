from pydantic import BaseModel


class VerticalCreate(BaseModel):
    ae_name: str
    ae_description: str
    path: str
    labels: list = []


class VerticalGetAll(BaseModel):
    path: str


class VerticalDelete(BaseModel):
    path: str
    ae_name: str
