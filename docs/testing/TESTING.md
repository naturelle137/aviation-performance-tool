# Testing Documentation

## Overview

Testing for the Aviation Performance Tool follows a safety-critical approach with three testing levels aligned to requirement priorities.

---

## Test Structure

```
tests/
├── unit/                    # Fast, isolated tests
│   ├── test_mass_balance.py
│   ├── test_performance.py
│   ├── test_unit_conversion.py
│   ├── test_cg_validation.py
│   └── test_interpolation.py
├── integration/             # Component interaction tests
│   ├── test_calculation_flow.py
│   ├── test_api_endpoints.py
│   └── test_profile_management.py
└── safety/                  # Hazard-specific tests
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

### With Coverage
```bash
uv run pytest --cov=app --cov-report=html
# Open htmlcov/index.html
```

### By Priority
```bash
# P1 requirements only (Safety Critical)
uv run pytest -m "p1"

# P1 and P2 (MVP)
uv run pytest -m "p1 or p2"
```

---

## Test Markers

Use pytest markers to categorize tests:

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
```

**Available Markers**:
| Marker | Description |
|--------|-------------|
| `@pytest.mark.p1` | P1 (Safety-critical) requirement |
| `@pytest.mark.p2` | P2 (Operational) requirement |
| `@pytest.mark.p3` | P3 (Comfort) requirement |
| `@pytest.mark.safety` | Safety-specific test |
| `@pytest.mark.slow` | Long-running test |
| `@pytest.mark.integration` | Integration test |

---

## Coverage Requirements

| Priority | Target Coverage | Enforcement |
|----------|-----------------|-------------|
| P1 | 90%+ | CI blocks merge if below |
| P2 | 80%+ | CI warns if below |
| P3 | 70%+ | Advisory only |

### Per-Module Coverage

| Module | Priority | Min Coverage |
|--------|----------|--------------|
| `services/mass_balance.py` | P1 | 90% |
| `services/performance.py` | P1 | 90% |
| `services/unit_conversion.py` | P1 | **95%** (Critical H-01) |
| `services/cg_validation.py` | P1 | 90% |
| `services/weather.py` | P2 | 80% |
| `api/` | P2 | 80% |

### Frontend P1 Components (90% Threshold)

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
    
    # Either blocked or extrapolated with penalty
    if result.status == "BLOCKED":
        assert "EXTRAPOLATION_LIMIT" in result.error_code
    else:
        assert result.calculation_mode == "extrapolated"
        assert "EXTRAPOLATION_PENALTY" in [w.code for w in result.warnings]
```

### 2. "Burn-out Shift" (H-12)
```python
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

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Install uv
        run: pip install uv
      
      - name: Install dependencies
        run: cd backend && uv sync
      
      - name: Run tests
        run: cd backend && uv run pytest --cov=app --cov-fail-under=80
      
      - name: Safety tests
        run: cd backend && uv run pytest tests/safety/ -v
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

> Document Version: 0.1.0
> Last Updated: 2025-01-23
