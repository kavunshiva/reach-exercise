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
    sqlalchemy.Column('object_ids', sqlalchemy.ARRAY(sqlalchemy.Integer)),
    sqlalchemy.Column('alert_all', sqlalchemy.Boolean),
)

engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)

@app.on_event('startup')
async def startup():
    await database.connect()

@app.on_event('shutdown')
async def shutdown():
    await database.disconnect()
