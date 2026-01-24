"""Calculation endpoints for M&B, fuel planning, and performance."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.aircraft import Aircraft
from app.schemas.calculation import (
    MassBalanceRequest,
    MassBalanceResponse,
    PerformanceRequest,
    PerformanceResponse,
)
from app.services.mass_balance import MassBalanceService
from app.services.performance import PerformanceService

router = APIRouter()


@router.post("/mass-balance", response_model=MassBalanceResponse)
async def calculate_mass_balance(
    request: MassBalanceRequest,
    db: Session = Depends(get_db),
) -> MassBalanceResponse:
    """Calculate mass and balance for a flight."""
    # Get aircraft
    aircraft = db.query(Aircraft).filter(Aircraft.id == request.aircraft_id).first()
    if not aircraft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aircraft with ID {request.aircraft_id} not found",
        )

    # Perform calculation
    service = MassBalanceService(aircraft)
    result = await service.calculate(
        weight_inputs=request.weight_inputs,
        fuel_inputs=request.fuel_tanks,
        fuel_liters_legacy=request.fuel_liters,
        trip_fuel_liters=request.trip_fuel_liters,
    )

    return result


@router.post("/performance", response_model=PerformanceResponse)
async def calculate_performance(
    request: PerformanceRequest,
    db: Session = Depends(get_db),
) -> PerformanceResponse:
    """Calculate takeoff and landing performance."""
    # Get aircraft
    aircraft = db.query(Aircraft).filter(Aircraft.id == request.aircraft_id).first()
    if not aircraft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aircraft with ID {request.aircraft_id} not found",
        )

    # Perform calculation
    service = PerformanceService(aircraft)
    result = service.calculate(
        weight_kg=request.weight_kg,
        pressure_altitude_ft=request.pressure_altitude_ft,
        temperature_c=request.temperature_c,
        wind_component_kt=request.wind_component_kt,
        runway_condition=request.runway_condition,
        runway_slope_percent=request.runway_slope_percent,
    )

    return result
