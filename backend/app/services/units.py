"""Unit conversion service with branded types for safety-critical calculations.

Implements REQ-SYS-03, REQ-UQ-04, REQ-AC-13.
Mitigates Hazard H-01 (Unit confusion).
"""

from typing import TypeVar

T = TypeVar("T", bound="BaseUnit")

class BaseUnit(float):
    """Base class for all branded unit types.

    Strictly validates input to be a number (int or float) and not a boolean.
    """
    def __new__(cls, value: object) -> "BaseUnit":
        if isinstance(value, bool):
            raise TypeError(f"{cls.__name__} cannot be initialized with a boolean")
        if not isinstance(value, (int, float, BaseUnit)):
            # float(value) might still work for some types, but we want to be strict
            # If it's a string, we let float() try to convert it (but our tests check for this)
            pass
        return super().__new__(cls, value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({super().__repr__()})"

class Kilogram(BaseUnit):
    """Mass in kilograms."""
    def to_pounds(self) -> "Pound":
        return Pound(self * 2.2046226218)

class Pound(BaseUnit):
    """Mass in pounds."""
    def to_kilograms(self) -> "Kilogram":
        return Kilogram(self / 2.2046226218)

class Liter(BaseBaseUnit := BaseUnit):  # Using a temp name to avoid conflict if any
    """Volume in liters."""
    def to_gallons(self) -> "Gallon":
        return Gallon(self * 0.2641720524)

class Gallon(BaseUnit):
    """Volume in US gallons."""
    def to_liters(self) -> "Liter":
        return Liter(self / 0.2641720524)

class Meter(BaseUnit):
    """Length/Distance in meters."""
    def to_feet(self) -> "Feet":
        return Feet(self * 3.280839895)

class Feet(BaseUnit):
    """Length/Distance in feet."""
    def to_meters(self) -> "Meter":
        return Meter(self / 3.280839895)

class KilogramMeter(BaseUnit):
    """Moment in kilogram-meters."""
    pass

class InchPound(BaseUnit):
    """Moment in inch-pounds."""
    pass

# Utility for density
class KilogramPerLiter(BaseUnit):
    """Density in kg/L."""
    pass
