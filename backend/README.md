# Backend - Aviation Performance Tool

FastAPI backend for aviation M&B and performance calculations.

## Tech Stack

- **Framework**: FastAPI
- **Python**: 3.12+
- **Package Manager**: uv
- **Testing**: pytest

## Quick Start

```bash
# Install dependencies
uv sync

# Run development server
uv run uvicorn app.main:app --reload

# Run tests
uv run pytest
```

## Project Structure

```
backend/
├── app/
│   ├── api/           # Route handlers
│   │   └── v1/
│   ├── models/        # Pydantic schemas
│   ├── services/      # Business logic
│   │   ├── mass_balance.py
│   │   ├── performance.py
│   │   ├── units.py
│   │   └── cg_validation.py
│   ├── core/          # Config, utilities
│   └── main.py        # FastAPI app
├── data/              # Aircraft profiles, databases
├── tests/
│   ├── unit/
│   ├── integration/
│   └── safety/
└── pyproject.toml
```

## API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

See [docs/api/API.md](/docs/api/API.md) for full API documentation.

## Environment Variables

Copy `.env.example` to `.env`:

```bash
cp ../.env.example .env
```

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Enable debug mode | `true` |
| `API_PREFIX` | API route prefix | `/api/v1` |

## Testing

```bash
# All tests
uv run pytest

# With coverage
uv run pytest --cov=app --cov-report=html

# Safety tests only
uv run pytest tests/safety/ -v

# By priority
uv run pytest -m "p1"
```

## Code Quality

```bash
# Lint
uv run ruff check .

# Format
uv run black .

# Type check
uv run mypy app/
```

## Docker

```bash
# Build
docker build -t aviation-tool-backend .

# Run
docker run -p 8000:8000 aviation-tool-backend
```

---

See [CONTRIBUTING.md](/CONTRIBUTING.md) for development guidelines.
