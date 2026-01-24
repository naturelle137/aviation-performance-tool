"""Mass & Balance calculation service."""

import base64
import io
from typing import TYPE_CHECKING

import matplotlib
import matplotlib.pyplot as plt

from app.models.aircraft import CGEnvelope, FuelType
from app.schemas.calculation import CGPoint, FuelInput, MassBalanceResponse, WeightInput
from app.services.units import Kilogram, Liter, Meter

matplotlib.use("Agg")  # Non-interactive backend for server use

if TYPE_CHECKING:
    from app.models.aircraft import Aircraft


class MassBalanceService:
    """Service for mass and balance calculations."""

    def __init__(self, aircraft: "Aircraft") -> None:
        """Initialize with aircraft data.

        Args:
            aircraft: The aircraft to calculate M&B for.
        """
        self.aircraft = aircraft

    async def calculate(
        self,
        weight_inputs: list[WeightInput],
        fuel_inputs: list[FuelInput] | None = None,
        fuel_liters_legacy: float | None = None,
        trip_fuel_liters: Liter = Liter(0),
    ) -> MassBalanceResponse:
        """Calculate mass and balance with migration tracking.

        Args:
            weight_inputs: Weights for each loading station.
            fuel_inputs: Per-tank fuel loading.
            fuel_liters_legacy: Legacy single-value fuel input.
            trip_fuel_liters: Planned fuel burn.

        Returns:
            MassBalanceResponse with details for all flight phases.
        """
        warnings: list[str] = []

        # 1. Coordinate Fuel Inputs
        current_fuel_liters: dict[str, Liter] = {}
        if fuel_inputs:
            current_fuel_liters = {f.tank_name: f.fuel_l for f in fuel_inputs}
        elif fuel_liters_legacy is not None:
            # Map legacy input to first available tank
            if self.aircraft.fuel_tanks:
                name = self.aircraft.fuel_tanks[0].name
                current_fuel_liters[name] = Liter(fuel_liters_legacy)

        # 2. Calculate State: ZERO FUEL
        payload_kg = Kilogram(sum(w.weight_kg for w in weight_inputs))
        payload_moment = sum(
            w.weight_kg * self._get_station_arm(w.station_name) for w in weight_inputs
        )

        zero_fuel_weight = Kilogram(self.aircraft.empty_weight_kg + payload_kg)
        zero_fuel_moment = (
            self.aircraft.empty_weight_kg * self.aircraft.empty_arm_m
        ) + payload_moment
        zero_fuel_arm = Meter(
            zero_fuel_moment / zero_fuel_weight if zero_fuel_weight > 0 else 0
        )

        # 3. Calculate State: TAKEOFF (T/O)
        takeoff_fuel_mass = Kilogram(0)
        takeoff_fuel_moment = 0.0

        for tank in self.aircraft.fuel_tanks:
            qty = current_fuel_liters.get(tank.name, Liter(0))
            density = self._get_fuel_density(tank.fuel_type)
            mass = Kilogram(qty * density)
            takeoff_fuel_mass = Kilogram(takeoff_fuel_mass + mass)
            takeoff_fuel_moment += mass * tank.arm_m

        takeoff_weight = Kilogram(zero_fuel_weight + takeoff_fuel_mass)
        takeoff_moment = zero_fuel_moment + takeoff_fuel_moment
        takeoff_arm = Meter(takeoff_moment / takeoff_weight if takeoff_weight > 0 else 0)

        # 4. Calculate State: LANDING (Burn)
        # Sequential burn logic: Burn from last tank to first for simplicity
        remaining_burn = trip_fuel_liters
        landing_fuel_mass = Kilogram(0)
        landing_fuel_moment = 0.0

        for tank in reversed(self.aircraft.fuel_tanks):
            qty = current_fuel_liters.get(tank.name, Liter(0))
            burn_from_this_tank = min(qty, remaining_burn)
            landing_qty = Liter(qty - burn_from_this_tank)
            remaining_burn = Liter(remaining_burn - burn_from_this_tank)

            density = self._get_fuel_density(tank.fuel_type)
            mass = Kilogram(landing_qty * density)
            landing_fuel_mass = Kilogram(landing_fuel_mass + mass)
            landing_fuel_moment += mass * tank.arm_m

        landing_weight = Kilogram(zero_fuel_weight + landing_fuel_mass)
        landing_moment = zero_fuel_moment + landing_fuel_moment
        landing_arm = Meter(landing_moment / landing_weight if landing_weight > 0 else 0)

        # 5. Validation & Hazards
        envelope = next(
            (e for e in self.aircraft.cg_envelopes if e.category == "normal"), None
        )

        to_in_limits = self._point_in_envelope(takeoff_weight, takeoff_arm, envelope)
        ldg_in_limits = self._point_in_envelope(landing_weight, landing_arm, envelope)
        zf_in_limits = self._point_in_envelope(zero_fuel_weight, zero_fuel_arm, envelope)

        # H-05 Hazard: Migration check
        if to_in_limits and not ldg_in_limits:
            warnings.append(
                "CRITICAL: CG shifts OUT OF LIMITS during flight (Landing state unsafe)."
            )

        if takeoff_weight > self.aircraft.mtow_kg:
            warnings.append(
                f"Takeoff weight {takeoff_weight:.1f}kg exceeds MTOW {self.aircraft.mtow_kg:.1f}kg"
            )

        # 6. Response Assembly
        cg_points = [
            CGPoint(
                label="Zero Fuel",
                weight_kg=zero_fuel_weight,
                arm_m=zero_fuel_arm,
                moment_kg_m=zero_fuel_moment,
                within_limits=zf_in_limits,
            ),
            CGPoint(
                label="Takeoff",
                weight_kg=takeoff_weight,
                arm_m=takeoff_arm,
                moment_kg_m=takeoff_moment,
                within_limits=to_in_limits,
            ),
            CGPoint(
                label="Landing",
                weight_kg=landing_weight,
                arm_m=landing_arm,
                moment_kg_m=landing_moment,
                within_limits=ldg_in_limits,
            ),
        ]

        return MassBalanceResponse(
            empty_weight_kg=Kilogram(self.aircraft.empty_weight_kg),
            payload_kg=payload_kg,
            fuel_weight_kg=takeoff_fuel_mass,
            takeoff_weight_kg=takeoff_weight,
            landing_weight_kg=landing_weight,
            zero_fuel_weight_kg=zero_fuel_weight,
            cg_points=cg_points,
            within_weight_limits=(takeoff_weight <= self.aircraft.mtow_kg),
            within_cg_limits=(to_in_limits and ldg_in_limits),
            warnings=warnings,
            chart_image_base64=self._generate_chart(cg_points, envelope),
        )

    def _get_station_arm(self, name: str) -> Meter:
        for s in self.aircraft.weight_stations:
            if s.name == name:
                return Meter(s.arm_m)
        return Meter(0)

    def _get_fuel_density(self, fuel_type: FuelType) -> float:
        """Map fuel type to standard density (kg/L)."""
        mapping = {
            FuelType.AVGAS_100LL: 0.72,
            FuelType.AVGAS_UL91: 0.71,
            FuelType.MOGAS: 0.72,
            FuelType.JET_A1: 0.84,
            FuelType.DIESEL: 0.84,
        }
        return mapping.get(fuel_type, 0.72)

    def _point_in_envelope(
        self,
        weight_kg: float,
        arm_m: float,
        envelope: CGEnvelope | None,
    ) -> bool:
        """Check if a point is within the CG envelope.

        Args:
            weight_kg: The weight to check.
            arm_m: The arm (CG position) to check.
            envelope: The CG envelope to check against.

        Returns:
            True if the point is within limits.
        """
        if not envelope or not envelope.polygon_points:
            return True  # No envelope defined, assume OK

        # Use matplotlib's path for point-in-polygon check
        from matplotlib.path import Path

        polygon = [(p["arm_m"], p["weight_kg"]) for p in envelope.polygon_points]
        path = Path(polygon)

        return bool(path.contains_point((arm_m, weight_kg)))

    def _generate_chart(
        self,
        cg_points: list[CGPoint],
        envelope: CGEnvelope | None,
    ) -> str | None:
        """Generate a M&B chart as base64 encoded PNG.

        Args:
            cg_points: The calculated CG points to plot.
            envelope: The CG envelope to draw.

        Returns:
            Base64 encoded PNG image string.
        """
        try:
            fig, ax = plt.subplots(figsize=(10, 8))

            # Plot envelope if available
            if envelope and envelope.polygon_points:
                arms = [p["arm_m"] for p in envelope.polygon_points]
                weights = [p["weight_kg"] for p in envelope.polygon_points]

                # Close the polygon
                arms.append(arms[0])
                weights.append(weights[0])

                ax.fill(arms, weights, alpha=0.3, color="green", label="CG Envelope")
                ax.plot(arms, weights, "g-", linewidth=2)

            # Plot CG points
            for point in cg_points:
                color = "green" if point.within_limits else "red"
                marker = "o" if point.within_limits else "x"
                ax.plot(
                    point.arm_m,
                    point.weight_kg,
                    marker,
                    color=color,
                    markersize=12,
                    markeredgewidth=3,
                    label=f"{point.label}: {point.weight_kg:.0f} kg @ {point.arm_m:.3f} m",
                )

            # Draw line between points
            if len(cg_points) >= 2:
                ax.plot(
                    [p.arm_m for p in cg_points],
                    [p.weight_kg for p in cg_points],
                    "b--",
                    linewidth=1,
                    alpha=0.5,
                )

            # Add reference lines
            ax.axhline(
                y=float(self.aircraft.mtow_kg),
                color="red",
                linestyle=":",
                alpha=0.5,
                label=f"MTOW: {self.aircraft.mtow_kg:.0f} kg",
            )

            ax.set_xlabel("CG Position (m)", fontsize=12)
            ax.set_ylabel("Weight (kg)", fontsize=12)
            ax.set_title(
                f"Mass & Balance - {self.aircraft.registration}",
                fontsize=14,
                fontweight="bold",
            )
            ax.legend(loc="upper left")
            ax.grid(True, alpha=0.3)

            # Save to bytes
            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
            buf.seek(0)
            plt.close(fig)

            return base64.b64encode(buf.read()).decode("utf-8")

        except Exception:
            return None
