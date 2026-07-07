# VoxPilot

Voice-controlled action pilot API, built with **FastAPI** and layered as
`router → controller → service`. Send a voice command as text and the API
triggers the matching action and logs it.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) — installs Python, manages the virtual
  environment and dependencies.

## Setup

Install dependencies (uv creates the `.venv/` automatically):

```bash
uv sync
```

## Run

Start the development server with live reload:

```bash
uv run uvicorn app.main:app --reload
```

Once running:

- API base URL: <http://127.0.0.1:8000>
- Interactive docs (Swagger UI): <http://127.0.0.1:8000/docs>

Keep this terminal open — application logs stream here in real time (see
[Logging](#logging)).

## Endpoints

| Method | Path      | Description                              |
| ------ | --------- | ---------------------------------------- |
| GET    | `/health` | Service health check                     |
| POST   | `/speak`  | Receive a voice command and run its action |

### Try it

With the server running, open a second terminal and send a command:

```bash
curl -X POST http://127.0.0.1:8000/speak \
  -H "Content-Type: application/json" \
  -d "{\"command\": \"camina hacia adelante\"}"
```

Response:

```json
{ "recognized": true, "action": "caminó hacia adelante" }
```

In the server terminal you will see the action logged:

```
2026-07-07 20:15:19 [info] caminó hacia adelante  correlation_id=b162782a... recibido='camina hacia adelante'
```

Unknown commands return `{"recognized": false, "action": null}` and log
`comando no reconocido`. Recognized commands live in the `COMMANDS` map in
`app/services/speech_service.py` — add a line there to support a new one.

## Logging

Structured logging via [structlog](https://www.structlog.org/). Every log line
includes:

- **date** — timestamp of the event
- **level** — log level (e.g. `info`)
- **correlation_id** — unique id per request, also returned in the
  `X-Request-ID` response header so a call can be traced end to end
- **recibido** — the raw command received

The correlation id is generated automatically per request by
[`asgi-correlation-id`](https://github.com/snok/asgi-correlation-id). You can
supply your own via the `X-Request-ID` header (must be a valid UUID, otherwise
a new one is generated).

## Project structure

```
app/
├── main.py                  # FastAPI app factory + middleware + router wiring
├── core/
│   ├── config.py            # Application settings
│   └── logging.py           # structlog configuration
├── routers/                 # HTTP route definitions
├── controllers/             # Request orchestration
├── services/                # Business logic
└── schemas/                 # Pydantic models
```

## Tests

```bash
uv run pytest
```
