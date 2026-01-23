# API Documentation

## Overview

The Aviation Performance Tool exposes a RESTful API for aircraft management, M&B calculations, and performance calculations.

**Base URL**: `http://localhost:8000/api/v1`

**OpenAPI Spec**: Available at `/docs` (Swagger UI) and `/redoc` (ReDoc)

---

## Authentication

> **Note**: Authentication is planned for Phase 3. Currently, the API is unauthenticated for local use.

---

## Endpoints

### Aircraft Profiles

#### List Aircraft
```http
GET /aircraft
```

**Response** `200 OK`:
```json
{
  "items": [
    {
      "registration": "D-EABC",
      "manufacturer": "Diamond",
      "model": "DA40 D",
      "status": "verified"
    }
  ],
  "total": 1
}
```

#### Get Aircraft Profile
```http
GET /aircraft/{registration}
```

**Parameters**:
| Name | Type | Description |
|------|------|-------------|
| `registration` | path | Aircraft registration (e.g., "D-EABC") |

**Response** `200 OK`: Full aircraft profile JSON (see ARCHITECTURE.md)

#### Create Aircraft Profile
```http
POST /aircraft
Content-Type: application/json
```

**Body**: Aircraft profile JSON

**Response** `201 Created`: Created profile

#### Update Aircraft Profile
```http
PUT /aircraft/{registration}
Content-Type: application/json
```

**Response** `200 OK`: Updated profile

#### Delete Aircraft Profile
```http
DELETE /aircraft/{registration}
```

**Response** `204 No Content`

---

### Mass & Balance Calculations

#### Calculate M&B
```http
POST /calculate/mass-balance
Content-Type: application/json
```

**Request Body**:
```json
{
  "aircraft_registration": "D-EABC",
  "category": "normal",
  "loading_stations": [
    {"name": "Pilot", "weight_kg": 85},
    {"name": "Passenger", "weight_kg": 75},
    {"name": "Baggage", "weight_kg": 20}
  ],
  "fuel": {
    "quantity_l": 100,
    "type": "JET-A1"
  },
  "landing_fuel_l": 30
}
```

**Response** `200 OK`:
```json
{
  "total_weight_kg": 1050.5,
  "takeoff_cg": {
    "position_m": 2.38,
    "within_envelope": true
  },
  "landing_cg": {
    "position_m": 2.41,
    "within_envelope": true
  },
  "zero_fuel_mass_kg": 980.5,
  "warnings": [],
  "status": "OK"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid input data
- `404 Not Found`: Aircraft not found
- `422 Unprocessable Entity`: Validation error

---

### Performance Calculations

#### Calculate Takeoff Performance
```http
POST /calculate/takeoff
Content-Type: application/json
```

**Request Body**:
```json
{
  "aircraft_registration": "D-EABC",
  "weight_kg": 1050,
  "airport": {
    "icao": "EDDF",
    "elevation_ft": 364,
    "runway": "07L"
  },
  "conditions": {
    "qnh_hpa": 1013,
    "temperature_c": 25,
    "wind_direction_deg": 70,
    "wind_speed_kt": 10
  },
  "surface": "asphalt",
  "condition": "dry",
  "safety_factor": 1.3
}
```

**Response** `200 OK`:
```json
{
  "pressure_altitude_ft": 364,
  "density_altitude_ft": 1850,
  "takeoff_roll_m": 450,
  "takeoff_distance_50ft_m": 720,
  "takeoff_distance_with_factor_m": 936,
  "available_tora_m": 3000,
  "headwind_component_kt": 10,
  "crosswind_component_kt": 0,
  "warnings": [],
  "calculation_mode": "table",
  "status": "GO"
}
```

**Warning Types**:
```json
{
  "warnings": [
    {
      "level": "CRITICAL",
      "code": "EXCEEDS_TORA",
      "message": "Takeoff distance exceeds available runway",
      "hazard_ref": "H-07"
    },
    {
      "level": "WARNING",
      "code": "CROSSWIND_LIMIT",
      "message": "Crosswind 18kt exceeds demonstrated limit 15kt",
      "hazard_ref": "H-14"
    },
    {
      "level": "CAUTION",
      "code": "EXTRAPOLATED",
      "message": "Performance data extrapolated beyond POH limits",
      "hazard_ref": "H-11"
    }
  ]
}
```

#### Calculate Landing Performance
```http
POST /calculate/landing
Content-Type: application/json
```

**Request Body**: Similar to takeoff, with `landing_weight_kg`

---

### Weather (Phase 2)

#### Get METAR
```http
GET /weather/metar/{icao}
```

**Response** `200 OK`:
```json
{
  "icao": "EDDF",
  "raw": "EDDF 231450Z 07010KT 9999 FEW040 25/15 Q1013",
  "parsed": {
    "wind_direction_deg": 70,
    "wind_speed_kt": 10,
    "temperature_c": 25,
    "dewpoint_c": 15,
    "qnh_hpa": 1013,
    "visibility_m": 9999
  },
  "observation_time": "2025-01-23T14:50:00Z"
}
```

---

## Error Responses

All errors follow this format:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Weight exceeds MTOM",
    "details": {
      "field": "weight_kg",
      "value": 1300,
      "max": 1200
    }
  }
}
```

**Error Codes**:
| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Input validation failed |
| `NOT_FOUND` | 404 | Resource not found |
| `CALCULATION_ERROR` | 422 | Cannot complete calculation |
| `LIMIT_EXCEEDED` | 422 | Safety limit exceeded |
| `EXTRAPOLATION_BLOCKED` | 422 | Extrapolation beyond 10% limit |

---

## Rate Limiting

> Currently no rate limiting for local deployment.

---

## Versioning

API versioning is path-based: `/api/v1/...`

Breaking changes will increment the version (`/api/v2/...`).

---

> Document Version: 0.1.0
> Last Updated: 2025-01-23
