"""Integration tests for Aircraft CRUD API with high-fidelity profiles."""

import pytest
from app.utils.data_loader import load_aircraft_profile, get_profile_path

class TestAircraftCRUD:
    """Integration tests for aircraft management."""

    def test_create_da40_ng_full_profile(self, client):
        """Verify that the DA40 NG profile can be created via API with all nested data."""
        path = get_profile_path("da40_ng.json")
        profile_data = load_aircraft_profile(path).model_dump()
        
        # 1. Create
        res = client.post("/api/v1/aircraft/", json=profile_data)
        assert res.status_code == 201
        aircraft_id = res.json()["id"]
        
        # 2. Verify Details
        detail_res = client.get(f"/api/v1/aircraft/{aircraft_id}")
        assert detail_res.status_code == 200
        data = detail_res.json()
        
        assert data["registration"] == "D-EBXX"
        assert len(data["weight_stations"]) == 3
        assert len(data["fuel_tanks"]) == 1
        assert len(data["cg_envelopes"]) == 1
        assert data["performance_source"] == "manufacturer"

    def test_aircraft_update_performance_source(self, client, sample_aircraft_data):
        """Verify that performance source can be updated."""
        res = client.post("/api/v1/aircraft/", json=sample_aircraft_data)
        aircraft_id = res.json()["id"]
        
        # Update source
        update_data = {"performance_source": "fsm375"}
        put_res = client.put(f"/api/v1/aircraft/{aircraft_id}", json=update_data)
        assert put_res.status_code == 200
        assert put_res.json()["performance_source"] == "fsm375"

    def test_duplicate_registration_error(self, client, sample_aircraft_data):
        """Verify 400 error on duplicate registration."""
        client.post("/api/v1/aircraft/", json=sample_aircraft_data)
        res = client.post("/api/v1/aircraft/", json=sample_aircraft_data)
        assert res.status_code == 400
        assert "already exists" in res.json()["detail"]
