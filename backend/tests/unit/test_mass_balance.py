"""Unit tests for the Mass & Balance Service."""

import pytest

from app.models.aircraft import Aircraft, CGEnvelope, FuelTank, FuelType, WeightStation
from app.schemas.calculation import FuelInput, WeightInput
from app.services.mass_balance import MassBalanceService
from app.services.units import Kilogram, Liter, Meter


@pytest.fixture
def mock_aircraft():
    """Create a mock aircraft for M&B testing."""
    # DA40-like configuration
    ac = Aircraft(
        registration="D-EBPF",
        aircraft_type="DA40",
        manufacturer="Diamond",
        empty_weight_kg=Kilogram(750),
        empty_arm_m=Meter(2.4),
        mtow_kg=Kilogram(1150)
    )

    # Fuel Tanks (Two tanks to test sequential burn)
    ac.fuel_tanks = [
        FuelTank(name="Main", capacity_l=Liter(100), arm_m=Meter(2.45), fuel_type=FuelType.AVGAS_100LL),
        FuelTank(name="Aux", capacity_l=Liter(50), arm_m=Meter(2.65), fuel_type=FuelType.AVGAS_100LL)
    ]

    # Weight Stations
    ac.weight_stations = [
        WeightStation(name="Pilot", arm_m=Meter(2.35), sort_order=0),
        WeightStation(name="Baggage", arm_m=Meter(3.10), sort_order=1)
    ]

    # Simple CG Envelope
    ac.cg_envelopes = [
        CGEnvelope(
            category="normal",
            polygon_points=[
                {"weight_kg": 600, "arm_m": 2.30},
                {"weight_kg": 1150, "arm_m": 2.35},
                {"weight_kg": 1150, "arm_m": 2.50},
                {"weight_kg": 600, "arm_m": 2.55}
            ]
        )
    ]
    return ac

@pytest.mark.mvp
@pytest.mark.p1
@pytest.mark.safety
@pytest.mark.asyncio
async def test_mb_calculate_migration(mock_aircraft):
    """Verify CG migration calculation (Takeoff vs Landing).

    Traceability: REQ-MB-07, H-12
    """
    service = MassBalanceService(mock_aircraft)

    weights = [
        WeightInput(station_name="Pilot", weight_kg=Kilogram(80)),
        WeightInput(station_name="Baggage", weight_kg=Kilogram(20))
    ]

    # Planned fuel: 100L in Main, 20L in Aux
    fuel = [
        FuelInput(tank_name="Main", fuel_l=Liter(100)),
        FuelInput(tank_name="Aux", fuel_l=Liter(20))
    ]

    # Trip burn: 30L
    result = await service.calculate(
        weight_inputs=weights,
        fuel_inputs=fuel,
        trip_fuel_liters=Liter(30)
    )

    # 1. Verify Weights
    assert result.empty_weight_kg == 750
    assert result.payload_kg == 100
    # 120L * 0.72 = 86.4 kg fuel
    assert result.fuel_weight_kg == pytest.approx(86.4)
    assert result.takeoff_weight_kg == pytest.approx(750 + 100 + 86.4)

    # 2. Verify Migration Points
    phases = [p.label for p in result.cg_points]
    assert "Takeoff" in phases
    assert "Landing" in phases
    assert "Zero Fuel" in phases

@pytest.mark.mvp
@pytest.mark.p1
@pytest.mark.safety
@pytest.mark.asyncio
async def test_mb_sequential_burn_logic(mock_aircraft):
    """Verify that fuel is burned from Aux tank first (sequential logic).

    Aux is aft of Main, so burning it first should shift CG forward.
    """
    service = MassBalanceService(mock_aircraft)

    weights = [WeightInput(station_name="Pilot", weight_kg=Kilogram(80))]

    # 50L in Main, 50L in Aux
    fuel = [
        FuelInput(tank_name="Main", fuel_l=Liter(50)),
        FuelInput(tank_name="Aux", fuel_l=Liter(50))
    ]

    # Burn 50L (should empty Aux)
    result = await service.calculate(
        weights,
        fuel_inputs=fuel,
        trip_fuel_liters=Liter(50)
    )

    to_point = next(p for p in result.cg_points if p.label == "Takeoff")
    ldg_point = next(p for p in result.cg_points if p.label == "Landing")

    # Takeoff CG should be further aft than landing CG
    assert to_point.arm_m > ldg_point.arm_m

@pytest.mark.p1
@pytest.mark.asyncio
async def test_mb_chart_generation(mock_aircraft):
    """Verify chart generation logic to cover plotting code."""
    service = MassBalanceService(mock_aircraft)
    # Simple valid case
    result = await service.calculate(
        weight_inputs=[WeightInput(station_name="Pilot", weight_kg=Kilogram(80))],
        trip_fuel_liters=Liter(10)
    )
    assert result.chart_image_base64 is not None
    assert len(result.chart_image_base64) > 100

@pytest.mark.p1
@pytest.mark.asyncio
async def test_mb_validation_exceedance(mock_aircraft):
    """Test explicit MTOW exceedance warning branch."""
    service = MassBalanceService(mock_aircraft)
    # Overload: 500kg pilot
    result = await service.calculate(
        weight_inputs=[WeightInput(station_name="Pilot", weight_kg=Kilogram(500))],
        trip_fuel_liters=Liter(0)
    )
    assert not result.within_weight_limits
    assert any("exceeds MTOW" in w for w in result.warnings)

@pytest.mark.mvp
@pytest.mark.p1
@pytest.mark.safety
@pytest.mark.asyncio
async def test_hazard_h05_detection(mock_aircraft):
    """Verify detection of Landing safety hazard.

    Simulation: Aircraft loaded heavy aft (Baggage) so that ZFW/Landing is unsafe,
    but Fuel (forward of baggage) makes Takeoff safe.
    Migration: Safe -> Unsafe.
    """
    # Modify aircraft for this test to ensure robust physics
    # Move Main Tank way forward to ensure fuel pulls CG forward strongly
    mock_aircraft.fuel_tanks[0].arm_m = Meter(1.0)

    service = MassBalanceService(mock_aircraft)

    # Load aircraft heavy aft (Baggage)
    # 200kg @ 3.1m -> Huge aft moment
    weights = [WeightInput(station_name="Baggage", weight_kg=Kilogram(200))]

    # Add Fuel (Main Tank @ 1.0m)
    fuel = [FuelInput(tank_name="Main", fuel_l=Liter(100))]

    # Burn all fuel
    result = await service.calculate(
        weights,
        fuel_inputs=fuel,
        trip_fuel_liters=Liter(100)
    )

    to_point = next(p for p in result.cg_points if p.label == "Takeoff")
    ldg_point = next(p for p in result.cg_points if p.label == "Landing")

    # With fuel @ 1.0m, TO CG should be much further forward than ZFW/Ldg CG
    assert to_point.within_limits is True
    assert ldg_point.within_limits is False
    assert any("CRITICAL: CG shifts OUT OF LIMITS" in w for w in result.warnings)

@pytest.mark.p1
@pytest.mark.asyncio
async def test_unknown_station_weight(mock_aircraft):
    """Test that unknown stations default to arm=0 and do not crash."""
    service = MassBalanceService(mock_aircraft)
    result = await service.calculate(
        weight_inputs=[WeightInput(station_name="Ghost", weight_kg=Kilogram(80))]
    )
    # 80kg * 0 arm = 0 moment
    assert result.payload_kg == 80

@pytest.mark.p1
@pytest.mark.asyncio
async def test_mb_legacy_compatibility(mock_aircraft):
    service = MassBalanceService(mock_aircraft)
    result = await service.calculate(
        weight_inputs=[],
        fuel_liters_legacy=100.0
    )
    # 100L * 0.72 = 72kg
    assert result.fuel_weight_kg == 72.0

@pytest.mark.p1
@pytest.mark.asyncio
async def test_mb_legacy_no_tanks(mock_aircraft):
    """Test legacy input with no tanks defined (should ignore fuel)."""
    mock_aircraft.fuel_tanks = []
    service = MassBalanceService(mock_aircraft)
    result = await service.calculate(
        weight_inputs=[],
        fuel_liters_legacy=100.0
    )
    assert result.fuel_weight_kg == 0


@pytest.mark.p1
@pytest.mark.asyncio
async def test_chart_generation_edge_cases(mock_aircraft):
    """Test chart generation with no envelope and exception handling."""
    from unittest.mock import patch

    # Case 1: No Envelope (Polygon Points missing)
    mock_aircraft.cg_envelopes = []
    service = MassBalanceService(mock_aircraft)
    res = await service.calculate([], trip_fuel_liters=Liter(0))
    assert res.chart_image_base64 is not None # Should still generate plot points

    # Case 2: Exception during plotting
    with patch("app.services.mass_balance.plt.subplots", side_effect=Exception("Boom")):
        res_fail = await service.calculate([], trip_fuel_liters=Liter(0))
        assert res_fail.chart_image_base64 is None



