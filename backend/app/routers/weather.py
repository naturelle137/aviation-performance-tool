"""Weather data endpoints (METAR/TAF)."""

from fastapi import APIRouter, HTTPException, status

from app.schemas.weather import MetarResponse, TafResponse
from app.services.weather import WeatherService

router = APIRouter()


@router.get("/metar/{icao}", response_model=MetarResponse)
async def get_metar(icao: str) -> MetarResponse:
    """Get current METAR for an airport."""
    service = WeatherService()

    try:
        metar = await service.get_metar(icao.upper())
        return metar
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Weather service unavailable: {e}",
        )


@router.get("/taf/{icao}", response_model=TafResponse)
async def get_taf(icao: str) -> TafResponse:
    """Get TAF forecast for an airport."""
    service = WeatherService()

    try:
        taf = await service.get_taf(icao.upper())
        return taf
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Weather service unavailable: {e}",
        )
