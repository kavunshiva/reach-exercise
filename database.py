import databases
import sqlalchemy

from app import app
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
metadata.create_all(engine)

@app.on_event('startup')
async def startup():
    await database.connect()

@app.on_event('shutdown')
async def shutdown():
    await database.disconnect()
