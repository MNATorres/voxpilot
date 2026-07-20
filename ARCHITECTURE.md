# Arquitectura de VoxPilot

**VoxPilot** es una API de piloto de acciones controlado por voz, construida con
**FastAPI**. Recibe comandos de voz (ya transcritos a texto) por HTTP, ejecuta la
acción correspondiente y la registra con logging estructurado.

Este documento describe la arquitectura completa del proyecto con diagramas.

---

## 1. Visión general del sistema

```mermaid
flowchart LR
    Cliente(["🎤 Cliente<br/>(comando de voz como texto)"])
    subgraph VoxPilot ["⚙️ VoxPilot (FastAPI + Uvicorn)"]
        API["API HTTP<br/>GET /health · POST /speak"]
    end
    Logs[("📋 Logs estructurados<br/>(structlog + correlation_id)")]

    Cliente -- "JSON por HTTP" --> API
    API -- "respuesta JSON<br/>+ header X-Request-ID" --> Cliente
    API -- "cada acción se registra" --> Logs
```

---

## 2. Arquitectura en capas

El proyecto sigue un flujo estricto **router → controller → service**, con
schemas Pydantic en la frontera HTTP. Cada capa tiene una responsabilidad
aislada y solo conoce a la capa inmediatamente inferior.

```mermaid
flowchart TD
    subgraph HTTP ["🌐 Frontera HTTP"]
        R["<b>Routers</b><br/><i>app/routers/</i><br/>Declaran endpoints y<br/>(de)serializan con schemas.<br/>Sin lógica de negocio."]
        S["<b>Schemas</b><br/><i>app/schemas/</i><br/>Modelos Pydantic de<br/>request/response."]
    end

    C["<b>Controllers</b><br/><i>app/controllers/</i><br/>Orquestan y delegan a los servicios.<br/>Sin imports de FastAPI."]

    SV["<b>Services</b><br/><i>app/services/</i><br/>Lógica de negocio pura.<br/>Sin HTTP, testeables en aislamiento."]

    subgraph CORE ["🧩 Núcleo transversal"]
        CFG["<b>core/config.py</b><br/>Settings + get_settings()<br/>(cacheado con lru_cache)"]
        LOG["<b>core/logging.py</b><br/>structlog + get_logger()<br/>inyecta correlation_id"]
    end

    R -- "valida entrada /<br/>serializa salida" --> S
    R -- "llama" --> C
    C -- "delega" --> SV
    SV -. "usa" .-> CFG
    SV -. "usa" .-> LOG

    style HTTP fill:#e8f0fe,stroke:#4285f4
    style CORE fill:#fef7e0,stroke:#f9ab00
```

**Reglas de dependencia** (siempre hacia abajo, nunca al revés):

| Capa | Puede importar | No puede |
|---|---|---|
| `routers/` | schemas, controllers, `fastapi` | services directamente, lógica de negocio |
| `controllers/` | services | `fastapi`, schemas |
| `services/` | `core/` | `fastapi`, HTTP, capas superiores |
| `schemas/` | `pydantic` | todo lo demás |

---

## 3. Composición de la aplicación (`app/main.py`)

`create_app()` es la fábrica de la aplicación: configura el logging, lee la
configuración, registra el middleware y cablea los routers.

```mermaid
flowchart TD
    MAIN["app/main.py · create_app()"]
    MAIN --> L1["1 · configure_logging()<br/>configura structlog"]
    MAIN --> L2["2 · get_settings()<br/>nombre, versión, descripción"]
    MAIN --> L3["3 · FastAPI(...)"]
    MAIN --> L4["4 · CorrelationIdMiddleware<br/>genera/propaga X-Request-ID"]
    MAIN --> L5["5 · include_router(health.router)"]
    MAIN --> L6["6 · include_router(speech.router)"]
```

---

## 4. Módulos y dependencias reales

Grafo de imports entre los módulos del proyecto:

```mermaid
flowchart LR
    subgraph main ["main.py"]
        APP["create_app()"]
    end

    subgraph routers ["routers/"]
        RH["health.py<br/>GET /health"]
        RS["speech.py<br/>POST /speak"]
    end

    subgraph schemas ["schemas/"]
        SH["health.py<br/>HealthResponse"]
        SS["speech.py<br/>SpeechRequest<br/>SpeechResponse"]
    end

    subgraph controllers ["controllers/"]
        CH["health_controller.py<br/>HealthController"]
        CS["speech_controller.py<br/>SpeechController"]
    end

    subgraph services ["services/"]
        SVH["health_service.py<br/>HealthService"]
        SVS["speech_service.py<br/>SpeechService + COMMANDS"]
    end

    subgraph core ["core/"]
        CFG["config.py<br/>Settings · get_settings()"]
        LOG["logging.py<br/>configure_logging() · get_logger()"]
    end

    APP --> RH
    APP --> RS
    APP --> CFG
    APP --> LOG

    RH --> SH
    RH --> CH
    RS --> SS
    RS --> CS

    CH --> SVH
    CS --> SVS

    SVH --> CFG
    SVS --> LOG
```

---

## 5. Flujo de una petición: `POST /speak`

```mermaid
sequenceDiagram
    autonumber
    actor Cliente
    participant MW as CorrelationIdMiddleware
    participant R as routers/speech.py<br/>speak()
    participant Sch as schemas/speech.py
    participant C as SpeechController
    participant S as SpeechService
    participant L as structlog (logger "speech")

    Cliente->>MW: POST /speak {"command": "camina hacia adelante"}
    MW->>MW: genera/propaga correlation_id
    MW->>R: request con contexto
    R->>Sch: valida body → SpeechRequest
    R->>C: handle(command)
    C->>S: process(command)
    S->>S: normaliza (strip + lower)<br/>y busca en COMMANDS

    alt comando reconocido
        S->>L: info("caminó hacia adelante", recibido=...)
        S-->>C: {recognized: true, action: "caminó hacia adelante"}
    else comando no reconocido
        S->>L: info("comando no reconocido", recibido=...)
        S-->>C: {recognized: false, action: null}
    end

    C-->>R: dict resultado
    R->>Sch: SpeechResponse(**resultado)
    R-->>MW: respuesta JSON
    MW-->>Cliente: 200 OK + header X-Request-ID
```

## 6. Flujo de una petición: `GET /health`

```mermaid
sequenceDiagram
    autonumber
    actor Cliente
    participant MW as CorrelationIdMiddleware
    participant R as routers/health.py<br/>health()
    participant C as HealthController
    participant S as HealthService
    participant CFG as core/config.py

    Cliente->>MW: GET /health
    MW->>R: request con correlation_id
    R->>C: check()
    C->>S: get_status()
    S->>CFG: get_settings() (cacheado)
    CFG-->>S: Settings(app_name, version)
    S-->>C: {status: "ok", service: "VoxPilot", version: "0.1.0"}
    C-->>R: dict resultado
    R-->>MW: HealthResponse
    MW-->>Cliente: 200 OK + header X-Request-ID
```

---

## 7. Pipeline de logging estructurado

Todo log pasa por la cadena de procesadores de **structlog** configurada en
`core/logging.py`. El `correlation_id` lo aporta `asgi-correlation-id` por
request, de modo que cada línea de log se puede correlacionar con la petición
HTTP que la originó (y con el header `X-Request-ID` que recibe el cliente).

```mermaid
flowchart LR
    E["logger.info(evento, **datos)"] --> P1["merge_contextvars"]
    P1 --> P2["_add_correlation_id<br/>(lo toma del contexto ASGI)"]
    P2 --> P3["add_log_level"]
    P3 --> P4["TimeStamper<br/>YYYY-MM-DD HH:MM:SS"]
    P4 --> P5["ConsoleRenderer"]
    P5 --> OUT[("stdout:<br/>date · level · evento ·<br/>correlation_id · campos extra")]
```

Reglas del proyecto: usar siempre `get_logger(<nombre>)`; nunca `print()` ni el
módulo `logging` de la stdlib directamente.

---

## 8. Estructura de archivos

```
voxpilot/
├── app/
│   ├── main.py                        # fábrica create_app() + middleware + routers
│   ├── core/
│   │   ├── config.py                  # Settings + get_settings() (lru_cache)
│   │   └── logging.py                 # structlog + correlation_id
│   ├── routers/
│   │   ├── health.py                  # GET /health
│   │   └── speech.py                  # POST /speak
│   ├── controllers/
│   │   ├── health_controller.py       # HealthController
│   │   └── speech_controller.py       # SpeechController
│   ├── services/
│   │   ├── health_service.py          # HealthService
│   │   └── speech_service.py          # SpeechService + mapa COMMANDS
│   └── schemas/
│       ├── health.py                  # HealthResponse
│       └── speech.py                  # SpeechRequest / SpeechResponse
├── tests/                             # un archivo por unidad bajo prueba
│   ├── test_api.py                    # end-to-end con TestClient
│   ├── test_config.py
│   ├── test_logging.py
│   ├── test_health_controller.py
│   ├── test_health_service.py
│   ├── test_speech_controller.py
│   └── test_speech_service.py
├── pyproject.toml                     # deps gestionadas con uv
├── uv.lock
└── CLAUDE.md                          # guía del proyecto
```

---

## 9. Estrategia de testing

Cada capa se prueba en aislamiento, más una suite end-to-end. La cobertura se
exige al **90 %** (`--cov-fail-under=90`).

```mermaid
flowchart TD
    subgraph E2E ["End-to-end"]
        TAPI["test_api.py<br/>TestClient contra la app completa<br/>(/health y /speak reales)"]
    end

    subgraph UNIT ["Unitarios (con fakes/mocks)"]
        TC["test_*_controller.py<br/>inyectan un servicio falso<br/>en el controller"]
        TS["test_*_service.py<br/>monkeypatch del logger<br/>para asertar el logging"]
        TCORE["test_config.py · test_logging.py<br/>núcleo transversal"]
    end

    TAPI --> APP2["create_app()"]
    TC --> CTRL2["Controllers"]
    TS --> SRV2["Services"]
    TCORE --> CORE2["core/"]
```

---

## 10. Cómo se extiende (patrón para nuevas funcionalidades)

Para añadir una nueva capacidad se crea **un archivo por capa** y se registra el
router en `create_app()`:

```mermaid
flowchart LR
    S1["1 · schemas/&lt;feature&gt;.py<br/>modelos request/response"] --> S2["2 · services/&lt;feature&gt;_service.py<br/>la lógica"]
    S2 --> S3["3 · controllers/&lt;feature&gt;_controller.py<br/>orquestación"]
    S3 --> S4["4 · routers/&lt;feature&gt;.py<br/>el endpoint"]
    S4 --> S5["5 · app.include_router(...)<br/>en create_app()"]
```

Para añadir solo un **comando de voz nuevo**, basta con agregar una entrada al
mapa `COMMANDS` en `app/services/speech_service.py`:

```python
COMMANDS: dict[str, str] = {
    "camina hacia adelante": "caminó hacia adelante",
    # "nuevo comando": "acción registrada",
}
```

---

## Stack tecnológico

| Componente | Herramienta |
|---|---|
| Lenguaje | Python 3.12+ |
| Framework web | FastAPI |
| Servidor ASGI | Uvicorn |
| Gestión de entorno y deps | uv |
| Logging estructurado | structlog + asgi-correlation-id |
| Testing | pytest + pytest-cov + httpx (cobertura ≥ 90 %) |
