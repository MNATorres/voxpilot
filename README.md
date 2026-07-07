# VoxPilot

Voice-controlled action pilot API, built with **FastAPI** and layered as
`router → controller → service`.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

## Setup

```bash
uv sync
```

This creates a virtual environment in `.venv/` and installs all dependencies.

## Run

```bash
uv run uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## Endpoints

| Method | Path      | Description          |
| ------ | --------- | -------------------- |
| GET    | `/health` | Service health check |

Interactive docs: `http://127.0.0.1:8000/docs`

## Project structure

```
app/
├── main.py              # FastAPI app entry point
├── core/
│   └── config.py        # Application settings
├── routers/             # HTTP route definitions
├── controllers/         # Request handling / orchestration
├── services/            # Business logic
└── schemas/             # Pydantic models
```
