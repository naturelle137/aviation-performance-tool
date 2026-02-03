# Testing Documentation

## Overview

Testing for the Aviation Performance Tool follows a **3-Tier Quality Gate System** aligned with requirement priorities:

| Gate | Priority | Coverage | Description |
|------|----------|----------|-------------|
| **Gate 1** | P1 (Critical/Safety) | $90\%$ | Flight-safe calculations, side-effect free |
| **Gate 2** | P2 (Operational) | $80\%$ | Significant cockpit value, error reduction |
| **Gate 3** | P3 (Global Baseline) | $70\%$ | All remaining code (gapless catch-all) |

---

## Test Structure

```
backend/tests/
├── unit/                        # Fast, isolated tests
│   ├── test_mass_balance_core.py    # P1
│   ├── test_mass_balance_logic.py   # P2
│   ├── test_performance_core.py     # P1
│   ├── test_performance_logic.py    # P2
│   ├── test_unit_conversion.py      # P1 (REQ-SYS-03)
│   ├── test_cg_validation.py        # P1 (REQ-MB-06)
│   └── test_weather_service.py      # P2 (REQ-WX-01)
├── integration/                 # Component interaction tests
│   ├── test_calculation_flow.py
│   ├── test_api_endpoints.py
│   └── test_aircraft_api_full.py
└── safety/                      # Hazard-specific tests
    ├── test_hazard_h01_unit_confusion.py
    ├── test_hazard_h03_interpolation.py
    ├── test_hazard_h05_cg_migration.py
    ├── test_hazard_h06_density_altitude.py
    ├── test_hazard_h11_extrapolation.py
    └── test_hazard_h14_crosswind.py
```

---

## Running Tests

### All Tests
```bash
cd backend
uv run pytest
```

### By Priority Gate
```bash
# Gate 1: P1 Safety-Critical (90% required)
uv run pytest -m "p1" --cov=app --cov-fail-under=90

# Gate 2: P2 Operational (80% required)
uv run pytest -m "p2" --cov=app --cov-fail-under=80

# Gate 3: Global Baseline (70% required)
uv run pytest --cov=app --cov-fail-under=70
```

### By Category
```bash
# Unit tests only (fast)
uv run pytest tests/unit/

# Integration tests
uv run pytest tests/integration/

# Safety-critical tests
uv run pytest tests/safety/

# Specific hazard
uv run pytest tests/safety/test_hazard_h05_cg_migration.py
```

### With Coverage Report
```bash
uv run pytest --cov=app --cov-report=html
# Open htmlcov/index.html
```

---

## Test Markers

Use pytest markers to categorize tests by priority:

```python
import pytest

@pytest.mark.p1
@pytest.mark.safety
def test_cg_outside_envelope_triggers_warning():
    """REQ-MB-03: Visual warning for out-of-envelope CG."""
    ...

@pytest.mark.p2
def test_metar_auto_populates_temperature():
    """REQ-WX-02: Auto-populate from METAR."""
    ...

@pytest.mark.p3
def test_pdf_export_includes_logo():
    """REQ-DOC-01: PDF export formatting."""
    ...
```

### Available Markers

| Marker | Priority | Description |
|--------|----------|-------------|
| `@pytest.mark.p1` | P1 | Safety-critical requirement test |
| `@pytest.mark.p2` | P2 | Operational requirement test |
| `@pytest.mark.p3` | P3 | Comfort/future requirement test |
| `@pytest.mark.safety` | — | Safety hazard test (may combine with p1/p2) |
| `@pytest.mark.slow` | — | Long-running test |
| `@pytest.mark.integration` | — | Integration test |

### Marker Configuration (`pyproject.toml`)

```toml
[tool.pytest.ini_options]
markers = [
    "p1: P1 Safety-Critical tests (90% coverage required)",
    "p2: P2 Operational tests (80% coverage required)",
    "p3: P3 Comfort/Future tests (70% coverage required)",
    "safety: Safety hazard mitigation test",
    "slow: Long-running test",
    "integration: Integration test",
]
```

---

## Per-Module Coverage Requirements (Exhaustive)

### Gate 1: P1 Core ($90\%$ Minimum)

| Module | REQ-IDs | Hazards Mitigated | Min Coverage |
|--------|---------|-------------------|--------------|
| `services/mass_balance/core.py` | REQ-MB-01, REQ-MB-07, REQ-MB-11 | H-04, H-05, H-12 | $90\%$ |
| `services/performance/core.py` | REQ-PF-01, REQ-PF-05, REQ-PF-12, REQ-PF-16, REQ-PF-23 | H-06, H-07, H-11 | $90\%$ |
| `services/units.py` | REQ-SYS-03, REQ-UQ-04, REQ-AC-13 | **H-01** (Critical) | $95\%$ |
| `services/cg_validation.py` | REQ-MB-06, REQ-MB-10 | H-05, H-12 | $90\%$ |

### Gate 2: P2 Operational ($80\%$ Minimum)

| Module | REQ-IDs | Min Coverage |
|--------|---------|--------------|
| `services/mass_balance/logic.py` | REQ-MB-02, REQ-MB-05, REQ-MB-08, REQ-MB-09 | $80\%$ |
| `services/performance/logic.py` | REQ-PF-03, REQ-PF-06, REQ-PF-08, REQ-PF-18, REQ-PF-19 | $80\%$ |
| `services/weather.py` | REQ-WX-01 through REQ-WX-06 | $80\%$ |
| `routers/aircraft.py` | REQ-AC-01 through REQ-AC-06 | $80\%$ |
| `routers/calculations.py` | REQ-MB-01, REQ-PF-01 (API layer) | $80\%$ |
| `routers/weather.py` | REQ-WX-01 (API layer) | $80\%$ |

### Gate 3: P3 Global Baseline ($70\%$ Minimum)

| Module | REQ-IDs | Min Coverage |
|--------|---------|--------------|
| `models/*.py` | REQ-AD-01 through REQ-AD-18 | $70\%$ |
| `schemas/*.py` | (Data transfer objects) | $70\%$ |
| `utils/*.py` | (Utility functions) | $70\%$ |
| `database.py` | REQ-SYS-01, REQ-SYS-02 | $70\%$ |
| `config.py` | (Configuration) | $70\%$ |
| `main.py` | (Application entry) | $70\%$ |
| `routers/health.py` | (Health check endpoint) | $70\%$ |

> [!IMPORTANT]
> Gate 3 is a **gapless catch-all**: any module not explicitly listed in Gate 1 or Gate 2 is automatically covered by the $70\%$ global threshold on `backend/app/`.

### Frontend P1 Components ($90\%$ Threshold)

| File | REQ-ID | Rationale |
|------|--------|-----------|
| `components/charts/CGEnvelopeChart.vue` | REQ-MB-02 | Visual confirmation of safety limits |
| `components/LoadingStation.vue` | REQ-UI-10 | Input for weight and balance |
| `views/CalculationView.vue` | REQ-MB-01 | Main calculation orchestrator |

---

## Safety Test Requirements

Every hazard in the Safety Traceability Matrix requires dedicated tests.

### Test Template for Hazards

```python
"""
Test file: test_hazard_hXX_description.py
Hazard: H-XX - [Hazard Name]
Severity: S1/S2
Mitigated by: REQ-XX-YY, REQ-XX-ZZ
"""

import pytest
from app.services import mass_balance

class TestHazardH05CGMigration:
    """
    H-05: Takeoff within limits, but Landing outside CG limits
    Severity: S1 (Catastrophic)
    Mitigated by: REQ-MB-10, REQ-MB-07
    """
    
    @pytest.mark.p1
    @pytest.mark.safety
    def test_landing_cg_outside_envelope_detected(self):
        """Landing CG must be validated even if takeoff CG is valid."""
        # Arrange
        aircraft = create_kl107_profile()
        loading = create_aft_heavy_loading()
        
        # Act
        result = mass_balance.calculate(aircraft, loading)
        
        # Assert
        assert result.takeoff_cg.within_envelope is True
        assert result.landing_cg.within_envelope is False
        assert "CG_MIGRATION" in [w.code for w in result.warnings]
    
    @pytest.mark.p1
    @pytest.mark.safety
    def test_warning_severity_is_critical(self):
        """CG migration warning must be CRITICAL level."""
        result = self._run_cg_migration_scenario()
        
        warning = next(w for w in result.warnings if w.code == "CG_MIGRATION")
        assert warning.level == "CRITICAL"
        assert warning.hazard_ref == "H-05"
```

---

## Edge-Case Stress Tests

These tests validate extreme scenarios from the Safety Traceability Matrix.

### 1. "The Sahara Switch" (H-06)
```python
@pytest.mark.p1
@pytest.mark.safety
def test_sahara_switch_extreme_hot_high():
    """
    +50°C and 5000ft elevation.
    System must either extrapolate with penalty or block calculation.
    """
    conditions = EnvironmentalConditions(
        temperature_c=50,
        pressure_altitude_ft=5000
    )
    
    result = performance.calculate_takeoff(aircraft, conditions)
    
    if result.status == "BLOCKED":
        assert "EXTRAPOLATION_LIMIT" in result.error_code
    else:
        assert result.calculation_mode == "extrapolated"
        assert "EXTRAPOLATION_PENALTY" in [w.code for w in result.warnings]
```

### 2. "Burn-out Shift" (H-12)
```python
@pytest.mark.p1
@pytest.mark.safety
def test_burnout_shift_cg_migration():
    """
    Maximum passenger load, minimum fuel.
    CG fits at takeoff but shifts aft during fuel burn.
    """
    loading = Loading(
        pilot_kg=85,
        passengers_kg=[90, 90],  # Rear passengers
        baggage_kg=50,           # Aft baggage
        fuel_l=40                # Minimum fuel
    )
    
    result = mass_balance.calculate(klemm_kl107, loading)
    
    assert result.takeoff_cg.within_envelope is True
    assert result.landing_cg.within_envelope is False
    assert result.cg_migration_warning is not None
```

### 3. "Boundary Breach" (H-11)
```python
@pytest.mark.p1
@pytest.mark.safety
def test_boundary_breach_blocks_calculation():
    """
    Temperature 11% above POH maximum.
    System must block calculation entirely.
    """
    poh_max_temp = 40  # POH maximum
    test_temp = 44.5   # 11.25% above (exceeds 10% buffer)
    
    with pytest.raises(ExtrapolationBlockedException) as exc:
        performance.calculate_takeoff(
            aircraft,
            conditions=EnvironmentalConditions(temperature_c=test_temp)
        )
    
    assert "exceeds 10% extrapolation limit" in str(exc.value)
```

### 4. "Crosswind Exceedance" (H-14)
```python
@pytest.mark.p2
@pytest.mark.safety
def test_crosswind_exceedance_critical_alert():
    """
    20kt crosswind for DA40 (15kt demonstrated limit).
    Must trigger critical alert.
    """
    conditions = WindConditions(
        direction_deg=90,
        speed_kt=20
    )
    runway = Runway(heading_deg=0)  # Full crosswind
    
    result = performance.calculate_crosswind(
        aircraft=da40,
        conditions=conditions,
        runway=runway
    )
    
    assert result.crosswind_kt == 20
    assert result.exceeds_demonstrated_limit is True
    assert result.warning_level == "CRITICAL"
```

---

## Test Data Management

### Fixtures

```python
# conftest.py

@pytest.fixture
def da40_profile():
    """Standard DA40 D profile for testing."""
    return load_profile("test_data/da40_standard.json")

@pytest.fixture
def kl107_profile():
    """Klemm KL 107 B with dual certification and hull tanks."""
    return load_profile("test_data/kl107_utility.json")

@pytest.fixture
def standard_conditions():
    """ISA conditions at sea level."""
    return EnvironmentalConditions(
        temperature_c=15,
        qnh_hpa=1013.25,
        elevation_ft=0
    )
```

### Test Data Files

```
tests/
└── test_data/
    ├── profiles/
    │   ├── da40_standard.json
    │   ├── kl107_utility.json
    │   └── p2008_basic.json
    ├── poh_tables/
    │   └── da40_takeoff_table.json
    └── scenarios/
        ├── sahara_switch.json
        └── burnout_shift.json
```

---

## CI Integration

### Quality Gates in GitHub Actions

The CI workflow (`.github/workflows/ci.yml`) runs all 3 gates as separate steps:

```yaml
- name: "Gate 1: P1 Core (90%)"
  run: |
    uv run pytest \
      --cov=app/services/mass_balance/core \
      --cov=app/services/performance/core \
      --cov=app/services/units \
      --cov=app/services/cg_validation \
      --cov-fail-under=90

- name: "Gate 2: P2 Logic (80%)"
  run: |
    uv run pytest \
      --cov=app/services/mass_balance/logic \
      --cov=app/services/performance/logic \
      --cov=app/services/weather \
      --cov=app/routers \
      --cov-fail-under=80

- name: "Gate 3: P3 Global (70%)"
  run: |
    uv run pytest \
      --cov=app \
      --cov-fail-under=70
```

---

## Mocking External Services

### Weather API Mock

```python
@pytest.fixture
def mock_weather_api(mocker):
    """Mock METAR API responses."""
    return mocker.patch(
        "app.services.weather.fetch_metar",
        return_value=MetarResponse(
            icao="EDDF",
            temperature_c=25,
            qnh_hpa=1013,
            wind_direction_deg=70,
            wind_speed_kt=10
        )
    )
```

---

> Document Version: 1.0.0  
> Last Updated: 2026-02-03
