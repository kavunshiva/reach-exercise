from typing import List

from pydantic import BaseModel

class ObjectIn(BaseModel):
    email: str
    phone_number: str

class AlertIn(BaseModel):
    text: str
    object_ids: List[int] = []
    alert_all: bool = False

class Alert(BaseModel):
    id: int
    text: str
    alert_all: bool
    number_of_objects_receiving_alert: int
