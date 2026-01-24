"""Unit tests for Aircraft models and schemas.

Verifies validation logic, multi-tank support, and branded unit integration.
"""

import pytest
from pydantic import ValidationError
from app.schemas.aircraft import AircraftCreate, FuelTankCreate, WeightStationCreate
from app.models.aircraft import FuelType
from app.services.units import Kilogram, Liter, Meter

@pytest.mark.mvp
@pytest.mark.p1
@pytest.mark.safety
def test_aircraft_registration_validation():
    """Verify ICAO registration regex validation.
    
    Traceability: REQ-AC-03
    """
    # Valid German registration
    ac = AircraftCreate(
        registration="D-EBPF",
        aircraft_type="DA40",
        manufacturer="Diamond",
        empty_weight_kg=Kilogram(750),
        empty_arm_m=Meter(2.4),
        mtow_kg=Kilogram(1150),
        fuel_tanks=[]
    )
    assert ac.registration == "D-EBPF"

    # Valid US registration (no dash)
    ac_us = AircraftCreate(
        registration="N12345",
        aircraft_type="C172",
        manufacturer="Cessna",
        empty_weight_kg=Kilogram(750),
        empty_arm_m=Meter(2.4),
        mtow_kg=Kilogram(1150),
        fuel_tanks=[]
    )
    assert ac_us.registration == "N12345"

    # Invalid registrations
    invalid_regs = ["D-", "TOO-LONG-REG", "invalid!"]
    for reg in invalid_regs:
        with pytest.raises(ValidationError):
            AircraftCreate(
                registration=reg,
                aircraft_type="DA40",
                manufacturer="Diamond",
                empty_weight_kg=750,
                empty_arm_m=2.4,
                mtow_kg=1150,
                fuel_tanks=[]
            )

@pytest.mark.mvp
@pytest.mark.p1
@pytest.mark.safety
def test_branded_units_in_schema():
    """Verify that branded unit types are correctly validated in schemas.
    
    Traceability: REQ-SYS-03, H-01
    """
    # Implicit conversion from float
    ac = AircraftCreate(
        registration="D-EBPF",
        aircraft_type="DA40",
        manufacturer="Diamond",
        empty_weight_kg=750.5,  # float input
        empty_arm_m=2.40,
        mtow_kg=1200.0,
        fuel_tanks=[]
    )
    assert isinstance(ac.empty_weight_kg, Kilogram)
    assert ac.empty_weight_kg == 750.5

    # Negative values should fail (gt=0)
    with pytest.raises(ValidationError):
        AircraftCreate(
            registration="D-EBPF",
            aircraft_type="DA40",
            manufacturer="Diamond",
            empty_weight_kg=-10,
            empty_arm_m=2.4,
            mtow_kg=1150
        )

@pytest.mark.mvp
@pytest.mark.p1
@pytest.mark.safety
def test_multi_tank_creation():
    """Verify nested fuel tank creation in AircraftCreate.
    
    Traceability: REQ-AD-02, REQ-AD-08
    """
    tank1 = FuelTankCreate(
        name="Main",
        capacity_l=Liter(100),
        arm_m=Meter(2.4),
        fuel_type=FuelType.AVGAS_100LL
    )
    tank2 = FuelTankCreate(
        name="Aux",
        capacity_l=Liter(50),
        arm_m=Meter(2.6),
        fuel_type=FuelType.AVGAS_100LL
    )
    
    ac = AircraftCreate(
        registration="D-EBPF",
        aircraft_type="DA40",
        manufacturer="Diamond",
        empty_weight_kg=750,
        empty_arm_m=2.4,
        mtow_kg=1150,
        fuel_tanks=[tank1, tank2]
    )
    
    assert len(ac.fuel_tanks) == 2
    assert ac.fuel_tanks[0].name == "Main"
    assert isinstance(ac.fuel_tanks[0].capacity_l, Liter)
