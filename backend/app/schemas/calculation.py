from typing import Literal

from pydantic import BaseModel, Field

from app.services.units import Celsius, Feet, Kilogram, Knot, Liter, Meter


class WeightInput(BaseModel):
    """Weight input for a specific station."""

    station_name: str = Field(..., examples=["Pilot"])
    weight_kg: Kilogram = Field(..., ge=0, examples=[85.0])


class CGPoint(BaseModel):
    """A point on the CG diagram."""

    label: str = Field(..., examples=["Takeoff"])
    weight_kg: Kilogram = Field(..., examples=[1050.0])
    arm_m: Meter = Field(..., examples=[2.38])
    moment_kg_m: float = Field(..., examples=[2499.0])
    within_limits: bool = Field(..., examples=[True])


class FuelInput(BaseModel):
    """Fuel quantity input for a specific tank."""

    tank_name: str = Field(..., examples=["Main Tank"])
    fuel_l: Liter = Field(..., ge=0, examples=[50.0])


class MassBalanceRequest(BaseModel):
    """Request schema for mass balance calculation."""

    aircraft_id: int = Field(..., examples=[1])
    weight_inputs: list[WeightInput] = Field(..., min_length=1)
    # Support both backward compatibility (float) and multi-tank (list)
    fuel_tanks: list[FuelInput] | None = Field(None, description="Detailed per-tank fuel loading")
    fuel_liters: float | None = Field(None, ge=0, examples=[150.0], description="DEPRECATED: Use fuel_tanks")
    trip_fuel_liters: Liter = Field(default=Liter(0), ge=0, examples=[50.0])


class MassBalanceResponse(BaseModel):
    """Response schema for mass balance calculation."""

    # Weight summary
    empty_weight_kg: Kilogram
    payload_kg: Kilogram
    fuel_weight_kg: Kilogram
    takeoff_weight_kg: Kilogram
    landing_weight_kg: Kilogram
    zero_fuel_weight_kg: Kilogram

    # CG positions
    cg_points: list[CGPoint]

    # Limits check
    within_weight_limits: bool
    within_cg_limits: bool
    warnings: list[str] = []

    # Chart data (base64 encoded image)
    chart_image_base64: str | None = None


class PerformanceRequest(BaseModel):
    """Request schema for performance calculation."""

    aircraft_id: int = Field(..., examples=[1])
    weight_kg: Kilogram = Field(..., gt=0, examples=[1050.0])
    pressure_altitude_ft: Feet = Field(..., examples=[2000.0])
    temperature_c: Celsius = Field(..., examples=[25.0])
    wind_component_kt: Knot = Field(default=Knot(0), examples=[-5.0])  # negative = headwind
    runway_condition: Literal["dry", "wet", "grass"] = Field(default="dry")
    runway_slope_percent: float = Field(default=0, ge=-3, le=3)


class PerformanceResponse(BaseModel):
    """Response schema for performance calculation."""

    # Atmosphere
    density_altitude_ft: Feet

    # Takeoff
    takeoff_ground_roll_m: Meter
    takeoff_distance_50ft_m: Meter
    takeoff_ground_roll_raw_m: Meter | None = None
    takeoff_distance_50ft_raw_m: Meter | None = None

    # Landing
    landing_ground_roll_m: Meter
    landing_distance_50ft_m: Meter
    landing_ground_roll_raw_m: Meter | None = None
    landing_distance_50ft_raw_m: Meter | None = None

    # Climb
    rate_of_climb_fpm: Feet | None = None

    # Corrections applied
    corrections_applied: list[str] = []

    # Source of data
    calculation_source: str  # fsm375, poh, custom

    # Warnings
    warnings: list[str] = []
