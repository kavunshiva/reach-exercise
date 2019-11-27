# Overview

This app two RESTful endpoints, `POST /object` and `POST /alert`, as well as a WebSocket endpoint, `/inbox/{object_id}`.

### POST /object
Accepts a `JSON`-encoded `object` in the body containing values for `email` and `phone_number`, e.g.

```json
{
  "email": "bob@example.com",
  "phone_number": "212-555-1234"
}
```

It then validates these fields, and inserts it into an `objects` table in a `PostgreSQL` database with the following schema:

| id | email | phone_number |
| --- | --- | --- |
| `int` | `str` | `str` |

If it successfully persists, a `200` status is returned, along with a `JSON` representation of the persisted `object`.

### POST /alert
Accepts a `JSON`-encoded `object` in the body containing values for `text`, `object_ids` and `alert_all`, e.g.

```json
{
  "text": "alert, alert!",
  "object_ids": [1,3,4],
  "alert_all": false
}
```

These `alerts` are intended to be sent out to the `objects` in the `object_ids` param or to all `objects` in the database of the value of `alert_all` is `true`. The incoming `object_ids` are filtered against the IDs in the `objects` table at the time of the request, the `alerts` are stored in an `alerts` table, and rows are appended to the `object_alerts` join table as well (`objects` and `alerts` have a many-to-many relationship).

The `alerts` table has a schema which looks as follows:

| id | text | alert_all | number_of_objects_receiving_alert |
| --- | --- | --- | --- |
| `int` | `str` | `boolean` | `int` |

If all goes well, a `200` status is returned indicating the `alerts` have successfully been persisted, and the `alerts` are also added to queue to be consumed by a `WebSocket` and forwarded along to the appropriate connected clients.

### WebSocket /inbox/{object_id}
On connection to this endpoint, all of the `alerts` associated with the `object_id` (through the `object_alerts` join table) are pushed to the client. As additional alerts intended for the `object` with the `object_id`, they are also pushed to the client.

# Setup
A `Dockerfile` and `docker-compose.yml` were created but are admittedly a bit rough around the edges. This app pulls in environment variables from a `.env` in its `app` directory which you'll have to make; it should look like the following:

```
DB_USERNAME=<YOUR_DB_USERNAME>
DB_PASSWORD=<YOUR_DB_PASSWORD>
DB_SERVER=localhost
DB_NAME=<YOUR_DB_NAME>
```

Indeed, the only environment variables we've got at the moment are the ones surrounding the database. Spool up a `PostgreSQL` database and paste the appropriate values into this `.env` file.

Then, when you'd like to run this locally, navigate to the `app` directory and go ahead and run the following from the command line:

```bash
uvicorn main:app
```

That's basically it. Your server should be up and running. By default, it will show up at `http://localhost:8000`, but your mileage may vary. You can go ahead and make `POST` requests against the server, e.g.

```bash
BASE_URL='http://localhost:8000'

curl -X POST \
-H "content-type: application/json" \
-d '{ "email": "bob@example.com", "phone_number": "718-555-1234" }' \
"$BASE_URL/object"
```

and you should get responses back. You can also connect a client to the WebSocket and watch as the `alerts` pour in.

When hitting the `objects` endpoint, try sending up some objects with an invalid `email` or `phone_number` and see what happens. When hitting the alerts endpoint, try passing up some `object_ids` that don't exist in the `database` and note that only the valid ones are included in the tally in `number_of_objects_receiving_alert`. Try connecting to the database via `psql` and query the `objects`, `alerts`, and `object_alerts` tables to watch them evolve in real time.

Have fun.

# Tests
Run `./tests.py` from the `app` directory. (You may need to run `chmod +x tests.py` if your system whines about not having sufficient privileges.)

# TODO
- [x] store credentials
- [x] add endpoints
  + [x] POST: /object
    - [x] write to database + return JSON
  + [x] POST: /alert
    - [x] write to database + return JSON
    - [x] notify clients via WebSocket
  + [x] WebSocket: /inbox/{object_id}
  + [x] default error response
- [x] add tests
- [x] add docstrings
- [x] add docker config
- [x] break code out into files
- [x] validations
