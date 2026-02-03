from unittest.mock import AsyncMock, patch

import pytest
from httpx import Request, Response

from app.config import Settings
from app.services.weather import WeatherService


@pytest.fixture
def weather_service(monkeypatch):
    """Fixture for WeatherService with active API key."""
    def mock_get_settings():
        return Settings(avwx_api_key="dummy_key")

    monkeypatch.setattr("app.services.weather.get_settings", mock_get_settings)
    return WeatherService()

@pytest.mark.p1
@pytest.mark.asyncio
async def test_get_metar_parsing(weather_service):
    """Test parsing of a real-like METAR response from AVWX."""
    icao = "EDDF"
    mock_data = {
        "raw": "EDDF 271020Z 20006KT 9999 FEW030 14/08 Q1018 NOSIG",
        "station": "EDDF",
        "time": {"dt": "2023-10-27T10:20:00Z"},
        "wind_direction": {"value": 200},
        "wind_speed": {"value": 6},
        "wind_gust": {"value": None},
        "visibility": {"value": 9999, "units": "m"},
        "temperature": {"value": 14},
        "dewpoint": {"value": 8},
        "altimeter": {"value": 1018},
        "clouds": [{"type": "FEW", "altitude": 30}]
    }

    mock_client = AsyncMock()
    request = Request("GET", f"https://avwx.rest/api/metar/{icao}")
    mock_client.get.return_value = Response(200, json=mock_data, request=request)
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with patch("httpx.AsyncClient", return_value=mock_client):
        metar = await weather_service.get_metar(icao)

        assert metar.station == "EDDF"
        assert metar.wind_direction == 200
        assert metar.temperature_c == 14
        assert metar.qnh_hpa == 1018
        assert metar.clouds[0]["height_ft"] == 3000

@pytest.mark.p1
@pytest.mark.asyncio
async def test_get_taf_parsing(weather_service):
    """Test parsing of a real-like TAF response from AVWX."""
    icao = "EDDF"
    mock_data = {
        "raw": "TAF EDDF ...",
        "station": "EDDF",
        "time": {"dt": "2023-10-27T10:20:00Z"},
        "start_time": {"dt": "2023-10-27T12:00:00Z"},
        "end_time": {"dt": "2023-10-28T12:00:00Z"},
        "forecast": []
    }

    mock_client = AsyncMock()
    request = Request("GET", f"https://avwx.rest/api/taf/{icao}")
    mock_client.get.return_value = Response(200, json=mock_data, request=request)
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with patch("httpx.AsyncClient", return_value=mock_client):
        taf = await weather_service.get_taf(icao)

        assert taf.station == "EDDF"
        assert taf.valid_from.year == 2023

@pytest.mark.p1
@pytest.mark.asyncio
async def test_parse_visibility_sm(weather_service):
    """Test visibility conversion from statute miles."""
    icao = "KJFK"
    mock_data = {
        "raw": "KJFK ...",
        "station": "KJFK",
        "time": {"dt": "2023-10-27T10:20:00Z"},
        "visibility": {"value": 10, "units": "sm"},
        "wind_direction": {"value": 0},
        "altimeter": {"value": 1013},
    }

    mock_client = AsyncMock()
    request = Request("GET", f"https://avwx.rest/api/metar/{icao}")
    mock_client.get.return_value = Response(200, json=mock_data, request=request)
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with patch("httpx.AsyncClient", return_value=mock_client):
        metar = await weather_service.get_metar(icao)
        # 10 sm = 16093.4 m -> 16093
        assert metar.visibility_m == 16093

@pytest.mark.p1
@pytest.mark.asyncio
async def test_api_404_error(weather_service):
    """Test 404 handling."""
    icao = "ZZZZ"

    mock_client = AsyncMock()
    request = Request("GET", f"https://avwx.rest/api/metar/{icao}")
    mock_client.get.return_value = Response(404, request=request)
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    with patch("httpx.AsyncClient", return_value=mock_client):
        with pytest.raises(ValueError, match="Airport ZZZZ not found"):
            await weather_service.get_metar(icao)
