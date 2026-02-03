"""Performance Operational Logic (P2/P3).

This module handles operational heuristics:
- FSM 3/75 correction factors
- Safety margins
- Warning generation
"""

from typing import Any

from app.services.units import Knot, Meter


class PerformanceLogic:
    """Operational logic engine for Performance calculations."""

    def __init__(self, aircraft: Any) -> None:
        self.aircraft = aircraft

    def apply_corrections(
        self,
        raw_roll: float,
        raw_total: float,
        params: dict[str, Any],
        is_mode_b: bool,
    ) -> tuple[Meter, Meter, Meter, Meter, list[str], float]:
        """Apply correction factors and safety margins.

        Args:
            raw_roll: Baseline ground roll.
            raw_total: Baseline total distance.
            params: Dict containing wind, surface, slope, phase, dens_alt.
            is_mode_b: Whether calculation is Mode B (adds Density Alt correction).

        Returns:
            tuple: (roll_final, total_final, roll_raw_factored, total_raw_factored, corrections, safety_factor)
        """
        corrections: list[str] = []
        phys_factor = 1.0

        # 1. Mode B Specific Corrections (Density Altitude)
        # Note: Mode A handles DA via interpolation inherently
        if is_mode_b:
            dens_alt = params["dens_alt"]
            alt_factor = 1.0 + (max(0, float(dens_alt)) / 1000 * 0.10)
            raw_roll *= alt_factor
            raw_total *= alt_factor
            corrections.append(f"Mode B Density Alt Corr: {alt_factor:.2f}x")

        # 2. Universal Physical Factors (FSM 3/75)

        # Wind Correction
        wind = params["wind"]
        if wind < 0: # Headwind (-1.5% per 2kt)
            factor = (1.0 - (abs(float(wind)) / 2 * 0.015))
            phys_factor *= factor
            corrections.append(f"Wind (-): {factor:.2f}x")
        else: # Tailwind (+10% per 2kt)
            factor = (1.0 + (float(wind) / 2 * 0.10))
            phys_factor *= factor
            corrections.append(f"Wind (+): {factor:.2f}x")

        # Surface Correction
        surface = params["surface"]
        if surface == "grass":
            phys_factor *= 1.20
            corrections.append("Grass Surface: 1.20x")
        elif surface == "wet":
            phys_factor *= 1.15
            corrections.append("Wet Surface: 1.15x")

        # Slope Correction (5% per 1%)
        slope = params["slope"]
        phase = params["phase"]
        if slope != 0:
            slope_dir = 1 if phase == "takeoff" else -1
            factor = (1.0 + (slope * 0.05 * slope_dir))
            phys_factor *= factor
            corrections.append(f"Slope {slope}%: {factor:.2f}x")

        # 3. Final Calculation
        safety_factor = 1.33 if phase == "landing" else 1.25
        corrections.append(f"Safety Factor ({phase}): {safety_factor:.2f}x")

        raw_roll_factored = raw_roll * phys_factor
        raw_total_factored = raw_total * phys_factor

        roll_final = raw_roll_factored * safety_factor
        total_final = raw_total_factored * safety_factor

        return (
            Meter(roll_final),
            Meter(total_final),
            Meter(raw_roll_factored),
            Meter(raw_total_factored),
            corrections,
            safety_factor
        )

    def generate_Global_warnings(self, wind: Knot) -> list[str]:
        """Generate high-level warnings."""
        warnings = []
        if wind > 0:
            warnings.append(f"Tailwind of {wind}kt increases takeoff/landing distances significantly (H-11).")
        return warnings
