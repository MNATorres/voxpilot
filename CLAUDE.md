# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project

**VoxPilot** — a voice-controlled action pilot API built with **FastAPI**.
The goal is to expose HTTP endpoints that trigger actions from voice commands.
Currently only a `/health` endpoint exists as the project baseline.

## Tech stack

- Python 3.12+
- FastAPI (web framework)
- Uvicorn (ASGI server)
- **uv** for environment and dependency management
- pytest + httpx for testing (dev group)

## Commands

```bash
uv sync                                 # create .venv and install deps
uv run uvicorn app.main:app --reload    # run the dev server (http://127.0.0.1:8000)
uv add <package>                        # add a runtime dependency
uv add --dev <package>                  # add a dev dependency
uv run pytest                           # run tests
```

Always use `uv run ...` to execute Python — never call a global `python`,
so the project's virtual environment is used.

## Architecture

Strict layered flow: **router → controller → service**, with Pydantic schemas
for I/O. Keep each layer's responsibility isolated.

```
app/
├── main.py                 # app factory (create_app) + router wiring
├── core/config.py          # Settings + get_settings() (cached)
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

## Conventions

- Commit messages in **English**, atomic (one logical change per commit).
- Type-hint public functions; keep modules small and single-purpose.
- Verify changes before committing (import the app or hit the endpoint with
  `TestClient`).
