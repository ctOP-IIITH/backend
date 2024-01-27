"""
This module defines various utility functions used elsewhere.
"""

from geopy.geocoders import Nominatim
from sqlalchemy.orm import Session

from app.models.vertical import Vertical as DBVertical
from app.models.sensor_types import SensorTypes as DBSensorTypes
from app.models.node import Node as DBNode


def get_vertical_name(sensor_type: int, db: Session):
    """Returns the vertical name from sensor type"""

    res = db.query(DBVertical).join(DBSensorTypes, DBSensorTypes.vertical_id ==
                                    DBVertical.id).filter(DBSensorTypes.id == sensor_type).first()
    if res is None:
        return None
    return res.res_name


def gen_vertical_code(vertical_name: str):
    """Returns the vertical code from vertical name"""

    words = [char for char in vertical_name if char.isalpha()
             and char.isupper()]

    if len(words) < 2:
        words.append('X')  # Add a dummy letter

    result_word = ''.join(words[:2]).upper()
    return result_word


def get_sensor_type_id(sensor_type_name: str, db: Session):
    """Get sensor type id from sensor type name"""

    res = db.query(DBSensorTypes).filter(
        DBSensorTypes.res_name == sensor_type_name).first()
    if res is None:
        return None
    return res.id


def get_next_sensor_node_number(sensor_type: int, db: Session) -> int:
    """Get the number of the next sensor of the given sensor type"""

    res = db.query(DBNode).filter(DBNode.sensor_type_id == sensor_type).order_by(
        DBNode.sensor_node_number.desc()).first()
    if res is None:
        return 1
    return res.sensor_node_number + 1


def get_pincode(latitude, longitude):
    """Get the pincode from latitude and longitude"""

    geolocator = Nominatim(user_agent="pincode_finder")
    location = geolocator.reverse((latitude, longitude), language='en')
    address = location.raw.get('address', {})
    pincode = address.get('postcode')

    return pincode


def get_node_code(vert: str, sensor_type: int, lat: int, long: int, db: Session):
    """Returns the node code from node ID"""

    vert = db.query(DBVertical).join(
        DBSensorTypes, DBSensorTypes.vertical_id == DBVertical.id).filter(DBSensorTypes.id == sensor_type) .first()

    if not vert:
        raise Exception("Vertical not found")

    vert_code = gen_vertical_code(vert.res_name)

    # NOTE: Takes a lot of time to complete
    pin_code = get_pincode(lat, long)
    pin_code = str(pin_code)[-4:] if pin_code else "0000"

    sensor_node_number = get_next_sensor_node_number(sensor_type, db),

    code = f"{vert_code}{sensor_type:02d}-{pin_code:04}-{sensor_node_number[0]:04d}"

    return code
