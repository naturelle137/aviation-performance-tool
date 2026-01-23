# Aviation Performance & Mass/Balance Tool

A safety-critical web application for General Aviation pilots to calculate Mass & Balance, Takeoff/Landing Performance, and Fuel Endurance for SEP aircraft.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## ✈️ Features

- **Aircraft Profile Management** - CRUD operations with verification status
- **Mass & Balance Calculation** - Graphical CG envelope with takeoff/landing points
- **Performance Calculation** - POH interpolation + FSM 3/75 fallback
- **Fuel & Endurance Planning** - Multi-tank support with density calculations
- **Weather Integration** - METAR/TAF for automated input (Phase 2)
- **PDF Export** - Digital Loadsheet documentation (Phase 3)

## 🛡️ Safety-First Design

This is **safety-critical aviation software** following:
- EARS requirement syntax with full traceability
- Hazard analysis with 14 identified hazards (H-01 to H-14)
- Priority system: P1 (Safety) → P2 (Operational) → P3 (Comfort)

See [Safety Traceability Matrix](docs/requirements/safety_traceability_matrix.md).

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [Requirements](docs/requirements/initial_requirements.md) | System requirements (EARS syntax) |
| [Safety Matrix](docs/requirements/safety_traceability_matrix.md) | Hazard log and mitigations |
| [Architecture](docs/architecture/ARCHITECTURE.md) | System design and components |
| [API](docs/api/API.md) | REST API documentation |
| [Testing](docs/testing/TESTING.md) | Test strategy and coverage |
| [Contributing](CONTRIBUTING.md) | Development guidelines |
| [Changelog](CHANGELOG.md) | Version history |
| [Branching](docs/development/BRANCHING_STRATEGY.md) | Git workflow |

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 20+ (frontend dev)
- Python 3.12+ (backend dev)
- uv (Python package manager)

### With Docker
```bash
git clone https://github.com/naturelle137/aviation-performance-tool.git
cd aviation-performance-tool
cp .env.example .env
docker compose up -d
```

Access:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Local Development

**Backend:**
```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## 🔧 Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Vue 3 + TypeScript, Vite |
| Backend | FastAPI (Python 3.12) |
| Package Mgmt | uv (Python), npm (Node) |
| Deployment | Docker |

## 🧪 Testing

```bash
# Backend
cd backend
uv run pytest --cov=app

# Frontend
cd frontend
npm run test:unit
```

See [Testing Documentation](docs/testing/TESTING.md) for coverage requirements.

## 🤝 Contributing

We follow **Conventional Commits** and strict safety guidelines.

```bash
# Feature branch
git checkout develop
git checkout -b feature/your-feature

# Commit with REQ-ID
git commit -m "feat(mb): add CG validation [REQ-MB-06]"
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for full guidelines.

## 📋 Roadmap

| Phase | Focus | Status |
|-------|-------|--------|
| 1 | M&B Core, Performance Engine, Units | 🔄 In Progress |
| 2 | Weather, Wind, Passenger Profiles | ⏳ Planned |
| 3 | PDF Export, Cloud Sync | ⏳ Planned |

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

> "Software calculates, the pilot decides – the documentation ensures that the basis for the calculation is correct."
