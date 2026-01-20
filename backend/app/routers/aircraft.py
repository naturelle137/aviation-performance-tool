"""Aircraft CRUD endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.aircraft import Aircraft, CGEnvelope, WeightStation
from app.schemas.aircraft import (
    AircraftCreate,
    AircraftResponse,
    AircraftUpdate,
    AircraftWithDetails,
)

router = APIRouter()


@router.get("/", response_model=list[AircraftResponse])
async def list_aircraft(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> list[Aircraft]:
    """List all aircraft."""
    aircraft = db.query(Aircraft).offset(skip).limit(limit).all()
    return aircraft


@router.post("/", response_model=AircraftResponse, status_code=status.HTTP_201_CREATED)
async def create_aircraft(
    aircraft_data: AircraftCreate,
    db: Session = Depends(get_db),
) -> Aircraft:
    """Create a new aircraft."""
    # Check for duplicate registration
    existing = (
        db.query(Aircraft)
        .filter(Aircraft.registration == aircraft_data.registration.upper())
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Aircraft with registration {aircraft_data.registration} already exists",
        )

    # Create aircraft
    aircraft = Aircraft(
        registration=aircraft_data.registration.upper(),
        aircraft_type=aircraft_data.aircraft_type,
        manufacturer=aircraft_data.manufacturer,
        empty_weight_kg=aircraft_data.empty_weight_kg,
        empty_arm_m=aircraft_data.empty_arm_m,
        mtow_kg=aircraft_data.mtow_kg,
        max_landing_weight_kg=aircraft_data.max_landing_weight_kg,
        max_ramp_weight_kg=aircraft_data.max_ramp_weight_kg,
        fuel_capacity_l=aircraft_data.fuel_capacity_l,
        fuel_arm_m=aircraft_data.fuel_arm_m,
        fuel_density_kg_l=aircraft_data.fuel_density_kg_l,
    )
    db.add(aircraft)
    db.commit()
    db.refresh(aircraft)

    # Add weight stations if provided
    for idx, station_data in enumerate(aircraft_data.weight_stations or []):
        station = WeightStation(
            aircraft_id=aircraft.id,
            name=station_data.name,
            arm_m=station_data.arm_m,
            max_weight_kg=station_data.max_weight_kg,
            default_weight_kg=station_data.default_weight_kg,
            sort_order=idx,
        )
        db.add(station)

    # Add CG envelopes if provided
    for envelope_data in aircraft_data.cg_envelopes or []:
        envelope = CGEnvelope(
            aircraft_id=aircraft.id,
            category=envelope_data.category,
            polygon_points=envelope_data.polygon_points,
        )
        db.add(envelope)

    db.commit()
    db.refresh(aircraft)

    return aircraft


@router.get("/{aircraft_id}", response_model=AircraftWithDetails)
async def get_aircraft(
    aircraft_id: int,
    db: Session = Depends(get_db),
) -> Aircraft:
    """Get aircraft by ID with all details."""
    aircraft = db.query(Aircraft).filter(Aircraft.id == aircraft_id).first()
    if not aircraft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aircraft with ID {aircraft_id} not found",
        )
    return aircraft


@router.put("/{aircraft_id}", response_model=AircraftResponse)
async def update_aircraft(
    aircraft_id: int,
    aircraft_data: AircraftUpdate,
    db: Session = Depends(get_db),
) -> Aircraft:
    """Update an aircraft."""
    aircraft = db.query(Aircraft).filter(Aircraft.id == aircraft_id).first()
    if not aircraft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aircraft with ID {aircraft_id} not found",
        )

    # Update fields that are provided
    update_data = aircraft_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(aircraft, field):
            setattr(aircraft, field, value)

    db.commit()
    db.refresh(aircraft)

    return aircraft


@router.delete("/{aircraft_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_aircraft(
    aircraft_id: int,
    db: Session = Depends(get_db),
) -> None:
    """Delete an aircraft."""
    aircraft = db.query(Aircraft).filter(Aircraft.id == aircraft_id).first()
    if not aircraft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aircraft with ID {aircraft_id} not found",
        )

    db.delete(aircraft)
    db.commit()
