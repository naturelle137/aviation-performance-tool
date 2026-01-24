from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.aircraft import FuelType
from app.services.units import Feet, Gallon, Kilogram, Liter, Meter, Pound


class WeightStationCreate(BaseModel):
    """Schema for creating a weight station."""

    name: str = Field(..., min_length=1, max_length=50, examples=["Pilot"])
    arm_m: Meter = Field(..., gt=0, examples=[2.35])
    max_weight_kg: Kilogram | None = Field(None, gt=0, examples=[110.0])
    default_weight_kg: Kilogram | None = Field(None, ge=0, examples=[80.0])


class WeightStationResponse(WeightStationCreate):
    """Schema for weight station response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    sort_order: int


class FuelTankCreate(BaseModel):
    """Schema for creating a fuel tank."""

    name: str = Field(..., min_length=1, max_length=50, examples=["Main Tank"])
    capacity_l: Liter = Field(..., gt=0, examples=[100.0])
    arm_m: Meter = Field(..., gt=0, examples=[2.40])
    unusable_fuel_l: Liter = Field(default=0.0, ge=0, examples=[3.8])
    fuel_type: FuelType = Field(default=FuelType.AVGAS_100LL)
    default_quantity_l: Liter = Field(default=0.0, ge=0)


class FuelTankResponse(FuelTankCreate):
    """Schema for fuel tank response."""

    model_config = ConfigDict(from_attributes=True)

    id: int


class CGEnvelopeCreate(BaseModel):
    """Schema for creating a CG envelope."""

    category: str = Field(default="normal", examples=["normal", "utility"])
    polygon_points: list[dict[str, float]] = Field(
        ...,
        min_length=3,
        examples=[[{"weight_kg": 600, "arm_m": 2.0}, {"weight_kg": 800, "arm_m": 2.4}]],
    )

    @field_validator("polygon_points")
    @classmethod
    def validate_polygon_points(
        cls, v: list[dict[str, float]]
    ) -> list[dict[str, float]]:
        """Validate that polygon points have required keys."""
        for point in v:
            if "weight_kg" not in point or "arm_m" not in point:
                raise ValueError("Each point must have 'weight_kg' and 'arm_m' keys")
        return v


class CGEnvelopeResponse(CGEnvelopeCreate):
    """Schema for CG envelope response."""

    model_config = ConfigDict(from_attributes=True)

    id: int


class AircraftBase(BaseModel):
    """Base schema for aircraft data."""

    registration: str = Field(
        ..., 
        pattern=r"^[A-Z0-9]{2,10}$|^[A-Z0-9]{1,3}-[A-Z0-9]{1,5}$",
        min_length=3, 
        max_length=10, 
        examples=["D-EABC"]
    )
    aircraft_type: str = Field(..., min_length=1, max_length=50, examples=["C172S"])
    manufacturer: str = Field(..., min_length=1, max_length=50, examples=["Cessna"])

    # Weight data
    empty_weight_kg: Kilogram = Field(..., gt=0, examples=[743.0])
    empty_arm_m: Meter = Field(..., gt=0, examples=[2.35])
    mtow_kg: Kilogram = Field(..., gt=0, examples=[1157.0])
    max_landing_weight_kg: Kilogram | None = Field(None, gt=0, examples=[1157.0])
    max_ramp_weight_kg: Kilogram | None = Field(None, gt=0, examples=[1160.0])


class AircraftCreate(AircraftBase):
    """Schema for creating an aircraft."""

    weight_stations: list[WeightStationCreate] | None = None
    fuel_tanks: list[FuelTankCreate] | None = None
    cg_envelopes: list[CGEnvelopeCreate] | None = None

    @field_validator("registration")
    @classmethod
    def uppercase_registration(cls, v: str) -> str:
        """Convert registration to uppercase."""
        return v.upper()


class AircraftUpdate(BaseModel):
    """Schema for updating an aircraft (all fields optional)."""

    registration: str | None = Field(None, min_length=1, max_length=10)
    aircraft_type: str | None = Field(None, min_length=1, max_length=50)
    manufacturer: str | None = Field(None, min_length=1, max_length=50)
    empty_weight_kg: float | None = Field(None, gt=0)
    empty_arm_m: Meter | None = Field(None, gt=0)
    mtow_kg: Kilogram | None = Field(None, gt=0)
    max_landing_weight_kg: Kilogram | None = Field(None, gt=0)
    max_ramp_weight_kg: Kilogram | None = Field(None, gt=0)
    # Fuel data is updated via separate endpoints or nested in Create


class AircraftResponse(AircraftBase):
    """Schema for aircraft response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    performance_source: str
    weighing_date: datetime | None
    created_at: datetime
    updated_at: datetime


class AircraftWithDetails(AircraftResponse):
    """Schema for aircraft with all related data."""

    weight_stations: list[WeightStationResponse] = []
    fuel_tanks: list[FuelTankResponse] = []
    cg_envelopes: list[CGEnvelopeResponse] = []
