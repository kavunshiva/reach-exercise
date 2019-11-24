from typing import List

from app import app
from fastapi import HTTPException
from database import *
from models import ObjectIn, AlertIn
from websocket import message_queue

@app.post('/object', response_model=ObjectIn)
async def create_object(object: ObjectIn):
    '''
    Create an object in the database from a POST request and return a
    representation of that object as a dict.

    Keyword arguments:
    object -- an instance of ObjectIn as converted from the body of an
    HTTP POST request by the app decorator
    '''
    query = objects.insert().values(
        email=object.email,
        phone_number=object.phone_number,
    )
    id = await database.execute(query)
    await _trigger_any_error_messages(id, 'objects')
    return {**object.dict(), 'id': id}

@app.post('/alert', response_model=Alert)
async def create_alert(alert: AlertIn):
    '''
    Create an alert in the database from a POST request,
    associate that alert with its appropriate persisted objects,
    and return a representation of that alert as a dict.

    Keyword arguments:
    alert -- an instance of AlertIn as converted from the body of an
    HTTP POST request by the app decorator
    '''
    object_ids = await get_object_ids(alert)
    new_alert_params = await insert_alert(alert, len(object_ids))
    new_alert_id = new_alert_params['id']
    await _trigger_any_error_messages(new_alert_id, 'alerts')
    await update_join_table(new_alert_id, object_ids)
    _add_alert_to_websocket_queue(new_alert_params, object_ids)
    return new_alert_params

async def _trigger_any_error_messages(id: int, resource: str):
    if id not in (await get_all_ids(resource)):
        raise HTTPException(
            status_code=404,
            detail=f'No {resource.title()} with ID {id} found.',
        )
    return None

def _add_alert_to_websocket_queue(params: dict, object_ids: List[int]):
    global message_queue
    for object_id in object_ids:
        if not object_id in message_queue.keys():
            message_queue[object_id] = [params]
        else:
            message_queue[object_id].append(params)
