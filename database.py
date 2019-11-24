from typing import List
import databases
import sqlalchemy
from fastapi.encoders import jsonable_encoder

from app import app
from models import AlertIn, Alert
from settings import DATABASE_URL

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

objects = sqlalchemy.Table(
    'objects',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('email', sqlalchemy.String),
    sqlalchemy.Column('phone_number', sqlalchemy.String),
)

alerts = sqlalchemy.Table(
    'alerts',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('text', sqlalchemy.String),
    sqlalchemy.Column('alert_all', sqlalchemy.Boolean),
    sqlalchemy.Column('number_of_objects_receiving_alert', sqlalchemy.Integer),
)

object_alerts = sqlalchemy.Table(
    'object_alerts',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('object_id', sqlalchemy.Integer),
    sqlalchemy.Column('alert_id', sqlalchemy.Integer),
)

engine = sqlalchemy.create_engine(DATABASE_URL)

metadata.create_all(engine) # TODO: move this into a separate migration script

@app.on_event('startup')
async def startup():
    await database.connect()

@app.on_event('shutdown')
async def shutdown():
    await database.disconnect()

async def get_all_ids(resource: str):
    query = select_all_ids_from_resource_query(resource)
    ids = []
    for id in jsonable_encoder(await database.fetch_all(query)):
        ids.append(id['id'])
    return ids

def select_all_ids_from_resource_query(resource: str):
    # avoid SQL injection (:resource interpolation doesn't work w/ table names)
    return {
        'objects': 'SELECT id FROM objects',
        'alerts': 'SELECT id FROM alerts',
    }[resource]

async def get_object_ids(alert: AlertIn):
    if alert.alert_all:
        object_ids = await get_all_ids('objects')
        alert.object_ids = object_ids
        return object_ids
    else:
        # return all object IDs on the alert existing in the objects table
        return await persisted_object_ids(alert.object_ids)

async def persisted_object_ids(ids: List[int]):
    all_db_ids = {}
    for id in (await get_all_ids('objects')):
        all_db_ids[id] = True
    persisted_ids = []
    for id in ids:
        if id in all_db_ids: persisted_ids.append(id)
    return persisted_ids

async def insert_alert(alert: AlertIn, object_count: int):
    query = alerts.insert().values(
        text=alert.text,
        alert_all=alert.alert_all,
        number_of_objects_receiving_alert=object_count,
    )
    return {
        **alert_params(alert),
        'number_of_objects_receiving_alert': object_count,
        'id': await database.execute(query),
    }

def alert_params(alert: AlertIn):
    params = {}
    alert_class_keys = Alert.__dict__['__fields__'].keys()
    for k, v in alert.dict().items():
        if k in alert_class_keys: params[k] = v
    return params

async def update_join_table(alert_id: int, object_ids: List[int]):
    join_table_query = [
        object_alerts.insert(),
        await object_alert_params(alert_id, object_ids),
    ]
    return await database.execute_many(*join_table_query)

async def object_alert_params(alert_id: int, object_ids: List[int]):
    params = []
    for object_id in object_ids:
        params.append({'object_id': object_id, 'alert_id': alert_id})
    return params
