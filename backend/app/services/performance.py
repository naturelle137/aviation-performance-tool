"""Performance calculation service."""

from typing import TYPE_CHECKING, Literal

from app.schemas.calculation import PerformanceResponse

if TYPE_CHECKING:
    from app.models.aircraft import Aircraft


class PerformanceService:
    """Service for takeoff and landing performance calculations."""

    # ISA standard conditions
    ISA_TEMP_SEA_LEVEL_C = 15.0
    ISA_LAPSE_RATE_C_PER_1000FT = 2.0

    # Default correction factors (will be replaced by FSM 3/75 or POH data)
    DEFAULT_FACTORS = {
        "grass_factor": 1.20,  # 20% increase for grass runway
        "wet_factor": 1.15,  # 15% increase for wet runway
        "slope_factor_per_percent": 0.05,  # 5% per 1% slope
        "wind_factor_headwind": 0.015,  # 1.5% reduction per kt headwind
        "wind_factor_tailwind": 0.10,  # 10% increase per kt tailwind (!)
    }

    def __init__(self, aircraft: "Aircraft") -> None:
        """Initialize with aircraft data.

        Args:
            aircraft: The aircraft to calculate performance for.
        """
        self.aircraft = aircraft

    def calculate(
        self,
        weight_kg: float,
        pressure_altitude_ft: float,
        temperature_c: float,
        wind_component_kt: float = 0,
        runway_condition: Literal["dry", "wet", "grass"] = "dry",
        runway_slope_percent: float = 0,
    ) -> PerformanceResponse:
        """Calculate takeoff and landing performance.

        Args:
            weight_kg: Aircraft weight in kg.
            pressure_altitude_ft: Pressure altitude in feet.
            temperature_c: OAT in Celsius.
            wind_component_kt: Wind component (negative = headwind).
            runway_condition: Runway surface condition.
            runway_slope_percent: Runway slope in percent.

        Returns:
            PerformanceResponse with calculated distances.
        """
        warnings: list[str] = []
        corrections: list[str] = []

        # Get base performance data
        # TODO: Use actual performance profiles from aircraft
        # For now, use simplified generic SEP performance
        base_ground_roll_to = self._get_base_takeoff_roll(weight_kg, pressure_altitude_ft)
        base_distance_50ft_to = base_ground_roll_to * 1.5  # Rough approximation

        base_ground_roll_ldg = self._get_base_landing_roll(weight_kg, pressure_altitude_ft)
        base_distance_50ft_ldg = base_ground_roll_ldg * 1.8  # Rough approximation

        # Apply temperature correction (density altitude effect)
        isa_temp = self.ISA_TEMP_SEA_LEVEL_C - (
            pressure_altitude_ft / 1000 * self.ISA_LAPSE_RATE_C_PER_1000FT
        )
        temp_deviation = temperature_c - isa_temp

        if temp_deviation != 0:
            # Approximately 1% per degree above ISA for takeoff
            temp_factor = 1 + (temp_deviation * 0.01)
            base_ground_roll_to *= temp_factor
            base_distance_50ft_to *= temp_factor
            corrections.append(
                f"Temperature: ISA{temp_deviation:+.0f}°C ({temp_factor:.2f}x)"
            )

        # Apply runway condition correction
        if runway_condition == "grass":
            grass_factor = self.DEFAULT_FACTORS["grass_factor"]
            base_ground_roll_to *= grass_factor
            base_distance_50ft_to *= grass_factor
            base_ground_roll_ldg *= grass_factor
            base_distance_50ft_ldg *= grass_factor
            corrections.append(f"Grass runway: {grass_factor:.2f}x")

        elif runway_condition == "wet":
            wet_factor = self.DEFAULT_FACTORS["wet_factor"]
            # Wet mainly affects landing
            base_ground_roll_ldg *= wet_factor
            base_distance_50ft_ldg *= wet_factor
            corrections.append(f"Wet runway (landing): {wet_factor:.2f}x")

        # Apply slope correction
        if runway_slope_percent != 0:
            slope_factor = self.DEFAULT_FACTORS["slope_factor_per_percent"]
            # Upslope reduces takeoff, increases landing
            to_slope_correction = 1 - (runway_slope_percent * slope_factor)
            ldg_slope_correction = 1 + (runway_slope_percent * slope_factor)

            base_ground_roll_to *= to_slope_correction
            base_distance_50ft_to *= to_slope_correction
            base_ground_roll_ldg *= ldg_slope_correction
            base_distance_50ft_ldg *= ldg_slope_correction
            corrections.append(f"Runway slope: {runway_slope_percent:+.1f}%")

        # Apply wind correction
        if wind_component_kt != 0:
            if wind_component_kt < 0:  # Headwind
                hw_factor = self.DEFAULT_FACTORS["wind_factor_headwind"]
                wind_factor = 1 + (wind_component_kt * hw_factor)  # Reduces distance
            else:  # Tailwind
                tw_factor = self.DEFAULT_FACTORS["wind_factor_tailwind"]
                wind_factor = 1 + (wind_component_kt * tw_factor)
                warnings.append(
                    f"Tailwind component of {wind_component_kt:.0f} kt - consider using opposite runway"
                )

            base_ground_roll_to *= wind_factor
            base_distance_50ft_to *= wind_factor
            base_ground_roll_ldg *= wind_factor
            base_distance_50ft_ldg *= wind_factor
            corrections.append(f"Wind: {wind_component_kt:+.0f} kt ({wind_factor:.2f}x)")

        # Add safety margin reminder
        corrections.append("Safety factor: 1.25x (recommended)")
        base_ground_roll_to *= 1.25
        base_distance_50ft_to *= 1.25
        base_ground_roll_ldg *= 1.43  # 1/0.7 for landing
        base_distance_50ft_ldg *= 1.43

        return PerformanceResponse(
            takeoff_ground_roll_m=round(base_ground_roll_to, 0),
            takeoff_distance_50ft_m=round(base_distance_50ft_to, 0),
            landing_ground_roll_m=round(base_ground_roll_ldg, 0),
            landing_distance_50ft_m=round(base_distance_50ft_ldg, 0),
            corrections_applied=corrections,
            calculation_source=self.aircraft.performance_source,
            warnings=warnings,
        )

    def _get_base_takeoff_roll(
        self,
        weight_kg: float,
        pressure_altitude_ft: float,
    ) -> float:
        """Get base takeoff ground roll distance.

        This is a simplified calculation. Will be replaced by actual
        performance data from POH/FSM375.

        Args:
            weight_kg: Aircraft weight.
            pressure_altitude_ft: Pressure altitude.

        Returns:
            Base ground roll in meters.
        """
        # Simplified generic SEP performance
        # Base: 300m at MTOW, sea level, ISA
        base_roll = 300

        # Weight factor (squared relationship)
        weight_ratio = weight_kg / self.aircraft.mtow_kg
        weight_factor = weight_ratio ** 2

        # Altitude factor (approximately 10% per 1000ft)
        altitude_factor = 1 + (pressure_altitude_ft / 1000 * 0.10)

        return base_roll * weight_factor * altitude_factor

    def _get_base_landing_roll(
        self,
        weight_kg: float,
        pressure_altitude_ft: float,
    ) -> float:
        """Get base landing ground roll distance.

        Args:
            weight_kg: Aircraft weight.
            pressure_altitude_ft: Pressure altitude.

        Returns:
            Base ground roll in meters.
        """
        # Simplified: landing roll is typically shorter than takeoff
        base_roll = 200

        weight_ratio = weight_kg / self.aircraft.mtow_kg
        weight_factor = weight_ratio ** 1.5  # Less sensitive than takeoff

        # Altitude affects TAS on approach
        altitude_factor = 1 + (pressure_altitude_ft / 1000 * 0.05)

        return base_roll * weight_factor * altitude_factor
