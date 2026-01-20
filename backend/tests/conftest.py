"""Pytest configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database session override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_aircraft_data():
    """Sample aircraft data for testing."""
    return {
        "registration": "D-EABC",
        "aircraft_type": "C172S",
        "manufacturer": "Cessna",
        "empty_weight_kg": 743.0,
        "empty_arm_m": 2.35,
        "mtow_kg": 1157.0,
        "max_landing_weight_kg": 1157.0,
        "fuel_capacity_l": 200.0,
        "fuel_arm_m": 2.40,
        "fuel_density_kg_l": 0.72,
    }


@pytest.fixture
def sample_weight_stations():
    """Sample weight stations for testing."""
    return [
        {"name": "Pilot", "arm_m": 2.35, "max_weight_kg": 110.0},
        {"name": "Copilot", "arm_m": 2.35, "max_weight_kg": 110.0},
        {"name": "Rear Passengers", "arm_m": 3.00, "max_weight_kg": 180.0},
        {"name": "Baggage", "arm_m": 3.50, "max_weight_kg": 54.0},
    ]


@pytest.fixture
def sample_cg_envelope():
    """Sample CG envelope for testing."""
    return {
        "category": "normal",
        "polygon_points": [
            {"weight_kg": 600, "arm_m": 2.20},
            {"weight_kg": 800, "arm_m": 2.20},
            {"weight_kg": 1157, "arm_m": 2.30},
            {"weight_kg": 1157, "arm_m": 2.50},
            {"weight_kg": 800, "arm_m": 2.55},
            {"weight_kg": 600, "arm_m": 2.50},
        ],
    }
