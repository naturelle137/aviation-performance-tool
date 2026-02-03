"""Mass & Balance Core Logic (P1).

This module handles the pure physics and mathematical calculations for mass and balance,
including weight summation, moment calculation, and CG envelope validation.
"""

from typing import TYPE_CHECKING, Any

from app.models.aircraft import FuelType
from app.services.cg_validation import CGValidationService
from app.services.units import Kilogram, Liter, Meter

if TYPE_CHECKING:
    from app.models.aircraft import Aircraft


class MassBalanceCore:
    """Core physics engine for Mass & Balance."""

    def __init__(self, aircraft: "Aircraft") -> None:
        self.aircraft = aircraft

    def calculate_moments(
        self,
        weight_inputs: list[Any],
        fuel_inputs: list[Any] | None,
        fuel_liters_legacy: float | None,
        trip_fuel_liters: Liter,
    ) -> dict[str, Any]:
        """Perform all physics calculations for the flight phases."""

        # 1. Coordinate Fuel Inputs
        current_fuel_liters: dict[str, Liter] = {}
        if fuel_inputs:
            current_fuel_liters = {f.tank_name: f.fuel_l for f in fuel_inputs}
        elif fuel_liters_legacy is not None:
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

        return {
            "payload_kg": payload_kg,
            "fuel_weight_kg": takeoff_fuel_mass,
            "zero_fuel": (zero_fuel_weight, zero_fuel_arm, zero_fuel_moment),
            "takeoff": (takeoff_weight, takeoff_arm, takeoff_moment),
            "landing": (landing_weight, landing_arm, landing_moment),
        }

    def validate_phases(self, phases: dict[str, tuple[Kilogram, Meter, float]]) -> dict[str, Any]:
        """Validate all flight phases against the envelope."""
        envelope = next(
            (e for e in self.aircraft.cg_envelopes if e.category == "normal"), None
        )

        res_zf = CGValidationService.validate_point(*phases["zero_fuel"][:2], envelope)
        res_to = CGValidationService.validate_point(*phases["takeoff"][:2], envelope)
        res_ldg = CGValidationService.validate_point(*phases["landing"][:2], envelope)

        return {
            "zero_fuel": res_zf,
            "takeoff": res_to,
            "landing": res_ldg,
            "envelope": envelope
        }

    def _get_station_arm(self, name: str) -> Meter:
        for s in self.aircraft.weight_stations:
            if s.name == name:
                return Meter(s.arm_m)
        return Meter(0)

    def _get_fuel_density(self, fuel_type: FuelType) -> float:
        mapping = {
            FuelType.AVGAS_100LL: 0.72,
            FuelType.AVGAS_UL91: 0.71,
            FuelType.MOGAS: 0.72,
            FuelType.JET_A1: 0.84,
            FuelType.DIESEL: 0.84,
        }
        return mapping.get(fuel_type, 0.72)
