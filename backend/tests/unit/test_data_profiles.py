"""Tests for Aircraft data profiles and loader."""

import pytest

from app.utils.data_loader import get_profile_path, load_aircraft_profile


@pytest.mark.mvp
@pytest.mark.p1
@pytest.mark.safety
def test_da40_ng_profile_validity():
    """Verify that the DA40 NG profile file is schema-compliant."""
    path = get_profile_path("da40_ng.json")
    profile = load_aircraft_profile(path)

    assert profile.registration == "D-EBXX"
    assert profile.aircraft_type == "DA40"
    assert profile.mtow_kg == 1310.0

    # Check stations
    front_seats = next(s for s in profile.weight_stations if s.name == "Front Seats")
    assert front_seats.arm_m == 2.30
    assert front_seats.max_weight_kg == 190.0

    # Check tanks
    main_tank = profile.fuel_tanks[0]
    assert main_tank.fuel_type.value == "Jet A-1"
    assert main_tank.capacity_l == 147.6

    # Check envelope
    assert len(profile.cg_envelopes[0].polygon_points) >= 6
