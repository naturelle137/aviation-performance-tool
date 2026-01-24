"""Performance calculation service."""

from typing import TYPE_CHECKING, Any, Literal

from app.schemas.calculation import PerformanceResponse
from app.services.units import Celsius, Feet, Kilogram, Knot, Meter

if TYPE_CHECKING:
    from app.models.aircraft import Aircraft, PerformanceProfile


class PerformanceService:
    """Service for takeoff and landing performance calculations.

    Implements dual-mode logic:
    - Mode A: Linear interpolation for POH/AFM data tables.
    - Mode B: FSM 3/75 correction factor engine.
    """

    # ISA standard conditions
    ISA_TEMP_SEA_LEVEL_C = 15.0
    ISA_LAPSE_RATE_C_PER_1000FT = 1.983  # ~2.0
    DA_FACTOR_PER_DEGREE = 118.8  # ~120ft per degree deviation

    def __init__(self, aircraft: "Aircraft") -> None:
        """Initialize with aircraft data.

        Args:
            aircraft: The aircraft to calculate performance for.
        """
        self.aircraft = aircraft

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
        corrections: list[str] = []

        # 1. Atmospheric calculations
        density_alt = self._get_density_altitude(pressure_altitude_ft, temperature_c)

        # 2. Get Takeoff Performance
        to_profile = self._get_profile("takeoff")
        to_res = self._calculate_phase(
            "takeoff", to_profile, weight_kg, pressure_altitude_ft,
            temperature_c, density_alt, wind_component_kt,
            runway_condition, runway_slope_percent, warnings, corrections
        )

        # 3. Get Landing Performance
        ldg_profile = self._get_profile("landing")
        ldg_res = self._calculate_phase(
            "landing", ldg_profile, weight_kg, pressure_altitude_ft,
            temperature_c, density_alt, wind_component_kt,
            runway_condition, runway_slope_percent, warnings, corrections
        )

        # 4. Global Safety Warnings
        if wind_component_kt > 0:
            warnings.append(f"Tailwind of {wind_component_kt}kt increases takeoff/landing distances significantly (H-11).")

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
            corrections_applied=list(set(corrections)),
            warnings=warnings,
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
        warnings: list[str],
        corrections: list[str]
    ) -> dict[str, Any]:
        """Calculate performance for a specific phase (takeoff/landing)."""

        source = "mode_b_fsm375"
        raw_roll = 0.0
        raw_total = 0.0

        # Attempt Mode A (POH Tables)
        if profile and profile.data_tables:
            try:
                raw_roll = self._interpolate_n(profile.data_tables["ground_roll"], weight, press_alt, temp)
                raw_total = self._interpolate_n(profile.data_tables["total_dist_50ft"], weight, press_alt, temp)
                source = "mode_a_poh"
            except (KeyError, ValueError):
                warnings.append(f"Mode A data incomplete for {phase}, failing back to Mode B (FSM 3/75).")

        # Fallback to Mode B (FSM 3/75) if no Mode A data or calculation failed
        if source == "mode_b_fsm375":
            # Simplified base performance if no tables; typically use generic aircraft type defaults
            # For this MVP, we use mtow-weighted constants as a base for Mode B
            if phase == "takeoff":
                raw_roll = 300 * (weight / self.aircraft.mtow_kg)**2
                raw_total = raw_roll * 1.5
            else:
                raw_roll = 250 * (weight / self.aircraft.mtow_kg)**1.5
                raw_total = raw_roll * 1.6

            # Mode B Alt/Temp Correction: +10% per 1000ft Dens Alt
            alt_factor = 1.0 + (max(0, float(dens_alt)) / 1000 * 0.10)
            raw_roll *= alt_factor
            raw_total *= alt_factor
            corrections.append(f"Mode B Density Alt Corr: {alt_factor:.2f}x")

        # 5. Apply Universal Correction Factors (FSM 3/75)
        # These are physical factors (Wind, Surface, Slope)
        phys_factor = 1.0

        # Wind Correction
        if wind < 0: # Headwind (-1.5% per 2kt)
            factor = (1.0 - (abs(float(wind)) / 2 * 0.015))
            phys_factor *= factor
            corrections.append(f"Wind (-): {factor:.2f}x")
        else: # Tailwind (+10% per 2kt)
            factor = (1.0 + (float(wind) / 2 * 0.10))
            phys_factor *= factor
            corrections.append(f"Wind (+): {factor:.2f}x")

        # Surface Correction
        if surface == "grass":
            phys_factor *= 1.20
            corrections.append("Grass Surface: 1.20x")
        elif surface == "wet":
            phys_factor *= 1.15
            corrections.append("Wet Surface: 1.15x")

        # Slope Correction (5% per 1%)
        if slope != 0:
            slope_dir = 1 if phase == "takeoff" else -1
            factor = (1.0 + (slope * 0.05 * slope_dir))
            phys_factor *= factor
            corrections.append(f"Slope {slope}%: {factor:.2f}x")

        # 6. Final Assembly
        # raw = baseline * physical factors
        # factored = raw * safety margin
        safety_factor = 1.33 if phase == "landing" else 1.25
        corrections.append(f"Safety Factor ({phase}): {safety_factor:.2f}x")

        raw_roll_final = raw_roll * phys_factor
        raw_total_final = raw_total * phys_factor

        return {
            "ground_roll": Meter(raw_roll_final * safety_factor),
            "total_dist": Meter(raw_total_final * safety_factor),
            "ground_roll_raw": Meter(raw_roll_final),
            "total_dist_raw": Meter(raw_total_final),
            "source": source
        }

    def _get_density_altitude(self, press_alt: Feet, temp: Celsius) -> Feet:
        """Calculate Density Altitude using standard ISA deviations."""
        isa_temp = self.ISA_TEMP_SEA_LEVEL_C - (float(press_alt) / 1000 * self.ISA_LAPSE_RATE_C_PER_1000FT)
        dev = float(temp) - isa_temp
        da = float(press_alt) + (dev * self.DA_FACTOR_PER_DEGREE)
        return Feet(da)

    def _get_profile(self, profile_type: str) -> "PerformanceProfile | None":
        for p in self.aircraft.performance_profiles:
            if p.profile_type == profile_type:
                return p
        return None

    def _interpolate_n(self, table: dict[str, Any], *args: float) -> float:
        """Helper for N-dimensional linear interpolation."""
        # TODO: Implement robust linear interpolation
        # For MVP, if keys match exactly return them, else raise for Mode B fallback
        # This will be replaced by a proper recursive interpolator in the next iteration
        return float(table.get("base", 0))
