"""Unit tests for Mass Balance service."""

import pytest
from unittest.mock import MagicMock

from app.services.mass_balance import MassBalanceService
from app.schemas.calculation import WeightInput


class TestMassBalanceService:
    """Tests for MassBalanceService."""

    @pytest.fixture
    def mock_aircraft(self):
        """Create a mock aircraft for testing."""
        aircraft = MagicMock()
        aircraft.registration = "D-EABC"
        aircraft.empty_weight_kg = 743.0
        aircraft.empty_arm_m = 2.35
        aircraft.mtow_kg = 1157.0
        aircraft.max_landing_weight_kg = 1157.0
        aircraft.fuel_capacity_l = 200.0
        aircraft.fuel_arm_m = 2.40
        aircraft.fuel_density_kg_l = 0.72
        aircraft.weight_stations = []
        aircraft.cg_envelopes = []
        return aircraft

    def test_calculate_basic(self, mock_aircraft):
        """Test basic M&B calculation."""
        service = MassBalanceService(mock_aircraft)

        result = service.calculate(
            weight_inputs=[],
            fuel_liters=100.0,
            trip_fuel_liters=50.0,
        )

        # Check fuel weight calculation
        expected_fuel_weight = 100.0 * 0.72
        assert result.fuel_weight_kg == expected_fuel_weight

        # Check takeoff weight
        expected_takeoff = 743.0 + expected_fuel_weight
        assert result.takeoff_weight_kg == expected_takeoff

        # Check landing weight
        expected_landing = expected_takeoff - (50.0 * 0.72)
        assert result.landing_weight_kg == expected_landing

    def test_calculate_with_payload(self, mock_aircraft):
        """Test M&B calculation with payload."""
        # Add a weight station
        station = MagicMock()
        station.name = "Pilot"
        station.arm_m = 2.35
        station.max_weight_kg = 110.0
        mock_aircraft.weight_stations = [station]

        service = MassBalanceService(mock_aircraft)

        result = service.calculate(
            weight_inputs=[WeightInput(station_name="Pilot", weight_kg=85.0)],
            fuel_liters=100.0,
            trip_fuel_liters=0,
        )

        assert result.payload_kg == 85.0
        assert result.takeoff_weight_kg == 743.0 + 85.0 + (100.0 * 0.72)

    def test_mtow_exceeded_warning(self, mock_aircraft):
        """Test that warning is generated when MTOW exceeded."""
        mock_aircraft.mtow_kg = 800.0  # Set low MTOW

        service = MassBalanceService(mock_aircraft)

        result = service.calculate(
            weight_inputs=[],
            fuel_liters=100.0,
            trip_fuel_liters=0,
        )

        assert not result.within_weight_limits
        assert any("exceeds MTOW" in w for w in result.warnings)

    def test_cg_points_created(self, mock_aircraft):
        """Test that takeoff and landing CG points are created."""
        service = MassBalanceService(mock_aircraft)

        result = service.calculate(
            weight_inputs=[],
            fuel_liters=100.0,
            trip_fuel_liters=50.0,
        )

        assert len(result.cg_points) == 2
        assert result.cg_points[0].label == "Takeoff"
        assert result.cg_points[1].label == "Landing"

    def test_station_max_weight_warning(self, mock_aircraft):
        """Test warning when station max weight exceeded."""
        station = MagicMock()
        station.name = "Pilot"
        station.arm_m = 2.35
        station.max_weight_kg = 80.0  # Low max
        mock_aircraft.weight_stations = [station]

        service = MassBalanceService(mock_aircraft)

        result = service.calculate(
            weight_inputs=[WeightInput(station_name="Pilot", weight_kg=100.0)],
            fuel_liters=50.0,
            trip_fuel_liters=0,
        )

        assert any("exceeds maximum" in w for w in result.warnings)
