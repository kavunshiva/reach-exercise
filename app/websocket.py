import asyncio
from fastapi.encoders import jsonable_encoder

from starlette.responses import HTMLResponse
from starlette.websockets import WebSocket
from database import database, alerts
from models import Alert

from app import app

message_queue = {}

@app.websocket('/inbox/{object_id}')
async def websocket_endpoint(websocket: WebSocket, object_id: int):
    '''
    Opens a websocket connection, pushes all alerts associated with the
    client's object_id to the client, then periodically checks for any
    new alerts associated with the client's object_id and pushes those to
    the client as they crop up.
    '''
    await _open_connection(websocket, object_id)
    await _check_for_incoming_messages(websocket, object_id)

async def _open_connection(websocket: WebSocket, object_id: int):
    await websocket.accept()
    alerts = await _alerts_belonging_to_object(object_id)
    return await websocket.send_json(jsonable_encoder(alerts))

async def _alerts_belonging_to_object(object_id: int):
    query = f'''
        SELECT * FROM alerts WHERE id IN (
            SELECT alert_id FROM object_alerts WHERE object_id = :object_id
        )
    '''
    return await database.fetch_all(
        query=query,
        values={'object_id': object_id}
    )

async def _check_for_incoming_messages(websocket: WebSocket, object_id: int):
    global message_queue
    while True:
        await asyncio.sleep(1)
        while message_queue[object_id] and len(message_queue[object_id]) > 0:
            await websocket.send_json(
                jsonable_encoder(message_queue[object_id].pop())
            )
