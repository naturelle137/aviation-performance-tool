"""Mass & Balance calculation service."""

import base64
import io
from typing import TYPE_CHECKING

import matplotlib
import matplotlib.pyplot as plt

from app.models.aircraft import CGEnvelope
from app.schemas.calculation import CGPoint, MassBalanceResponse, WeightInput

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

    def calculate(
        self,
        weight_inputs: list[WeightInput],
        fuel_liters: float,
        trip_fuel_liters: float = 0,
    ) -> MassBalanceResponse:
        """Calculate mass and balance.

        Args:
            weight_inputs: List of weights for each station.
            fuel_liters: Total fuel in liters.
            trip_fuel_liters: Fuel to be used during flight.

        Returns:
            MassBalanceResponse with calculation results.
        """
        warnings: list[str] = []

        # Calculate fuel weight (Patched for Draft consistency)
        # TODO: Update to handle per-tank fuel input
        fuel_density = 0.72  # Default
        fuel_arm = 0.0

        if self.aircraft.fuel_tanks:
            # For draft consistency, use the first tank's characteristics if available
            # Standard densities: AvGas=0.72, Diesel=0.84, JetA1=0.84
            tank = self.aircraft.fuel_tanks[0]
            fuel_arm = tank.arm_m
            if "Diesel" in tank.fuel_type.value or "Jet" in tank.fuel_type.value:
                fuel_density = 0.84
            else:
                fuel_density = 0.72

        fuel_weight_kg = fuel_liters * fuel_density
        trip_fuel_weight_kg = trip_fuel_liters * fuel_density
        landing_fuel_weight_kg = fuel_weight_kg - trip_fuel_weight_kg

        # Calculate payload
        payload_kg = sum(w.weight_kg for w in weight_inputs)

        # Calculate takeoff weight
        takeoff_weight_kg = (
            self.aircraft.empty_weight_kg + payload_kg + fuel_weight_kg
        )

        # Calculate landing weight
        landing_weight_kg = takeoff_weight_kg - trip_fuel_weight_kg

        # Calculate moments
        empty_moment = self.aircraft.empty_weight_kg * self.aircraft.empty_arm_m
        fuel_moment = fuel_weight_kg * fuel_arm
        landing_fuel_moment = landing_fuel_weight_kg * fuel_arm

        # Calculate payload moment (match inputs to weight stations)
        payload_moment = 0.0
        station_map = {s.name: s for s in self.aircraft.weight_stations}

        for weight_input in weight_inputs:
            station = station_map.get(weight_input.station_name)
            if station:
                payload_moment += weight_input.weight_kg * station.arm_m

                # Check max weight per station
                if station.max_weight_kg and weight_input.weight_kg > station.max_weight_kg:
                    warnings.append(
                        f"Weight at {station.name} ({weight_input.weight_kg} kg) "
                        f"exceeds maximum ({station.max_weight_kg} kg)"
                    )
            else:
                warnings.append(f"Unknown weight station: {weight_input.station_name}")

        # Calculate CG positions
        total_takeoff_moment = empty_moment + payload_moment + fuel_moment
        takeoff_arm = total_takeoff_moment / takeoff_weight_kg if takeoff_weight_kg > 0 else 0

        total_landing_moment = empty_moment + payload_moment + landing_fuel_moment
        landing_arm = total_landing_moment / landing_weight_kg if landing_weight_kg > 0 else 0

        # Check weight limits
        within_weight_limits = True
        if takeoff_weight_kg > self.aircraft.mtow_kg:
            warnings.append(
                f"Takeoff weight ({takeoff_weight_kg:.1f} kg) exceeds MTOW ({self.aircraft.mtow_kg:.1f} kg)"
            )
            within_weight_limits = False

        if self.aircraft.max_landing_weight_kg:
            if landing_weight_kg > self.aircraft.max_landing_weight_kg:
                warnings.append(
                    f"Landing weight ({landing_weight_kg:.1f} kg) exceeds MLW "
                    f"({self.aircraft.max_landing_weight_kg:.1f} kg)"
                )
                within_weight_limits = False

        # Check CG limits
        within_cg_limits = True
        normal_envelope = next(
            (e for e in self.aircraft.cg_envelopes if e.category == "normal"),
            None,
        )

        takeoff_in_limits = self._point_in_envelope(
            takeoff_weight_kg, takeoff_arm, normal_envelope
        )
        landing_in_limits = self._point_in_envelope(
            landing_weight_kg, landing_arm, normal_envelope
        )

        if not takeoff_in_limits:
            warnings.append("Takeoff CG is outside the envelope limits")
            within_cg_limits = False

        if not landing_in_limits:
            warnings.append("Landing CG is outside the envelope limits")
            within_cg_limits = False

        # Create CG points
        cg_points = [
            CGPoint(
                label="Takeoff",
                weight_kg=round(takeoff_weight_kg, 1),
                arm_m=round(takeoff_arm, 3),
                moment_kg_m=round(total_takeoff_moment, 1),
                within_limits=takeoff_in_limits,
            ),
            CGPoint(
                label="Landing",
                weight_kg=round(landing_weight_kg, 1),
                arm_m=round(landing_arm, 3),
                moment_kg_m=round(total_landing_moment, 1),
                within_limits=landing_in_limits,
            ),
        ]

        # Generate chart
        chart_base64 = self._generate_chart(cg_points, normal_envelope)

        return MassBalanceResponse(
            empty_weight_kg=round(self.aircraft.empty_weight_kg, 1),
            payload_kg=round(payload_kg, 1),
            fuel_weight_kg=round(fuel_weight_kg, 1),
            takeoff_weight_kg=round(takeoff_weight_kg, 1),
            landing_weight_kg=round(landing_weight_kg, 1),
            cg_points=cg_points,
            within_weight_limits=within_weight_limits,
            within_cg_limits=within_cg_limits,
            warnings=warnings,
            chart_image_base64=chart_base64,
        )

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

        polygon = [
            (p["arm_m"], p["weight_kg"]) for p in envelope.polygon_points
        ]
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
                y=self.aircraft.mtow_kg,
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
