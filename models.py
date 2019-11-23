from pydantic import BaseModel
from typing import List

class ObjectIn(BaseModel):
    email: str
    phone_number: str

class AlertIn(BaseModel):
    text: str
    object_ids: List[int] = []
    alert_all: bool
