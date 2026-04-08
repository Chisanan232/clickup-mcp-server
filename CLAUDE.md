# CLAUDE.md — ClickUp MCP Server

This file provides guidance for AI assistants working in this repository.

## Project Overview

**clickup-mcp-server** (v0.2.0) is a Python-based [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that gives AI assistants standardized access to the ClickUp API. It exposes ClickUp resources (Teams, Spaces, Folders, Lists, Tasks) as MCP tools, runs as a FastAPI/Uvicorn web server, and handles incoming ClickUp webhook events.

- **Language**: Python 3.13+
- **Package manager**: `uv`
- **Build backend**: `hatchling`
- **PyPI package**: `clickup-mcp-server`

---

## Repository Structure

```
clickup_mcp/           # Main source package
  _base/               # Abstract base factories (BaseServerFactory)
  api/                 # ClickUp resource managers (SpaceAPI, TeamAPI, ...)
  mcp_server/          # MCP server: tool definitions + FastMCP factory
    app.py             # MCPServerFactory (singleton)
    models/            # Input/output Pydantic models for MCP tools
    space.py, task.py, list.py, folder.py, team.py, workspace.py
    errors/            # Error handling decorators (@handle_tool_errors)
  models/              # Data layer
    domain/            # Type-safe domain objects (ClickUpSpace, Task, ...)
    dto/               # Serialization models (deserialize / serialize)
    mapping/           # DTO ↔ Domain mappers
    cli.py             # ServerConfig, LogLevel, MCPTransportType
  web_server/          # FastAPI web server
    app.py             # WebServerFactory (singleton)
    event/             # Webhook ingress + event dispatch
      webhook.py       # POST /webhook/clickup endpoint
      sink.py          # EventSink (local vs. message queue)
      handler/         # Decorator & OOP-style handler registration
      models/          # Webhook event models and enums
  client.py            # ClickUpAPIClient (async httpx)
  config.py            # Pydantic Settings (env vars)
  entry.py             # CLI entry point (clickup-mcp-server command)
  exceptions.py        # Exception hierarchy
  types.py             # PEP 561 type aliases (500+ lines)

test/
  unit_test/           # Isolated unit tests
  integration_test/    # Multi-component tests (real FastAPI app)
  contract_test/       # Webhook contract tests (35+ JSON fixtures)
  e2e_test/            # End-to-end tests (requires live ClickUp API)
  ci_script_test/      # CI script validation
  conftest.py          # Shared fixtures (test_settings)
  config.py            # Test configuration from environment

docs/                  # Docusaurus documentation site
scripts/               # CI helper scripts
.github/workflows/     # GitHub Actions pipelines
```

---

## Development Setup

```bash
# Install all dependencies (including dev + pre-commit-ci groups)
uv sync --all-extras

# Install pre-commit hooks
pre-commit install
```

---

## Running the Server

```bash
# With a ClickUp API token directly
clickup-mcp-server --token pk_your_token_here

# From a .env file
clickup-mcp-server --env .env

# Full options
clickup-mcp-server \
  --host 0.0.0.0 \
  --port 8000 \
  --log-level info \
  --transport sse \       # or http-streaming
  --reload                # dev auto-reload

# As Python module
python -m clickup_mcp
```

Transport options:
- `sse` (default): MCP over SSE, mounted at `/sse`
- `http-streaming`: MCP over HTTP streaming, mounted at `/mcp`

Web endpoints always available:
- `GET /health` — health check
- `POST /webhook/clickup` — ClickUp webhook ingress

---

## Testing

```bash
# Run all tests (coverage enabled by default via pytest.ini)
pytest

# Skip slow tests
pytest -m "not slow"

# Specific test suites
pytest test/unit_test/
pytest test/integration_test/
pytest test/contract_test/
pytest test/e2e_test/   # requires CLICKUP_API_TOKEN + real resources

# Run with coverage report
pytest --cov=clickup_mcp/ --cov-report=term-missing
```

`pytest.ini` settings:
- `asyncio_mode = auto` — all async tests run automatically
- `--reruns 1` — flaky tests retry once
- `-p no:warnings` — warnings suppressed in test output
- Coverage configured in `.coveragerc`

---

## Code Quality

Pre-commit hooks (run automatically on commit, configured in `.pre-commit-config.yaml`):

| Tool | Purpose |
|------|---------|
| `black` | Code formatting (line length: **120**) |
| `isort` | Import sorting (black profile) |
| `autoflake` | Remove unused imports |
| `mypy` | Static type checking (`--ignore-missing-imports`) |
| `uv-lock` | Keep `uv.lock` in sync |

Run manually:
```bash
pre-commit run --all-files
mypy clickup_mcp/
```

---

## Architecture Patterns

### 1. Singleton Factory Pattern

All major components use a factory with `.create()`, `.get()`, and `.reset()`:

```python
# MCPServerFactory, WebServerFactory, ClickUpAPIClientFactory
mcp = MCPServerFactory.create()   # first call
mcp = MCPServerFactory.get()      # subsequent calls
MCPServerFactory.reset()          # test teardown
```

**Always call `.reset()` in test teardown** to avoid singleton state leaking between tests.

### 2. DTO / Domain / Mapper Separation

- **Domain models** (`models/domain/`): type-safe business objects, validated
- **DTOs** (`models/dto/`): API serialization with `.deserialize()` / `.serialize()`
- **Mappers** (`models/mapping/`): bidirectional conversion between layers

Do not bypass this layering — all API responses go through DTO → Domain.

### 3. MCP Tool Definitions

Tools live in `mcp_server/<resource>.py`. Each tool:
- Is decorated with `@mcp.tool()` (from the `FastMCP` singleton)
- Uses `@handle_tool_errors` from `mcp_server/errors/` to normalize errors
- Accepts Pydantic input models from `mcp_server/models/`
- Returns structured data (domain models or dicts)

Tool naming convention: `resource.operation` (e.g., `space.get`, `task.list`, `folder.create`).

### 4. Event / Webhook System

```
POST /webhook/clickup
  → parse ClickUpWebhookEvent
  → EventSink.dispatch()
    → local: call registered handlers directly
    → MQ mode: publish to message queue
```

Handlers can be registered two ways:
- **Decorator style**: `@clickup_event_handler(EventType.TASK_CREATED)`
- **OOP style**: subclass `ClickUpEventHandler`

### 5. Error Handling

The `@handle_tool_errors` decorator wraps MCP tools. Custom exceptions in `exceptions.py` form a hierarchy under `ClickUpError`. Always raise typed exceptions rather than bare `Exception`.

---

## Key Conventions

### Typing
- All code must be fully type-annotated
- Complex type aliases live in `clickup_mcp/types.py` (PEP 561, `py.typed` marker)
- Do not use `Any` without a comment explaining why

### Naming
- Modules/functions/variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private members: `_leading_underscore`
- Type aliases: `CapWords` (e.g., `ClickUpToken`, `SpaceId`)

### Async
- All I/O is async (`httpx`, `FastAPI`, `MCP`)
- Use `async def` and `await` throughout; never block the event loop

### Configuration
- Settings managed via Pydantic Settings (`clickup_mcp/config.py`)
- Environment variables are the canonical config source
- Use `.env` files for local development; never hardcode secrets

### Logging
- One logger per module: `logger = logging.getLogger(__name__)`
- Use structured log messages with context (IDs, operation names)

### Docstrings
- Public methods have docstrings with `Args:`, `Returns:`, `Raises:`, and `Usage Examples:`
- This is especially important for MCP tool functions (they surface to AI clients)

---

## Adding a New MCP Tool

1. Add the resource manager method in `clickup_mcp/api/<resource>.py`
2. Add input/output Pydantic models in `clickup_mcp/mcp_server/models/`
3. Register the tool in `clickup_mcp/mcp_server/<resource>.py` with `@mcp.tool()` + `@handle_tool_errors`
4. Add domain model changes in `models/domain/`, DTO in `models/dto/`, mapper in `models/mapping/`
5. Write unit tests in `test/unit_test/` and integration tests in `test/integration_test/`

---

## CI/CD

GitHub Actions workflows:
- **`ci.yaml`**: Main pipeline — runs all tests, uploads coverage to CodeCov, sends metrics to SonarCloud
- **`type-check.yml`**: MyPy type checking
- **`docker-ci.yml`**: Docker image build validation
- **`documentation.yaml`**: Build and deploy Docusaurus docs to GitHub Pages
- **`release.yml`**: Release to PyPI + GitHub releases
- **`check-clickup-api-spec.yaml`**: Validates ClickUp API spec compliance
- **`check-clickup-webhook-payloads.yml`**: Validates webhook fixture files

Branches:
- `master` is the main branch — PRs target here
- CI runs on push to `master` and on all pull requests

---

## Environment Variables

Key variables (see `.env.example` for full list):

| Variable | Purpose |
|----------|---------|
| `CLICKUP_API_TOKEN` | ClickUp personal API token (required) |
| `CLICKUP_WEBHOOK_SECRET` | Webhook signature verification secret |
| `CORS_ORIGINS` | Allowed CORS origins (comma-separated) |
| `EVENT_SINK_BACKEND` | `local` (default) or message queue backend |
| `MQ_*` | Message queue configuration (when using MQ sink) |

---

## Docker

```bash
docker build -t clickup-mcp-server .
docker run -e CLICKUP_API_TOKEN=pk_... -p 8000:8000 clickup-mcp-server
```

The `Dockerfile` uses `python:3.13-slim` as the base image.
