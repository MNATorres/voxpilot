# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project

**VoxPilot** — a voice-controlled action pilot API built with **FastAPI**.
The goal is to expose HTTP endpoints that trigger actions from voice commands.

Endpoints:
- `GET /health` — service health check.
- `POST /speak` — receives a voice command as text (`{"command": "..."}`),
  runs the matching action and logs it. Recognized commands live in the
  `COMMANDS` map in `app/services/speech_service.py`.

## Tech stack

- Python 3.12+
- FastAPI (web framework)
- Uvicorn (ASGI server)
- **uv** for environment and dependency management
- **structlog** + **asgi-correlation-id** for structured logging
- pytest + pytest-cov + httpx for testing (dev group)

## Commands

```bash
uv sync                                 # create .venv and install deps
uv run uvicorn app.main:app --reload    # run the dev server (http://127.0.0.1:8000)
uv add <package>                        # add a runtime dependency
uv add --dev <package>                  # add a dev dependency
uv run pytest                           # run tests with coverage
```

Always use `uv run ...` to execute Python — never call a global `python`,
so the project's virtual environment is used.

On Windows, prefix Python commands that print accented output with
`PYTHONIOENCODING=utf-8 PYTHONUTF8=1` to avoid mangled console encoding.

## Architecture

Strict layered flow: **router → controller → service**, with Pydantic schemas
for I/O. Keep each layer's responsibility isolated.

```
app/
├── main.py                 # app factory (create_app) + middleware + router wiring
├── core/
│   ├── config.py           # Settings + get_settings() (cached)
│   └── logging.py          # structlog config + get_logger(); injects correlation_id
├── routers/                # HTTP routes; define APIRouter, no business logic
├── controllers/            # orchestration; call services, no HTTP concerns
├── services/               # business logic; no HTTP/FastAPI imports
└── schemas/                # Pydantic request/response models
```

### Layer rules

- **Routers** only declare endpoints and (de)serialize via schemas. They call a
  controller and return a schema instance.
- **Controllers** orchestrate and delegate to services. No `fastapi` imports.
- **Services** hold business logic. No `fastapi` imports, no HTTP awareness —
  they must be testable in isolation.
- **Schemas** are Pydantic models used at the router boundary.

### Adding a new feature (pattern)

To add a new capability (e.g. a voice command), create one file per layer and
wire the router in `main.py` via `app.include_router(...)`:
1. `schemas/<feature>.py` — request/response models
2. `services/<feature>_service.py` — the logic
3. `controllers/<feature>_controller.py` — orchestration
4. `routers/<feature>.py` — the endpoint
5. `app.include_router(<feature>.router)` in `create_app()`

Do not add business logic to routers or HTTP handling to services.

## Logging

Use `get_logger(<name>)` from `app/core/logging.py` (structlog). Log with an
event message plus structured key/values, e.g.
`logger.info("caminó hacia adelante", recibido=command)`. Every line carries
`date`, `level`, `correlation_id` and any extra fields. The `correlation_id` is
injected automatically per request by `CorrelationIdMiddleware` and returned in
the `X-Request-ID` response header. Do not use the stdlib `logging` module
directly or `print()`.

## Testing

- Tests live in `tests/`, one file per unit under test.
- Run with `uv run pytest`. Coverage is enforced at **90%**
  (`--cov-fail-under=90`); keep new code covered.
- Unit-test services/controllers in isolation using fakes/mocks (inject a fake
  service into a controller; monkeypatch `speech_service.logger` to assert
  logging). Test endpoints end to end with `fastapi.testclient.TestClient`.

## Conventions

- Commit messages in **English**, atomic (one logical change per commit).
- Type-hint public functions; keep modules small and single-purpose.
- Verify changes before committing (import the app or hit the endpoint with
  `TestClient`).
