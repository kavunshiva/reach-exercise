from app import app
from database import database, objects, alerts
from models import ObjectIn, AlertIn

@app.post('/object', response_model=ObjectIn)
async def create_object(object: ObjectIn):
    query = objects.insert().values(
        email=object.email,
        phone_number=object.phone_number,
    )
    last_record_id = await database.execute(query)
    return {**object.dict(), 'id': last_record_id}

@app.post('/alert', response_model=AlertIn)
async def create_alert(alert: AlertIn):
    query = alerts.insert().values(
        text=alert.text,
        object_ids=alert.object_ids,
        alert_all=alert.alert_all,
    )
    last_record_id = await database.execute(query)
    return {**alert.dict(), 'id': last_record_id}
