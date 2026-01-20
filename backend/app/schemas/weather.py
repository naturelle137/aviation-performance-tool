"""Pydantic schemas for weather data."""

from datetime import datetime

from pydantic import BaseModel, Field


class MetarResponse(BaseModel):
    """Parsed METAR data."""

    raw: str = Field(..., examples=["EDDF 201350Z 27008KT 9999 FEW040 12/04 Q1023"])
    station: str = Field(..., examples=["EDDF"])
    time: datetime
    wind_direction: int | None = Field(None, examples=[270])
    wind_speed_kt: int = Field(..., examples=[8])
    wind_gust_kt: int | None = None
    visibility_m: int = Field(..., examples=[9999])
    temperature_c: int = Field(..., examples=[12])
    dewpoint_c: int = Field(..., examples=[4])
    qnh_hpa: int = Field(..., examples=[1023])
    clouds: list[dict[str, str | int]] = Field(default_factory=list)
    # e.g., [{"cover": "FEW", "height_ft": 4000}]


class TafResponse(BaseModel):
    """Parsed TAF data."""

    raw: str
    station: str
    issued: datetime
    valid_from: datetime
    valid_to: datetime
    forecasts: list[dict] = Field(default_factory=list)
