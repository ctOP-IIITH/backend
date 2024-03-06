"""
This module defines the Sensor types model.
"""

from sqlalchemy import Column, Integer, String, ARRAY, ForeignKey, UniqueConstraint
from app.database import Base
import json


class SensorTypes(Base):
    """
    This class defines the Sensor type model.
    """

    __tablename__ = "sensor_types"

    id = Column(Integer, primary_key=True)
    res_name = Column(String(50), nullable=False)
    if Base.metadata.bind and "postgresql" in str(Base.metadata.bind.url):
        parameters = Column(ARRAY(String(50)), nullable=True)
        data_types = Column(ARRAY(String(50)), nullable=True)
        labels = Column(ARRAY(String(50)), nullable=True)
    else:
        parameters = Column(String(50), nullable=True)
        data_types = Column(String(50), nullable=True)
        labels = Column(String(50), nullable=True)
    vertical_id = Column(Integer, ForeignKey("verticals.id"))
    # combination of vertical_id and res_name should be unique
    __table_args__ = (
        UniqueConstraint("vertical_id", "res_name", name="unique_sensor_type"),
    )

    @property
    def parameters(self):
        if Base.metadata.bind and "postgresql" in str(Base.metadata.bind.url):
            return self._parameters
        else:
            return json.loads(self._parameters)

    @parameters.setter
    def parameters(self, value):
        if Base.metadata.bind and "postgresql" in str(Base.metadata.bind.url):
            self._parameters = value
        else:
            self._parameters = json.dumps(value)

    @property
    def data_types(self):
        if Base.metadata.bind and "postgresql" in str(Base.metadata.bind.url):
            return self._data_types
        else:
            return json.loads(self._data_types)

    @data_types.setter
    def data_types(self, value):
        if Base.metadata.bind and "postgresql" in str(Base.metadata.bind.url):
            self._data_types = value
        else:
            self._data_types = json.dumps(value)

    @property
    def labels(self):
        if Base.metadata.bind and "postgresql" in str(Base.metadata.bind.url):
            return self._labels
        else:
            return json.loads(self._labels)

    @labels.setter
    def labels(self, value):
        if Base.metadata.bind and "postgresql" in str(Base.metadata.bind.url):
            self._labels = value
        else:
            self._labels = json.dumps(value)

    def __repr__(self):
        return f"<Sensor Type (id = {self.id}, res_name = {self.res_name}>, parameters={self.parameters},data_types = {self.data_types}, labels= {self.labels}, vertical_id= {self.vertical_id} )"
