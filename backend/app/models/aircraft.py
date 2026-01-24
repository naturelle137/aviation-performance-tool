"""Aircraft and related database models."""

import enum
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Enum, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class FuelType(str, enum.Enum):
    """Supported fuel types with standard densities."""
    MOGAS = "MoGas"
    AVGAS_100LL = "AvGas 100LL"
    JET_A1 = "Jet A-1"
    AVGAS_UL91 = "AvGas UL91"
    DIESEL = "Diesel"


class Aircraft(Base):
    """Aircraft model with basic specifications."""

    __tablename__ = "aircraft"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    registration: Mapped[str] = mapped_column(
        String(10), unique=True, index=True, nullable=False
    )
    aircraft_type: Mapped[str] = mapped_column(String(50), nullable=False)
    manufacturer: Mapped[str] = mapped_column(String(50), nullable=False)

    # Weight data
    empty_weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    empty_arm_m: Mapped[float] = mapped_column(Float, nullable=False)
    mtow_kg: Mapped[float] = mapped_column(Float, nullable=False)
    max_landing_weight_kg: Mapped[float] = mapped_column(Float, nullable=True)
    max_ramp_weight_kg: Mapped[float] = mapped_column(Float, nullable=True)

    # Relationships (Fuel data moved to FuelTank relationship)
    fuel_tanks: Mapped[list["FuelTank"]] = relationship(
        "FuelTank",
        back_populates="aircraft",
        cascade="all, delete-orphan",
    )

    # Performance source
    performance_source: Mapped[str] = mapped_column(
        String(20), default="manufacturer"
    )  # fsm375, manufacturer, custom
    custom_formulas: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    # Weighing info
    weighing_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    weight_stations: Mapped[list["WeightStation"]] = relationship(
        "WeightStation",
        back_populates="aircraft",
        cascade="all, delete-orphan",
        order_by="WeightStation.sort_order",
    )
    cg_envelopes: Mapped[list["CGEnvelope"]] = relationship(
        "CGEnvelope",
        back_populates="aircraft",
        cascade="all, delete-orphan",
    )
    performance_profiles: Mapped[list["PerformanceProfile"]] = relationship(
        "PerformanceProfile",
        back_populates="aircraft",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Aircraft {self.registration} ({self.aircraft_type})>"


class FuelTank(Base):
    """Fuel tank definition for an aircraft."""

    __tablename__ = "fuel_tanks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    aircraft_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("aircraft.id", ondelete="CASCADE"), nullable=False
    )

    name: Mapped[str] = mapped_column(String(50), nullable=False)
    capacity_l: Mapped[float] = mapped_column(Float, nullable=False)
    arm_m: Mapped[float] = mapped_column(Float, nullable=False)
    unusable_fuel_l: Mapped[float] = mapped_column(Float, default=0.0)
    fuel_type: Mapped[FuelType] = mapped_column(
        Enum(FuelType), default=FuelType.AVGAS_100LL, nullable=False
    )
    default_quantity_l: Mapped[float] = mapped_column(Float, default=0.0)

    # Relationship
    aircraft: Mapped["Aircraft"] = relationship("Aircraft", back_populates="fuel_tanks")

    def __repr__(self) -> str:
        return f"<FuelTank {self.name} for {self.aircraft_id}>"


class WeightStation(Base):
    """Weight station (loading point) for an aircraft."""

    __tablename__ = "weight_stations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    aircraft_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("aircraft.id", ondelete="CASCADE"), nullable=False
    )

    name: Mapped[str] = mapped_column(String(50), nullable=False)
    arm_m: Mapped[float] = mapped_column(Float, nullable=False)
    max_weight_kg: Mapped[float] = mapped_column(Float, nullable=True)
    default_weight_kg: Mapped[float] = mapped_column(Float, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    # Relationship
    aircraft: Mapped["Aircraft"] = relationship("Aircraft", back_populates="weight_stations")

    def __repr__(self) -> str:
        return f"<WeightStation {self.name} @ {self.arm_m}m>"


class CGEnvelope(Base):
    """CG envelope (limits polygon) for an aircraft."""

    __tablename__ = "cg_envelopes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    aircraft_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("aircraft.id", ondelete="CASCADE"), nullable=False
    )

    category: Mapped[str] = mapped_column(
        String(20), default="normal"
    )  # normal, utility, acrobatic
    polygon_points: Mapped[list[dict[str, float]]] = mapped_column(JSON, nullable=False)
    # Format: [{"weight_kg": 800, "arm_m": 2.0}, ...]

    # Relationship
    aircraft: Mapped["Aircraft"] = relationship("Aircraft", back_populates="cg_envelopes")

    def __repr__(self) -> str:
        return f"<CGEnvelope {self.category} for aircraft {self.aircraft_id}>"


class PerformanceProfile(Base):
    """Performance data profile for an aircraft."""

    __tablename__ = "performance_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    aircraft_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("aircraft.id", ondelete="CASCADE"), nullable=False
    )

    profile_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # takeoff, landing, climb, cruise
    source: Mapped[str] = mapped_column(
        String(20), default="manufacturer"
    )  # fsm375, poh, custom

    # Data can be stored as tables or formulas
    data_tables: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    formulas: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Relationship
    aircraft: Mapped["Aircraft"] = relationship(
        "Aircraft", back_populates="performance_profiles"
    )

    def __repr__(self) -> str:
        return f"<PerformanceProfile {self.profile_type} ({self.source})>"
