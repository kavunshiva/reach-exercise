#!/usr/bin/env python3
# TODO: get test DB setup to allow for testing of valid requests

import json
from starlette.testclient import TestClient
from database import *
from crud import app

client = TestClient(app)

def test_create_object():
    # _create_object_succeeds_when_params_passed_up()
    _create_object_errors_if_no_params_passed_up()

def test_create_alert():
    _create_alert_errors_if_no_params_passed_up()

# def _create_object_succeeds_when_params_passed_up():
#     response = client.post(
#         '/object',
#         json={ 'email': 'bob@example.com', 'phone_number': '718-555-1234' },
#     )
#     breakpoint()
#     assert response.status_code == 200
#     assert json.loads(response.text)['detail'][0]['msg'] == 'field required'

def _create_object_errors_if_no_params_passed_up():
    response = client.post('/object')
    assert response.status_code == 422
    assert json.loads(response.text)['detail'][0]['msg'] == 'field required'

def _create_alert_errors_if_no_params_passed_up():
    response = client.post('/alert')
    assert response.status_code == 422
    assert json.loads(response.text)['detail'][0]['msg'] == 'field required'

# def test_websocket():
#     with client.websocket_connect('/index/{object_id}') as websocket:
#         data = websocket.receive_json()
#         assert data == {"msg": "Hello WebSocket"}

if __name__ == '__main__':
    test_create_object()
    test_create_alert()
    print('tests passed!')
