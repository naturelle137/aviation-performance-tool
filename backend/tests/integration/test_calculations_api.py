"""Integration tests for Calculation API (M&B and Performance)."""

import pytest

class TestCalculationAPI:
    """Integration tests for calculation endpoints."""

    def test_calculate_mass_balance_full_flow(self, client, sample_aircraft_data):
        """Test full flow of M&B calculation via API."""
        # 1. Create aircraft
        create_res = client.post("/api/v1/aircraft/", json=sample_aircraft_data)
        aircraft_id = create_res.json()["id"]
        
        # 2. Perform calculation
        payload = {
            "aircraft_id": aircraft_id,
            "weight_inputs": [
                {"station_name": "Pilot", "weight_kg": 80.0},
                {"station_name": "Baggage", "weight_kg": 20.0}
            ],
            "fuel_tanks": [
                {"tank_name": "Main", "fuel_l": 100.0}
            ],
            "trip_fuel_liters": 20.0
        }
        
        res = client.post("/api/v1/calculations/mass-balance", json=payload)
        assert res.status_code == 200
        data = res.json()
        
        assert "takeoff_weight_kg" in data
        assert "cg_points" in data
        assert len(data["cg_points"]) == 3 # Zero Fuel, Takeoff, Landing
        assert "chart_image_base64" in data

    def test_calculate_performance_mode_b(self, client, sample_aircraft_data):
        """Test performance calculation via API (Mode B fallback)."""
        # 1. Create aircraft
        create_res = client.post("/api/v1/aircraft/", json=sample_aircraft_data)
        aircraft_id = create_res.json()["id"]
        
        # 2. Perform calculation
        payload = {
            "aircraft_id": aircraft_id,
            "weight_kg": 1150.0,
            "pressure_altitude_ft": 1000.0,
            "temperature_c": 20.0,
            "wind_component_kt": -5.0, # Headwind
            "runway_condition": "grass",
            "runway_slope_percent": 1.0
        }
        
        res = client.post("/api/v1/calculations/performance", json=payload)
        assert res.status_code == 200
        data = res.json()
        
        assert data["calculation_source"] == "mode_b_fsm375"
        assert data["takeoff_ground_roll_m"] > 300 # Should be factored
        assert "Grass Surface" in str(data["corrections_applied"])

    def test_calculate_not_found(self, client):
        """Test 404 when aircraft doesn't exist."""
        payload = {
            "aircraft_id": 999,
            "weight_kg": 1000.0,
            "pressure_altitude_ft": 0,
            "temperature_c": 15
        }
        res = client.post("/api/v1/calculations/performance", json=payload)
        assert res.status_code == 404
