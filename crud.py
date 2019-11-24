from typing import List
from fastapi.encoders import jsonable_encoder

from app import app
from database import database, objects, alerts, object_alerts
from models import ObjectIn, AlertIn, Alert
from websocket import message_queue

@app.post('/object', response_model=ObjectIn)
async def create_object(object: ObjectIn):
    query = objects.insert().values(
        email=object.email,
        phone_number=object.phone_number,
    )
    id = await database.execute(query)
    return {**object.dict(), 'id': id}

@app.post('/alert', response_model=Alert)
async def create_alert(alert: AlertIn):
    object_ids = await _get_object_ids(alert)
    new_alert_params = await _insert_alert(alert, len(object_ids))
    await _update_join_table(new_alert_params['id'], object_ids)
    _add_alert_to_websocket_queue(new_alert_params, object_ids)
    return new_alert_params

async def _get_object_ids(alert: AlertIn):
    if alert.alert_all:
        object_ids = []
        for id in jsonable_encoder(
            await database.fetch_all('SELECT id FROM objects')
        ):
            object_ids.append(id['id'])
        alert.object_ids = object_ids
        return object_ids
    else:
        return alert.object_ids

async def _insert_alert(alert: AlertIn, object_count: int):
    query = alerts.insert().values(
        text=alert.text,
        alert_all=alert.alert_all,
        number_of_objects_receiving_alert=object_count,
    )
    return {
        **_alert_params(alert),
        'number_of_objects_receiving_alert': object_count,
        'id': await database.execute(query),
    }

def _alert_params(alert: AlertIn):
    alert_params = {}
    alert_class_keys = Alert.__dict__['__fields__'].keys()
    for k, v in alert.dict().items():
        if k in alert_class_keys: alert_params[k] = v
    return alert_params

async def _update_join_table(alert_id: int, object_ids: List[int]):
    join_table_query = [
        object_alerts.insert(),
        await _object_alert_params(alert_id, object_ids),
    ]
    return await database.execute_many(*join_table_query)

async def _object_alert_params(alert_id: int, object_ids: List[int]):
    params = []
    for object_id in object_ids:
        params.append({'object_id': object_id, 'alert_id': alert_id})
    return params

def _add_alert_to_websocket_queue(alert_params: dict, object_ids: List[int]):
    global message_queue
    for object_id in object_ids:
        if not object_id in message_queue.keys():
            message_queue[object_id] = [alert_params]
        else:
            message_queue[object_id].append(alert_params)
