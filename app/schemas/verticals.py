from pydantic import BaseModel, Field


class VerticalCreate(BaseModel):
    ae_name: str
    ae_description: str
    ae_short_name: str = Field(..., min_length=2, max_length=2)
    labels: list = []
