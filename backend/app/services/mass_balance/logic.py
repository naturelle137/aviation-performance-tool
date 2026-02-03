"""Mass & Balance Operational Logic (P2/P3).

This module handles operational aspects such as chart generation, warning formatting,
and helper utilities for presentation.
"""

import base64
import io
from typing import TYPE_CHECKING, Any

import matplotlib
import matplotlib.pyplot as plt

from app.models.aircraft import CGEnvelope
from app.schemas.calculation import CGPoint

if TYPE_CHECKING:
    from app.models.aircraft import Aircraft

matplotlib.use("Agg")


class MassBalanceLogic:
    """Operational logic engine for Mass & Balance."""

    def __init__(self, aircraft: "Aircraft") -> None:
        self.aircraft = aircraft

    def generate_chart(
        self,
        cg_points: list[CGPoint],
        envelope: CGEnvelope | None,
    ) -> str | None:
        """Generate a M&B chart as base64 encoded PNG."""
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

    def construct_warnings(
        self,
        validation_results: dict[str, Any],
        takeoff_weight: float,
    ) -> list[str]:
        """Construct user-facing warnings based on validation results."""
        warnings: list[str] = []

        res_to = validation_results["takeoff"]
        res_ldg = validation_results["landing"]
        res_zf = validation_results["zero_fuel"]

        to_in_limits = res_to.within_limits
        ldg_in_limits = res_ldg.within_limits
        zf_in_limits = res_zf.within_limits

        # Collect detailed validation warnings
        warnings.extend(res_to.warnings if not to_in_limits else [])
        warnings.extend(res_ldg.warnings if not ldg_in_limits else [])
        warnings.extend(res_zf.warnings if not zf_in_limits else [])

        # H-05 Hazard: Migration check
        if to_in_limits and not ldg_in_limits:
            warnings.append(
                "CRITICAL: CG shifts OUT OF LIMITS during flight (Landing state unsafe)."
            )

        if takeoff_weight > self.aircraft.mtow_kg:
            warnings.append(
                f"Takeoff weight {takeoff_weight:.1f}kg exceeds MTOW {self.aircraft.mtow_kg:.1f}kg"
            )

        return warnings
