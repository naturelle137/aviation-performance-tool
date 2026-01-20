# Aviation Performance & Mass/Balance Tool

A web-based tool for calculating Mass & Balance, fuel planning, and takeoff/landing performance for SEP aircraft (Single Engine Piston).

## Features

- ✈️ **Aircraft Profile Management** - CRUD operations for aircraft with weight stations and CG envelopes
- ⚖️ **Mass & Balance Calculation** - Tabular and graphical CG visualization
- ⛽ **Fuel Planning** - Trip fuel, reserve, and endurance calculations
- 🛫 **Performance Calculation** - Takeoff and landing distance with corrections (FSM 3/75 support)
- 🌤️ **Weather Integration** - METAR/TAF retrieval for performance calculations
- 📄 **PDF Export** - Professional flight documentation with charts

## Tech Stack

### Backend
- **Python 3.12** with FastAPI
- **SQLAlchemy 2.0** ORM with Alembic migrations
- **PostgreSQL** (Production) / SQLite (Development)
- **uv** for dependency management

### Frontend
- **Vue 3** with Composition API
- **TypeScript**
- **Vite** build tool
- **PrimeVue** UI components
- **Chart.js** for M&B diagrams

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 20+ (for frontend development)
- Python 3.12+ (for backend development)
- uv (Python package manager)

### Development Setup

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/aviation-performance-tool.git
cd aviation-performance-tool
```

2. Copy environment files:
```bash
cp .env.example .env
```

3. Start with Docker Compose:
```bash
docker compose up -d
```

4. Access the application:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Local Development (without Docker)

#### Backend
```bash
cd backend
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
aviation-performance-tool/
├── backend/           # FastAPI backend
├── frontend/          # Vue 3 frontend
├── docs/              # Documentation
├── docker-compose.yml # Development environment
└── .github/           # CI/CD workflows
```

## Testing

```bash
# Backend tests
cd backend
uv run pytest

# Frontend tests
cd frontend
npm run test:unit
npm run test:e2e
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please read the contribution guidelines first.
