"""Integration tests for Aircraft API."""



class TestAircraftAPI:
    """Integration tests for Aircraft CRUD endpoints."""

    def test_list_aircraft_empty(self, client):
        """Test listing aircraft when database is empty."""
        response = client.get("/api/v1/aircraft/")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_aircraft(self, client, sample_aircraft_data):
        """Test creating a new aircraft."""
        response = client.post("/api/v1/aircraft/", json=sample_aircraft_data)
        assert response.status_code == 201

        data = response.json()
        assert data["registration"] == "D-EABC"
        assert data["manufacturer"] == "Cessna"
        assert data["mtow_kg"] == 1157.0
        assert "id" in data

    def test_create_duplicate_registration(self, client, sample_aircraft_data):
        """Test that duplicate registration is rejected."""
        # Create first aircraft
        client.post("/api/v1/aircraft/", json=sample_aircraft_data)

        # Try to create duplicate
        response = client.post("/api/v1/aircraft/", json=sample_aircraft_data)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_get_aircraft_by_id(self, client, sample_aircraft_data):
        """Test getting aircraft by ID."""
        # Create aircraft
        create_response = client.post("/api/v1/aircraft/", json=sample_aircraft_data)
        aircraft_id = create_response.json()["id"]

        # Get by ID
        response = client.get(f"/api/v1/aircraft/{aircraft_id}")
        assert response.status_code == 200
        assert response.json()["registration"] == "D-EABC"

    def test_get_aircraft_not_found(self, client):
        """Test 404 when aircraft not found."""
        response = client.get("/api/v1/aircraft/999")
        assert response.status_code == 404

    def test_update_aircraft(self, client, sample_aircraft_data):
        """Test updating an aircraft."""
        # Create aircraft
        create_response = client.post("/api/v1/aircraft/", json=sample_aircraft_data)
        aircraft_id = create_response.json()["id"]

        # Update
        update_data = {"mtow_kg": 1200.0}
        response = client.put(f"/api/v1/aircraft/{aircraft_id}", json=update_data)
        assert response.status_code == 200
        assert response.json()["mtow_kg"] == 1200.0

    def test_delete_aircraft(self, client, sample_aircraft_data):
        """Test deleting an aircraft."""
        # Create aircraft
        create_response = client.post("/api/v1/aircraft/", json=sample_aircraft_data)
        aircraft_id = create_response.json()["id"]

        # Delete
        response = client.delete(f"/api/v1/aircraft/{aircraft_id}")
        assert response.status_code == 204

        # Verify deleted
        get_response = client.get(f"/api/v1/aircraft/{aircraft_id}")
        assert get_response.status_code == 404

    def test_create_aircraft_with_stations(
        self, client, sample_aircraft_data, sample_weight_stations
    ):
        """Test creating aircraft with weight stations."""
        sample_aircraft_data["weight_stations"] = sample_weight_stations

        response = client.post("/api/v1/aircraft/", json=sample_aircraft_data)
        assert response.status_code == 201

        # Get full details
        aircraft_id = response.json()["id"]
        detail_response = client.get(f"/api/v1/aircraft/{aircraft_id}")
        assert detail_response.status_code == 200

        data = detail_response.json()
        assert len(data["weight_stations"]) == 4

    def test_create_aircraft_with_envelope(
        self, client, sample_aircraft_data, sample_cg_envelope
    ):
        """Test creating aircraft with CG envelope."""
        sample_aircraft_data["cg_envelopes"] = [sample_cg_envelope]

        response = client.post("/api/v1/aircraft/", json=sample_aircraft_data)
        assert response.status_code == 201

        # Get full details
        aircraft_id = response.json()["id"]
        detail_response = client.get(f"/api/v1/aircraft/{aircraft_id}")
        assert detail_response.status_code == 200

        data = detail_response.json()
        assert len(data["cg_envelopes"]) == 1
        assert data["cg_envelopes"][0]["category"] == "normal"
