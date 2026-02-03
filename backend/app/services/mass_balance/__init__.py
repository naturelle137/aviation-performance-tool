"""Mass & Balance Service Facade.

This module exposes the `MassBalanceService` class which orchestrates
Core (P1) and Logic (P2/P3) modules.
"""

from typing import TYPE_CHECKING

from app.schemas.calculation import CGPoint, FuelInput, MassBalanceResponse, WeightInput
from app.services.units import Kilogram, Liter

from .core import MassBalanceCore
from .logic import MassBalanceLogic

if TYPE_CHECKING:
    from app.models.aircraft import Aircraft


class MassBalanceService:
    """Service for mass and balance calculations.

    Implements:
        - REQ-MB-01: Calculate Total Weight and CG.
        - REQ-MB-07: Calculate CG for Takeoff and Landing (migration).
        - REQ-MB-10: Detect CG migration out of limits.
    """

    def __init__(self, aircraft: "Aircraft") -> None:
        """Initialize with aircraft data."""
        self.aircraft = aircraft
        self.core = MassBalanceCore(aircraft)
        self.logic = MassBalanceLogic(aircraft)

    async def calculate(
        self,
        weight_inputs: list[WeightInput],
        fuel_inputs: list[FuelInput] | None = None,
        fuel_liters_legacy: float | None = None,
        trip_fuel_liters: Liter = Liter(0),
    ) -> MassBalanceResponse:
        """Calculate mass and balance with migration tracking."""

        # 1. Perform Physics Calculations (P1)
        results = self.core.calculate_moments(
            weight_inputs, fuel_inputs, fuel_liters_legacy, trip_fuel_liters
        )

        # 2. Validate Results (P1)
        validation = self.core.validate_phases(results)

        # 3. Assemble Response components
        zf_weight, zf_arm, zf_moment = results["zero_fuel"]
        to_weight, to_arm, to_moment = results["takeoff"]
        ldg_weight, ldg_arm, ldg_moment = results["landing"]

        takeoff_weight_kg = to_weight

        cg_points = [
            CGPoint(
                label="Zero Fuel",
                weight_kg=zf_weight,
                arm_m=zf_arm,
                moment_kg_m=zf_moment,
                within_limits=validation["zero_fuel"].within_limits,
            ),
            CGPoint(
                label="Takeoff",
                weight_kg=to_weight,
                arm_m=to_arm,
                moment_kg_m=to_moment,
                within_limits=validation["takeoff"].within_limits,
            ),
            CGPoint(
                label="Landing",
                weight_kg=ldg_weight,
                arm_m=ldg_arm,
                moment_kg_m=ldg_moment,
                within_limits=validation["landing"].within_limits,
            ),
        ]

        # 4. Operational Logic (P2/P3)
        warnings = self.logic.construct_warnings(validation, takeoff_weight_kg)
        chart_base64 = self.logic.generate_chart(cg_points, validation["envelope"])

        # 5. Final Response
        return MassBalanceResponse(
            empty_weight_kg=Kilogram(self.aircraft.empty_weight_kg),
            payload_kg=results["payload_kg"],
            fuel_weight_kg=results["fuel_weight_kg"],
            takeoff_weight_kg=takeoff_weight_kg,
            landing_weight_kg=ldg_weight,
            zero_fuel_weight_kg=zf_weight,
            cg_points=cg_points,
            within_weight_limits=(takeoff_weight_kg <= self.aircraft.mtow_kg),
            within_cg_limits=(
                validation["takeoff"].within_limits and validation["landing"].within_limits
            ),
            warnings=warnings,
            chart_image_base64=chart_base64,
        )
