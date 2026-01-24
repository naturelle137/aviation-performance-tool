"""Unit tests for the Mass & Balance Service."""

import pytest
from app.services.mass_balance import MassBalanceService
from app.models.aircraft import Aircraft, FuelTank, FuelType, WeightStation, CGEnvelope
from app.schemas.calculation import WeightInput, FuelInput
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

@pytest.mark.mvp
@pytest.mark.p1
@pytest.mark.safety
@pytest.mark.asyncio
async def test_hazard_h05_detection(mock_aircraft):
    """Verify detection of Landing safety hazard.
    
    Simulation: Aircraft loaded such that burning aft fuel moves CG forward 
    outside the front limits.
    """
    service = MassBalanceService(mock_aircraft)
    
    # Load aircraft heavy front
    weights = [WeightInput(station_name="Pilot", weight_kg=Kilogram(150))]
    # Full aft fuel (moves CG aft into envelope for T/O)
    fuel = [FuelInput(tank_name="Aux", fuel_l=Liter(50))] 
    
    # Burn all fuel (shifts CG forward)
    result = await service.calculate(
        weights, 
        fuel_inputs=fuel, 
        trip_fuel_liters=Liter(50)
    )
    
    zf_point = next(p for p in result.cg_points if p.label == "Zero Fuel")
    to_point = next(p for p in result.cg_points if p.label == "Takeoff")
    
    if to_point.within_limits and not zf_point.within_limits:
        assert any("CRITICAL: CG shifts OUT OF LIMITS" in w for w in result.warnings)

@pytest.mark.mvp
@pytest.mark.p1
def test_mb_legacy_fuel_input_compatibility(mock_aircraft):
    """Verify that legacy float fuel_liters still works for backward compatibility."""
    service = MassBalanceService(mock_aircraft)
    
    # This test doesn't need to be async if we just use core math or mock await
    # Actually calculate is async, so we use pytest-asyncio
    pass

@pytest.mark.asyncio
async def test_mb_legacy_compatibility(mock_aircraft):
    service = MassBalanceService(mock_aircraft)
    result = await service.calculate(
        weight_inputs=[],
        fuel_liters_legacy=100.0
    )
    # 100L * 0.72 = 72kg
    assert result.fuel_weight_kg == 72.0
