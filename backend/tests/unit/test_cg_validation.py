"""Unit tests for the CG Validation Service."""

import pytest
from app.services.cg_validation import CGValidationService
from app.models.aircraft import CGEnvelope
from app.services.units import Kilogram, Meter

@pytest.fixture
def sample_envelope():
    """Create a standard rectangular-ish envelope for testing."""
    return CGEnvelope(
        category="normal",
        polygon_points=[
            {"weight_kg": 600, "arm_m": 2.20},
            {"weight_kg": 1200, "arm_m": 2.20},
            {"weight_kg": 1200, "arm_m": 2.50},
            {"weight_kg": 600, "arm_m": 2.50},
        ]
    )

@pytest.mark.mvp
@pytest.mark.p1
@pytest.mark.safety
def test_validate_point_inside(sample_envelope):
    """Verify that a point clearly inside is valid."""
    result = CGValidationService.validate_point(
        Kilogram(900), Meter(2.35), sample_envelope
    )
    assert result.within_limits is True
    assert len(result.warnings) == 0

@pytest.mark.mvp
@pytest.mark.p1
@pytest.mark.safety
def test_validate_point_on_boundary(sample_envelope):
    """Verify that a point exactly on the boundary is valid."""
    # Front limit is 2.20m
    result = CGValidationService.validate_point(
        Kilogram(900), Meter(2.20), sample_envelope
    )
    assert result.within_limits is True

@pytest.mark.mvp
@pytest.mark.p1
@pytest.mark.safety
def test_validate_point_fore_limit(sample_envelope):
    """Verify semantic warning for Fore limit violation."""
    # 2.19m is outside (limit 2.20m)
    result = CGValidationService.validate_point(
        Kilogram(900), Meter(2.19), sample_envelope
    )
    assert result.within_limits is False
    assert any("too far FORE" in w for w in result.warnings)
    assert "2.200m limit" in result.warnings[0]

@pytest.mark.mvp
@pytest.mark.p1
@pytest.mark.safety
def test_validate_point_aft_limit(sample_envelope):
    """Verify semantic warning for Aft limit violation."""
    # 2.51m is outside (limit 2.50m)
    result = CGValidationService.validate_point(
        Kilogram(900), Meter(2.51), sample_envelope
    )
    assert result.within_limits is False
    assert any("too far AFT" in w for w in result.warnings)

@pytest.mark.mvp
@pytest.mark.p1
@pytest.mark.safety
def test_validate_point_weight_limit(sample_envelope):
    """Verify semantic warning for Weight violation."""
    # 1201kg is outside (max 1200kg)
    result = CGValidationService.validate_point(
        Kilogram(1201), Meter(2.35), sample_envelope
    )
    assert result.within_limits is False
    assert any("Weight exceeds Envelope Maximum" in w for w in result.warnings)

@pytest.mark.mvp
@pytest.mark.p1
def test_validate_no_envelope():
    """Verify behavior when no envelope is provided."""
    result = CGValidationService.validate_point(Kilogram(900), Meter(2.35), None)
    assert result.within_limits is True
    assert "No CG envelope defined" in result.warnings[0]

@pytest.mark.mvp
@pytest.mark.p1
@pytest.mark.safety
def test_sloped_boundary_validation():
    """Verify validation on a non-rectangular sloped boundary.
    
    AFM Example: Front limit moves aft as weight increases.
    800kg @ 2.20m to 1200kg @ 2.30m
    """
    sloped_envelope = CGEnvelope(
        category="normal",
        polygon_points=[
            {"weight_kg": 800, "arm_m": 2.20},
            {"weight_kg": 1200, "arm_m": 2.30},
            {"weight_kg": 1200, "arm_m": 2.50},
            {"weight_kg": 800, "arm_m": 2.50},
        ]
    )
    
    # Mid-weight point (1000kg). 
    # Sloped limit at 1000kg is exactly 2.25m.
    
    # 1. Inside
    assert CGValidationService.validate_point(Kilogram(1000), Meter(2.26), sloped_envelope).within_limits is True
    
    # 2. Outside (but within the min/max arm of the WHOLE polygon)
    # This tests that we don't just use a simple bounding box.
    res = CGValidationService.validate_point(Kilogram(1000), Meter(2.24), sloped_envelope)
    assert res.within_limits is False
    # Since it's within [2.20, 2.50], it might not trigger FORE/AFT if they were based on bounding box.
    # But our service uses specific warning for sloped violations if no basic limit triggered.
    assert any("outside normal envelope limits" in w for w in res.warnings)
