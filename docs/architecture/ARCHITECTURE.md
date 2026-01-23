# Architecture Documentation

## System Overview

The Aviation Performance Tool is a safety-critical web application for General Aviation pilots to calculate Mass & Balance, Takeoff/Landing Performance, and Fuel Endurance.

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (Vue 3)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  M&B Module  │  │ Performance  │  │   Aircraft Manager   │  │
│  │              │  │   Module     │  │                      │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────┬───────────────────────────────────┘
                              │ REST API
┌─────────────────────────────┴───────────────────────────────────┐
│                      Backend (FastAPI)                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    API Layer                              │  │
│  │   /api/v1/aircraft  /api/v1/calculate  /api/v1/weather   │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                   Service Layer                           │  │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────────────┐   │  │
│  │  │ Mass &     │ │Performance │ │ Unit Conversion    │   │  │
│  │  │ Balance    │ │ Engine     │ │ (Branded Types)    │   │  │
│  │  └────────────┘ └────────────┘ └────────────────────┘   │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Data Layer                             │  │
│  │       Aircraft Profiles (JSON) │ Airport Database         │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| Frontend | Vue 3 + TypeScript | Reactive UI, strong typing |
| Styling | CSS (Vanilla) | Maximum control, no framework lock-in |
| Backend | FastAPI (Python) | Fast, async, auto-generated OpenAPI docs |
| Database | JSON Files (local) | Offline-first, portable profiles |
| Package Manager | uv (Python), npm (Node) | Fast, reliable dependency management |
| Containerization | Docker | Consistent deployment |

---

## Module Architecture

### 1. Mass & Balance Service (`backend/app/services/mass_balance.py`)

**Responsibility**: Calculate total weight and CG position from load station inputs.

**Key Classes**:
```python
class LoadStation:
    """A loading point with weight and arm."""
    name: str
    weight_kg: Kilogram
    arm_m: Meter

class MassBalanceResult:
    """Result of M&B calculation."""
    total_weight_kg: Kilogram
    cg_position_m: Meter
    takeoff_cg: CGPoint
    landing_cg: CGPoint
    is_within_envelope: bool
    warnings: list[Warning]
```

**Requirements Implemented**: REQ-MB-01 through REQ-MB-11

---

### 2. Performance Engine (`backend/app/services/performance.py`)

**Responsibility**: Calculate takeoff/landing distances using POH data or FSM 3/75.

**Calculation Modes**:
- **Mode A**: Bilinear interpolation from POH tables
- **Mode B**: Algorithmic using FSM 3/75 factors

**Key Functions**:
```python
def calculate_takeoff_distance(
    aircraft: AircraftProfile,
    conditions: EnvironmentalConditions,
    runway: Runway
) -> PerformanceResult: ...

def calculate_density_altitude(
    elevation_ft: float,
    qnh_hpa: float,
    temperature_c: float
) -> float: ...
```

**Requirements Implemented**: REQ-PF-01 through REQ-PF-24

---

### 3. Unit Conversion Service (`backend/app/services/units.py`)

**Responsibility**: Prevent unit confusion through branded types (H-01 mitigation).

**Branded Types**:
```python
class Kilogram(float): """Mass in kilograms."""
class Pound(float): """Mass in pounds."""
class Liter(float): """Volume in liters."""
class Gallon(float): """Volume in US gallons."""
class Meter(float): """Length in meters."""
class Feet(float): """Length in feet."""
```

**Conversion is explicit**:
```python
# Type-safe conversions
kg = Kilogram(100)
lb = kg.to_pounds()  # Returns Pound(220.46)

# Compile-time safety (with type checker)
def calculate_moment(weight: Kilogram, arm: Meter) -> KilogramMeter:
    return KilogramMeter(weight * arm)
```

**Requirements Implemented**: REQ-SYS-03, REQ-UQ-04, REQ-AC-13

---

### 4. CG Validation Service (`backend/app/services/cg_validation.py`)

**Responsibility**: Validate CG position against aircraft envelope.

**Algorithm**: Point-in-Polygon (Ray Casting) for polygonal envelopes.

```python
def is_within_envelope(
    cg: CGPoint,
    envelope: list[EnvelopeVertex]
) -> bool:
    """
    Uses ray casting algorithm for polygon containment.
    Supports non-linear, sloped envelopes (REQ-MB-06).
    """
```

**Requirements Implemented**: REQ-MB-06, REQ-MB-10

---

## Data Models

### Aircraft Profile Schema (`data/schemas/aircraft.json`)

```json
{
  "registration": "D-EABC",
  "manufacturer": "Diamond",
  "model": "DA40 D",
  "icao_designator": "DA40",
  "version": {
    "valid_from": "2024-01-15",
    "weighing_report": "WR-2024-001"
  },
  "status": "verified",
  "units": {
    "mass": "kg",
    "volume": "L",
    "arm": "m"
  },
  "basic_empty_mass": {
    "weight_kg": 850.5,
    "arm_m": 2.345
  },
  "fuel_tanks": [
    {
      "name": "Main Tank",
      "capacity_l": 148,
      "unusable_l": 7.6,
      "arm_m": 2.42,
      "fuel_type": "JET-A1"
    }
  ],
  "loading_stations": [
    {
      "name": "Pilot",
      "arm_m": 2.32,
      "default_kg": 80
    }
  ],
  "envelopes": {
    "normal": {
      "mtom_kg": 1200,
      "vertices": [
        {"arm_m": 2.20, "mass_kg": 800},
        {"arm_m": 2.45, "mass_kg": 800},
        {"arm_m": 2.50, "mass_kg": 1200},
        {"arm_m": 2.25, "mass_kg": 1200}
      ]
    }
  },
  "performance": {
    "mode": "table",
    "takeoff_tables": "...",
    "landing_tables": "..."
  }
}
```

---

## Safety Architecture

### Hazard Mitigation Layers

```
Layer 1: Input Validation (REQ-UI-11)
         ↓ Invalid inputs rejected
Layer 2: Type Safety (Branded Units - H-01 mitigation)
         ↓ Unit confusion prevented
Layer 3: Calculation Guards (REQ-PF-13, REQ-PF-17)
         ↓ Extrapolation controlled
Layer 4: Result Validation (REQ-MB-03, REQ-MB-04, REQ-PF-09)
         ↓ Limit violations detected
Layer 5: Visual Feedback (REQ-UI-10)
         ↓ Pilot informed
Layer 6: Audit Trail (Logging)
         ↓ Decisions recorded
```

### Error Handling Strategy

| Error Type | Handling | User Impact |
|------------|----------|-------------|
| Input Validation | Reject immediately | Red border, error message |
| Calculation Error | Raise exception, log | "Unable to calculate" message |
| Limit Violation | Return result + warning | Yellow/Red visual indicator |
| System Error | Log, graceful degradation | Error page with recovery options |

---

## File Structure

```
aviation-performance-tool/
├── backend/
│   ├── app/
│   │   ├── api/              # API route handlers
│   │   │   └── v1/
│   │   ├── models/           # Pydantic data models
│   │   ├── services/         # Business logic
│   │   │   ├── mass_balance.py
│   │   │   ├── performance.py
│   │   │   ├── units.py
│   │   │   └── cg_validation.py
│   │   └── core/             # Configuration, utilities
│   ├── data/                 # Aircraft profiles, airport DB
│   └── tests/
│       ├── unit/
│       ├── integration/
│       └── safety/
├── frontend/
│   ├── src/
│   │   ├── components/       # Vue components
│   │   ├── views/            # Page-level views
│   │   ├── services/         # API clients
│   │   └── stores/           # Pinia state management
│   └── tests/
└── docs/
    ├── architecture/         # This documentation
    ├── api/                  # API documentation
    ├── requirements/         # System requirements
    └── development/          # Development guides
```

---

## Deployment Architecture

```
┌─────────────────────────────────────────────┐
│              Docker Compose                  │
│  ┌─────────────────┐  ┌─────────────────┐  │
│  │    Frontend     │  │     Backend     │  │
│  │   (nginx:80)    │  │  (uvicorn:8000) │  │
│  └────────┬────────┘  └────────┬────────┘  │
│           │                    │            │
│           └────────┬───────────┘            │
│                    │                        │
│           ┌────────┴────────┐               │
│           │  Shared Volume  │               │
│           │   (data/)       │               │
│           └─────────────────┘               │
└─────────────────────────────────────────────┘
```

---

## Future Considerations

### Phase 2 Additions
- Weather service integration (METAR/TAF API)
- Wind component calculator

### Phase 3 Additions
- Cloud sync (Firebase/Firestore)
- PDF export service
- User authentication

---

> Document Version: 0.1.0
> Last Updated: 2025-01-23
