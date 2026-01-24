"""Weather service for METAR/TAF retrieval."""

from datetime import UTC, datetime

import httpx

from app.config import get_settings
from app.schemas.weather import MetarResponse, TafResponse


class WeatherService:
    """Service for fetching and parsing weather data."""

    AVWX_BASE_URL = "https://avwx.rest/api"

    def __init__(self) -> None:
        """Initialize weather service."""
        self.settings = get_settings()

    async def get_metar(self, icao: str) -> MetarResponse:
        """Fetch and parse METAR for an airport.

        Args:
            icao: ICAO airport code (e.g., EDDF).

        Returns:
            Parsed METAR data.

        Raises:
            ValueError: If airport not found.
            Exception: If API request fails.
        """
        if not self.settings.avwx_api_key:
            # Return mock data for development
            return self._mock_metar(icao)

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.AVWX_BASE_URL}/metar/{icao}",
                headers={"Authorization": f"BEARER {self.settings.avwx_api_key}"},
                timeout=10.0,
            )

            if response.status_code == 404:
                raise ValueError(f"Airport {icao} not found")

            response.raise_for_status()
            data = response.json()

            return self._parse_metar(data)

    async def get_taf(self, icao: str) -> TafResponse:
        """Fetch and parse TAF for an airport.

        Args:
            icao: ICAO airport code.

        Returns:
            Parsed TAF data.

        Raises:
            ValueError: If airport not found.
            Exception: If API request fails.
        """
        if not self.settings.avwx_api_key:
            return self._mock_taf(icao)

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.AVWX_BASE_URL}/taf/{icao}",
                headers={"Authorization": f"BEARER {self.settings.avwx_api_key}"},
                timeout=10.0,
            )

            if response.status_code == 404:
                raise ValueError(f"Airport {icao} not found")

            response.raise_for_status()
            data = response.json()

            return self._parse_taf(data)

    def _parse_metar(self, data: dict) -> MetarResponse:
        """Parse AVWX METAR response.

        Args:
            data: Raw AVWX API response.

        Returns:
            Parsed MetarResponse.
        """
        # Parse time
        time_str = data.get("time", {}).get("dt", "")
        try:
            time = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            time = datetime.now(UTC)

        # Parse clouds
        clouds = []
        for cloud in data.get("clouds", []):
            if cloud.get("type"):
                clouds.append({
                    "cover": cloud.get("type", ""),
                    "height_ft": cloud.get("altitude", 0) * 100,  # AVWX returns hundreds of feet
                })

        return MetarResponse(
            raw=data.get("raw", ""),
            station=data.get("station", ""),
            time=time,
            wind_direction=data.get("wind_direction", {}).get("value"),
            wind_speed_kt=data.get("wind_speed", {}).get("value", 0),
            wind_gust_kt=data.get("wind_gust", {}).get("value"),
            visibility_m=self._parse_visibility(data.get("visibility", {})),
            temperature_c=data.get("temperature", {}).get("value", 0),
            dewpoint_c=data.get("dewpoint", {}).get("value", 0),
            qnh_hpa=data.get("altimeter", {}).get("value", 1013),
            clouds=clouds,
        )

    def _parse_taf(self, data: dict) -> TafResponse:
        """Parse AVWX TAF response.

        Args:
            data: Raw AVWX API response.

        Returns:
            Parsed TafResponse.
        """
        # Parse times
        try:
            issued = datetime.fromisoformat(
                data.get("time", {}).get("dt", "").replace("Z", "+00:00")
            )
        except (ValueError, AttributeError):
            issued = datetime.now(UTC)

        try:
            valid_from = datetime.fromisoformat(
                data.get("start_time", {}).get("dt", "").replace("Z", "+00:00")
            )
            valid_to = datetime.fromisoformat(
                data.get("end_time", {}).get("dt", "").replace("Z", "+00:00")
            )
        except (ValueError, AttributeError):
            valid_from = issued
            valid_to = issued

        return TafResponse(
            raw=data.get("raw", ""),
            station=data.get("station", ""),
            issued=issued,
            valid_from=valid_from,
            valid_to=valid_to,
            forecasts=data.get("forecast", []),
        )

    def _parse_visibility(self, visibility_data: dict) -> int:
        """Parse visibility to meters.

        Args:
            visibility_data: AVWX visibility object.

        Returns:
            Visibility in meters.
        """
        value = visibility_data.get("value", 9999)
        units = visibility_data.get("units", "m")

        if units == "sm":  # Statute miles
            return int(value * 1609.34)
        return int(value)

    def _mock_metar(self, icao: str) -> MetarResponse:
        """Return mock METAR for development.

        Args:
            icao: ICAO airport code.

        Returns:
            Mock MetarResponse.
        """
        return MetarResponse(
            raw=f"{icao} 201350Z 27008KT 9999 FEW040 12/04 Q1023",
            station=icao,
            time=datetime.now(UTC),
            wind_direction=270,
            wind_speed_kt=8,
            wind_gust_kt=None,
            visibility_m=9999,
            temperature_c=12,
            dewpoint_c=4,
            qnh_hpa=1023,
            clouds=[{"cover": "FEW", "height_ft": 4000}],
        )

    def _mock_taf(self, icao: str) -> TafResponse:
        """Return mock TAF for development.

        Args:
            icao: ICAO airport code.

        Returns:
            Mock TafResponse.
        """
        now = datetime.now(UTC)
        return TafResponse(
            raw=f"{icao} 201100Z 2012/2112 27010KT 9999 FEW040",
            station=icao,
            issued=now,
            valid_from=now,
            valid_to=now,
            forecasts=[],
        )
