"""CG Envelope Validation Service."""

import math
from typing import TYPE_CHECKING, NamedTuple

from app.services.units import Kilogram, Meter

if TYPE_CHECKING:
    from app.models.aircraft import CGEnvelope


class ValidationResult(NamedTuple):
    """Result of a CG point validation."""
    within_limits: bool
    warnings: list[str]


class CGValidationService:
    """Service for validating CG points against envelopes.

    Mitigates Hazard H-13 (Polygon accuracy) and REQ-MB-06.
    """

    @staticmethod
    def validate_point(
        weight: Kilogram,
        arm: Meter,
        envelope: "CGEnvelope | None",
        epsilon: float = 1e-7
    ) -> ValidationResult:
        """Validate if a CG point (weight, arm) is within the given envelope.

        Uses a robust geometric algorithm with explicit boundary inclusion.
        """
        if not envelope or not envelope.polygon_points:
            return ValidationResult(within_limits=True, warnings=["No CG envelope defined for validation."])

        warnings: list[str] = []

        # Extract points as (x, y) = (arm, weight)
        poly = [(float(p["arm_m"]), float(p["weight_kg"])) for p in envelope.polygon_points]
        px, py = float(arm), float(weight)

        # 1. Check for boundary/vertex hits (Safety critical inclusion)
        on_boundary = False
        for i in range(len(poly)):
            p1 = poly[i]
            p2 = poly[(i + 1) % len(poly)]

            # Distance from point to line segment
            dist = CGValidationService._dist_point_to_segment(px, py, p1[0], p1[1], p2[0], p2[1])
            if dist <= epsilon:
                on_boundary = True
                break

        if on_boundary:
            return ValidationResult(within_limits=True, warnings=[])

        # 2. Ray Casting for internal containment
        is_inside = False
        n = len(poly)
        j = n - 1
        for i in range(n):
            if ((poly[i][1] > py) != (poly[j][1] > py)) and \
               (px < (poly[j][0] - poly[i][0]) * (py - poly[i][1]) / (poly[j][1] - poly[i][1]) + poly[i][0]):
                is_inside = not is_inside
            j = i

        if not is_inside:
            # Determine WHY it is outside for better pilot situational awareness
            arms = [p[0] for p in poly]
            weights = [p[1] for p in poly]
            min_arm, max_arm = min(arms), max(arms)
            min_weight, max_weight = min(weights), max(weights)

            if px < min_arm - epsilon:
                warnings.append(f"CG too far FORE ({arm:.3f}m < {min_arm:.3f}m limit)")
            elif px > max_arm + epsilon:
                warnings.append(f"CG too far AFT ({arm:.3f}m > {max_arm:.3f}m limit)")

            if py > max_weight + epsilon:
                warnings.append(f"Weight exceeds Envelope Maximum ({weight:.1f}kg > {max_weight:.1f}kg)")
            elif py < min_weight - epsilon:
                warnings.append(f"Weight below Envelope Minimum ({weight:.1f}kg < {min_weight:.1f}kg)")

            if not warnings:
                warnings.append(f"Point ({weight:.1f}kg @ {arm:.3f}m) outside {envelope.category} envelope limits.")

        return ValidationResult(within_limits=is_inside, warnings=warnings)

    @staticmethod
    def _dist_point_to_segment(px: float, py: float, x1: float, y1: float, x2: float, y2: float) -> float:
        """Calculate the shortest distance between a point and a line segment."""
        # Line segment length squared
        l2 = (x1 - x2)**2 + (y1 - y2)**2
        if l2 == 0:
            return math.sqrt((px - x1)**2 + (py - y1)**2)

        # Consider the line extending through the segment, parameterized as p1 + t (p2 - p1)
        # We find projection of point p onto the line.
        # t is the position of projection on the line segment [0, 1]
        t = ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / l2
        t = max(0.0, min(1.0, t))

        proj_x = x1 + t * (x2 - x1)
        proj_y = y1 + t * (y2 - y1)

        return math.sqrt((px - proj_x)**2 + (py - proj_y)**2)
