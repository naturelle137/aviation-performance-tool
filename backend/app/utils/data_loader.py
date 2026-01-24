"""Data loader utility for aircraft profiles."""

import json
from pathlib import Path

from app.schemas.aircraft import AircraftCreate


def load_aircraft_profile(file_path: str | Path) -> AircraftCreate:
    """Load and validate an aircraft profile from JSON."""
    with open(file_path) as f:
        data = json.load(f)

    # Validate with Pydantic schema
    return AircraftCreate(**data)

def get_profile_path(filename: str) -> Path:
    """Get the path to a data profile."""
    return Path(__file__).parent.parent / "data" / filename
