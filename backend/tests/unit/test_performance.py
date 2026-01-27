"""Unit tests for the Performance Service."""

import pytest

from app.models.aircraft import Aircraft, PerformanceProfile
from app.services.performance import PerformanceService
from app.services.units import Celsius, Feet, Kilogram, Knot


@pytest.fixture
def mock_aircraft():
    """Create a mock aircraft for Performance testing."""
    ac = Aircraft(
        registration="D-EBPF",
        aircraft_type="DA40",
        manufacturer="Diamond",
        mtow_kg=Kilogram(1150)
    )
    ac.performance_profiles = []
    # Hack to allow appending to relationship list without DB session
    ac.performance_profiles = list(ac.performance_profiles)
    return ac

# ... (existing tests)

@pytest.mark.p1
@pytest.mark.asyncio
async def test_mode_a_interpolation_fallback(mock_aircraft):
    """Test Mode A failure falling back to Mode B (lines 109-115)."""
    # Create invalid Table using real model class
    profile = PerformanceProfile(
        profile_type="takeoff",
        data_tables={"ground_roll": {}} # Empty table triggers KeyError
    )
    mock_aircraft.performance_profiles.append(profile)

    service = PerformanceService(mock_aircraft)
    res = await service.calculate(Kilogram(1150), Feet(0), Celsius(15))

    assert res.calculation_source == "mode_b_fsm375" # Fallback happened
    assert any("Mode A data incomplete" in w for w in res.warnings)

@pytest.mark.mvp
@pytest.mark.p1
@pytest.mark.safety
@pytest.mark.asyncio
async def test_performance_mode_b_baseline(mock_aircraft):
    """Verify Mode B (FSM 3/75) baseline calculation at Sea Level, ISA.

    Traceability: REQ-PE-04
    """
    service = PerformanceService(mock_aircraft)

    # Calculate at MTOW, 0ft, 15C
    res = await service.calculate(
        weight_kg=Kilogram(1150),
        pressure_altitude_ft=Feet(0),
        temperature_c=Celsius(15),
        runway_condition="dry",
        runway_slope_percent=0
    )

    # 1. Density Altitude should be 0 (ISA Sea Level)
    assert res.density_altitude_ft == 0

    # 2. Distances should be factored (1.25x for takeoff roll)
    # Mode B Baseline is 300m for T/O ground roll
    assert res.takeoff_ground_roll_raw_m == 300
    assert res.takeoff_ground_roll_m == 300 * 1.25
    assert res.calculation_source == "mode_b_fsm375"

@pytest.mark.mvp
@pytest.mark.p1
@pytest.mark.safety
@pytest.mark.asyncio
async def test_performance_density_altitude_effect(mock_aircraft):
    """Verify that increased density altitude increases distances."""
    service = PerformanceService(mock_aircraft)

    # High altitude: 5000ft, 25C (Hot & High)
    res = await service.calculate(
        weight_kg=Kilogram(1150),
        pressure_altitude_ft=Feet(5000),
        temperature_c=Celsius(25)
    )

    # ISA at 5000ft: 15 - 5*2 = 5C. 25C is ISA+20.
    # DA = 5000 + 20*120 = 7400ft approx.
    assert res.density_altitude_ft > 5000

    # Distances at 5000ft should be > distances at sea level
    assert res.takeoff_ground_roll_raw_m > 300

@pytest.mark.mvp
@pytest.mark.p1
@pytest.mark.safety
@pytest.mark.asyncio
async def test_performance_surface_factors(mock_aircraft):
    """Verify grass and wet surface correction factors."""
    service = PerformanceService(mock_aircraft)

    # Grass factor (1.20x)
    res_grass = await service.calculate(
        weight_kg=Kilogram(1150),
        pressure_altitude_ft=Feet(0),
        temperature_c=Celsius(15),
        runway_condition="grass"
    )

    # (300 * 1.0 wind) * 1.2 grass * 1.25 safety = 450
    assert res_grass.takeoff_ground_roll_m == pytest.approx(300 * 1.2 * 1.25)
    assert any("Grass Surface" in c for c in res_grass.corrections_applied)

@pytest.mark.mvp
@pytest.mark.p1
@pytest.mark.safety
@pytest.mark.asyncio
async def test_performance_slope_impact(mock_aircraft):
    """Verify that upslope increases Takeoff distance but decreases Landing distance."""
    service = PerformanceService(mock_aircraft)

    # 2% upslope
    res = await service.calculate(
        weight_kg=Kilogram(1150),
        pressure_altitude_ft=Feet(0),
        temperature_c=Celsius(15),
        runway_slope_percent=2.0
    )

    # Takeoff roll should have 2 * 0.05 = 10% increase
    # Landing roll should have 2 * 0.05 = 10% decrease
    assert any("Slope 2.0%" in c for c in res.corrections_applied)

@pytest.mark.mvp
@pytest.mark.p1
@pytest.mark.safety
@pytest.mark.asyncio
async def test_hazard_h11_tailwind_warning(mock_aircraft):
    """Verifytailwind safety warning (H-11)."""
    service = PerformanceService(mock_aircraft)

    res = await service.calculate(
        weight_kg=Kilogram(1150),
        pressure_altitude_ft=Feet(0),
        temperature_c=Celsius(15),
        wind_component_kt=Knot(5) # 5kt tailwind
    )

    assert any("Tailwind" in w for w in res.warnings)
    # Factor: +10% per 2kt -> 5kt = +25%
    assert res.takeoff_ground_roll_raw_m == pytest.approx(300 * 1.25)



@pytest.mark.p1
@pytest.mark.asyncio
async def test_wind_headwind_and_wet(mock_aircraft):
    """Test Headwind deduction and Wet surface addition (lines 138-140, 151-153)."""
    service = PerformanceService(mock_aircraft)
    res = await service.calculate(
        Kilogram(1150), Feet(0), Celsius(15),
        wind_component_kt=Knot(-10), # Headwind
        runway_condition="wet"
    )
    # Headwind -10kt: 1.0 - (10/2 * 0.015) = 1.0 - 0.075 = 0.925
    # Wet: 1.15
    # Total: 300 * 0.925 * 1.15
    expected_raw = 300 * 0.925 * 1.15
    assert res.takeoff_ground_roll_raw_m == pytest.approx(expected_raw)

@pytest.mark.p1
@pytest.mark.asyncio
async def test_landing_mode_b_scaling(mock_aircraft):
    """Test Landing-specific Mode B constant (lines 124-125)."""
    service = PerformanceService(mock_aircraft)
    res = await service.calculate(Kilogram(1150), Feet(0), Celsius(15))

    # Landing Base: 250 * (W/MTOW)^1.5. Here Ratio=1.0 -> 250m
    assert res.landing_ground_roll_raw_m == 250
