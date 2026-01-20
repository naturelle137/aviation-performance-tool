"""Pydantic schemas package."""

from app.schemas.aircraft import (
    AircraftCreate,
    AircraftResponse,
    AircraftUpdate,
    AircraftWithDetails,
    CGEnvelopeCreate,
    CGEnvelopeResponse,
    WeightStationCreate,
    WeightStationResponse,
)
from app.schemas.calculation import (
    MassBalanceRequest,
    MassBalanceResponse,
    PerformanceRequest,
    PerformanceResponse,
)
from app.schemas.weather import MetarResponse, TafResponse

__all__ = [
    "AircraftCreate",
    "AircraftResponse",
    "AircraftUpdate",
    "AircraftWithDetails",
    "WeightStationCreate",
    "WeightStationResponse",
    "CGEnvelopeCreate",
    "CGEnvelopeResponse",
    "MassBalanceRequest",
    "MassBalanceResponse",
    "PerformanceRequest",
    "PerformanceResponse",
    "MetarResponse",
    "TafResponse",
]
