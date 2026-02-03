"""Unit tests for the unit conversion service.

Verifies mathematical correctness and type behavior.
Mitigates Hazard H-01 (Incorrect CG due to kg/lbs confusion).
Implements REQ-SYS-03, REQ-UQ-04, REQ-AC-13.
"""

import pytest

from app.services.units import Feet, Gallon, Kilogram, Liter, Meter, Pound


@pytest.mark.p1
@pytest.mark.safety
def test_kg_to_lb_conversion():
    """Verify kg to lb conversion logic.

    Traceability: REQ-AC-13, H-01
    """
    kg = Kilogram(100)
    lb = kg.to_pounds()
    assert isinstance(lb, Pound)
    assert lb == pytest.approx(220.462, abs=1e-3)

@pytest.mark.p1
@pytest.mark.safety
def test_lb_to_kg_conversion():
    """Verify lb to kg conversion logic.

    Traceability: REQ-AC-13, H-01
    """
    lb = Pound(220.462)
    kg = lb.to_kilograms()
    assert isinstance(kg, Kilogram)
    assert kg == pytest.approx(100.0, abs=1e-3)

@pytest.mark.p1
@pytest.mark.safety
def test_liter_to_gallon_conversion():
    """Verify liter to gallon conversion logic.

    Traceability: REQ-AC-13, H-01
    """
    liter = Liter(100)
    gallon = liter.to_gallons()
    assert isinstance(gallon, Gallon)
    assert gallon == pytest.approx(26.417, abs=1e-3)

@pytest.mark.p1
@pytest.mark.safety
def test_gallon_to_liter_conversion():
    """Verify gallon to liter conversion logic.

    Traceability: REQ-AC-13, H-01
    """
    gallon = Gallon(26.417)
    liter = gallon.to_liters()
    assert isinstance(liter, Liter)
    assert liter == pytest.approx(100.0, abs=1e-3)

@pytest.mark.p1
@pytest.mark.safety
def test_meter_to_feet_conversion():
    """Verify meter to feet conversion logic.

    Traceability: REQ-AC-13, H-01
    """
    meter = Meter(10)
    feet = meter.to_feet()
    assert isinstance(feet, Feet)
    assert feet == pytest.approx(32.808, abs=1e-3)

@pytest.mark.p1
@pytest.mark.safety
def test_feet_to_meter_conversion():
    """Verify feet to meter conversion logic.

    Traceability: REQ-AC-13, H-01
    """
    feet = Feet(32.808)
    meter = feet.to_meters()
    assert isinstance(meter, Meter)
    assert meter == pytest.approx(10.0, abs=1e-3)

@pytest.mark.p1
@pytest.mark.safety
def test_branded_type_inheritance():
    """Ensure branded types behave like floats.

    Traceability: REQ-UQ-04
    """
    kg = Kilogram(10)
    result = kg * 2
    assert result == 20
    # Operations with floats return floats in Python inheritance
    assert not isinstance(result, Kilogram)

    # Re-branding is explicit
    rebranded = Kilogram(result)
    assert isinstance(rebranded, Kilogram)

@pytest.mark.p1
@pytest.mark.safety
def test_invalid_types_initialization():
    """Verify behavior with invalid input types.

    Traceability: REQ-SYS-03, H-01
    """
    # String input should raise ValueError (inherited from float)
    with pytest.raises(ValueError):
        Kilogram("abc")

    # None input should raise TypeError (inherited from float)
    with pytest.raises(TypeError):
        Kilogram(None)

    # Boolean input should raise TypeError (safety mitigation)
    with pytest.raises(TypeError) as excinfo:
        Kilogram(True)
    assert "cannot be initialized with a boolean" in str(excinfo.value)
