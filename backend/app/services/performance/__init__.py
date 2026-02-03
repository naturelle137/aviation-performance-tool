"""Performance Service Facade.

This module exposes the `PerformanceService` class which orchestrates
Core (P1) physics and Logic (P2/P3) rules.
"""

from typing import TYPE_CHECKING, Any, Literal

from app.schemas.calculation import PerformanceResponse
from app.services.units import Celsius, Feet, Kilogram, Knot

from .core import PerformanceCore
from .logic import PerformanceLogic

if TYPE_CHECKING:
    from app.models.aircraft import Aircraft, PerformanceProfile


class PerformanceService:
    """Service for takeoff and landing performance calculations.

    Implements:
        - REQ-PF-01: Calculate Takeoff Distance (TODR).
        - REQ-PF-02: Support Mode A (Tables) and Mode B (FSM 3/75).
        - REQ-PF-18: FSM 3/75 correction factors.
    """

    def __init__(self, aircraft: "Aircraft") -> None:
        """Initialize with aircraft data."""
        self.aircraft = aircraft
        self.core = PerformanceCore(aircraft)
        self.logic = PerformanceLogic(aircraft)

    async def calculate(
        self,
        weight_kg: Kilogram,
        pressure_altitude_ft: Feet,
        temperature_c: Celsius,
        wind_component_kt: Knot = Knot(0),
        runway_condition: Literal["dry", "wet", "grass"] = "dry",
        runway_slope_percent: float = 0,
    ) -> PerformanceResponse:
        """Calculate takeoff and landing performance.

        Supports both Mode A (Interpolation) and Mode B (Correction Factors).
        """
        warnings: list[str] = []

        # 1. Atmospheric calculations (P1)
        density_alt = self.core.calculate_density_altitude(pressure_altitude_ft, temperature_c)

        # 2. Get Takeoff Performance
        to_profile = self._get_profile("takeoff")
        to_res = self._calculate_phase(
            "takeoff", to_profile, weight_kg, pressure_altitude_ft,
            temperature_c, density_alt, wind_component_kt,
            runway_condition, runway_slope_percent, warnings
        )

        # 3. Get Landing Performance
        ldg_profile = self._get_profile("landing")
        ldg_res = self._calculate_phase(
            "landing", ldg_profile, weight_kg, pressure_altitude_ft,
            temperature_c, density_alt, wind_component_kt,
            runway_condition, runway_slope_percent, warnings
        )

        # 4. Global Safety Warnings (P2/P3)
        warnings.extend(self.logic.generate_Global_warnings(wind_component_kt))

        return PerformanceResponse(
            density_altitude_ft=density_alt,
            takeoff_ground_roll_m=to_res["ground_roll"],
            takeoff_distance_50ft_m=to_res["total_dist"],
            takeoff_ground_roll_raw_m=to_res["ground_roll_raw"],
            takeoff_distance_50ft_raw_m=to_res["total_dist_raw"],
            landing_ground_roll_m=ldg_res["ground_roll"],
            landing_distance_50ft_m=ldg_res["total_dist"],
            landing_ground_roll_raw_m=ldg_res["ground_roll_raw"],
            landing_distance_50ft_raw_m=ldg_res["total_dist_raw"],
            calculation_source=to_res["source"],
            corrections_applied=to_res["corrections"] + ldg_res["corrections"], # Flatten for simplicity
            warnings=list(set(warnings)),
        )

    def _calculate_phase(
        self,
        phase: str,
        profile: "PerformanceProfile | None",
        weight: Kilogram,
        press_alt: Feet,
        temp: Celsius,
        dens_alt: Feet,
        wind: Knot,
        surface: str,
        slope: float,
        warnings: list[str]
    ) -> dict[str, Any]:
        """Calculate performance for a specific phase (takeoff/landing)."""

        source = "mode_b_fsm375"
        raw_roll = 0.0
        raw_total = 0.0

        # 1. Base Performance (P1)
        # Attempt Mode A (POH Tables)
        if profile and profile.data_tables:
            try:
                # Mode A: Interpolation from Tables
                raw_roll = self.core.interpolate_n(profile.data_tables["ground_roll"], weight, press_alt, temp)
                raw_total = self.core.interpolate_n(profile.data_tables["total_dist_50ft"], weight, press_alt, temp)
                source = "mode_a_poh"
            except (KeyError, ValueError):
                warnings.append(f"Mode A data incomplete for {phase}, failing back to Mode B (FSM 3/75).")

        # Fallback to Mode B (FSM 3/75) if no Mode A data or calculation failed
        if source == "mode_b_fsm375":
            raw_roll, raw_total = self.core.calculate_mode_b_base(weight, phase)

        # 2. Operational Adjustments (P2/P3)
        roll_final, total_final, roll_raw, total_raw, corrections, _ = self.logic.apply_corrections(
            raw_roll, raw_total,
            params={
                "wind": wind, "surface": surface, "slope": slope,
                "phase": phase, "dens_alt": dens_alt
            },
            is_mode_b=(source == "mode_b_fsm375")
        )

        return {
            "ground_roll": roll_final,
            "total_dist": total_final,
            "ground_roll_raw": roll_raw,
            "total_dist_raw": total_raw,
            "source": source,
            "corrections": corrections
        }

    def _get_profile(self, profile_type: str) -> "PerformanceProfile | None":
        for p in self.aircraft.performance_profiles:
            if p.profile_type == profile_type:
                return p
        return None
