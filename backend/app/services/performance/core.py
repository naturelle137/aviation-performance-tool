"""Performance Core Logic (P1).

This module handles pure physics calculations:
- Atmospheric physics (Density Altitude)
- Interpolation math
- Base physical formulas
"""

from typing import Any

from app.services.units import Celsius, Feet, Kilogram


class PerformanceCore:
    """Core physics engine for Performance calculations."""

    # ISA standard conditions
    ISA_TEMP_SEA_LEVEL_C = 15.0
    ISA_LAPSE_RATE_C_PER_1000FT = 1.983
    DA_FACTOR_PER_DEGREE = 118.8

    def __init__(self, aircraft: Any) -> None:
        self.aircraft = aircraft

    def calculate_density_altitude(self, press_alt: Feet, temp: Celsius) -> Feet:
        """Calculate Density Altitude using standard ISA deviations."""
        isa_temp = self.ISA_TEMP_SEA_LEVEL_C - (float(press_alt) / 1000 * self.ISA_LAPSE_RATE_C_PER_1000FT)
        dev = float(temp) - isa_temp
        da = float(press_alt) + (dev * self.DA_FACTOR_PER_DEGREE)
        return Feet(da)

    def interpolate_n(self, table: dict[str, Any], *args: float) -> float:
        """Helper for N-dimensional linear interpolation.

        Currently returns base value as placeholder (MVP intent).
        """
        # TODO: Implement robust linear interpolation
        return float(table.get("base", 0))

    def calculate_mode_b_base(self, weight: Kilogram, phase: str) -> tuple[float, float]:
        """Calculate simplified base performance for Mode B (FSM 3/75).

        Returns:
            tuple[float, float]: (raw_ground_roll, raw_total_distance)
        """
        # For this MVP, we use mtow-weighted constants as a base for Mode B
        if phase == "takeoff":
            raw_roll = 300 * (weight / self.aircraft.mtow_kg)**2
            raw_total = raw_roll * 1.5
        else:
            raw_roll = 250 * (weight / self.aircraft.mtow_kg)**1.5
            raw_total = raw_roll * 1.6

        return raw_roll, raw_total
