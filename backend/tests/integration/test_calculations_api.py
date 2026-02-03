"""Integration tests for Calculation endpoints."""

import pytest

from app.models.aircraft import Aircraft, CGEnvelope, FuelTank, WeightStation


@pytest.mark.mvp
class TestCalculationAPI:

    @pytest.fixture
    def test_aircraft(self, db_session):
        """Create a full test aircraft in DB."""
        ac = Aircraft(
            registration="D-TEST",
            aircraft_type="DA40",
            manufacturer="Diamond",
            empty_weight_kg=800,
            empty_arm_m=2.4,
            mtow_kg=1150,
            max_landing_weight_kg=1150,
            performance_source="manufacturer"
        )
        db_session.add(ac)
        db_session.commit()
        db_session.refresh(ac)

        # Stations
        stations = [
            WeightStation(aircraft_id=ac.id, name="Pilot", arm_m=2.3, max_weight_kg=110),
            WeightStation(aircraft_id=ac.id, name="Pax", arm_m=2.3, max_weight_kg=110),
        ]
        db_session.add_all(stations)

        # Tanks
        tank = FuelTank(
            aircraft_id=ac.id, name="Main", capacity_l=150, arm_m=2.6,
            unusable_fuel_l=2, fuel_type="Jet A-1"
        )
        db_session.add(tank)

        # Envelope
        env = CGEnvelope(
            aircraft_id=ac.id, category="normal",
            polygon_points=[
                {"weight_kg": 800, "arm_m": 2.3},
                {"weight_kg": 1150, "arm_m": 2.3},
                {"weight_kg": 1150, "arm_m": 2.6},
                {"weight_kg": 800, "arm_m": 2.6}
            ]
        )
        db_session.add(env)
        db_session.commit()
        return ac

    def test_mass_balance_flow(self, client, test_aircraft):
        """Test full M&B calculation via API."""
        payload = {
            "aircraft_id": test_aircraft.id,
            "weight_inputs": [
                {"station_name": "Pilot", "weight_kg": 80},
                {"station_name": "Pax", "weight_kg": 0}
            ],
            "fuel_liters": 100,
            "trip_fuel_liters": 30
        }

        res = client.post("/api/v1/calculations/mass-balance", json=payload)
        assert res.status_code == 200
        data = res.json()

        assert data["empty_weight_kg"] == 800
        assert data["takeoff_weight_kg"] > 800
        assert len(data["cg_points"]) > 0
        assert data["within_weight_limits"] is True
        assert data["within_cg_limits"] is True

    def test_performance_flow(self, client, test_aircraft):
        """Test performance calculation via API."""
        # Force Mode B (FSM) via aircraft setting locally if needed,
        # but default mocked/stubbed logic in Mode A should return valid numbers
        payload = {
            "aircraft_id": test_aircraft.id,
            "weight_kg": 1000,
            "pressure_altitude_ft": 1000,
            "temperature_c": 15,
            "wind_component_kt": 5,
            "runway_condition": "dry",
            "runway_slope_percent": 0
        }

        res = client.post("/api/v1/calculations/performance", json=payload)
        assert res.status_code == 200
        data = res.json()

        assert data["takeoff_ground_roll_m"] > 0
        assert data["landing_ground_roll_m"] > 0
