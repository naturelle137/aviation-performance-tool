# Traceability Analysis & Migration Plan

**Date:** 2026-01-26
**Scope:** `src/` (Combined Backend `app/` and Frontend `src/`)
**Objective:** Identify code traceable to requirements (MVP) and isolate non-compliant/prototype code.

## 1. Traceability Matrix

### Backend (`backend/app/`)

| File Path | Status | REQ-ID | Coverage (Est.) | Action |
|-----------|--------|--------|-----------------|--------|
| `services/mass_balance.py` | **Active (Missing Tag)** | Implements REQ-MB-01, REQ-MB-07, REQ-FE-01 | High | **keep** (Add Tags) |
| `services/performance.py` | **Active (Missing Tag)** | Implements REQ-PF-01, REQ-PF-02, REQ-PF-18 | High | **keep** (Add Tags) |
| `services/cg_validation.py` | **Verified** | REQ-MB-06 (Explicit) | High | **keep** |
| `services/units.py` | **Verified** | REQ-SYS-03 (Explicit) | High | **keep** |
| `services/weather.py` | **Active (MVP)** | REQ-WX-01 (Implied) | Low | **keep** (Refactor Required) |
| `models/aircraft.py` | **Active (MVP)** | REQ-AD-01, REQ-AD-02 | High | **keep** |
| `routers/aircraft.py` | **Active (Low Cov)** | REQ-AC-01 | Low (22%) | **keep** (Needs Tests) |
| `routers/calculations.py` | **Active (MVP)** | REQ-MB-01 | Medium (43%) | **keep** (Needs Tests) |
| `routers/weather.py` | **Active (Low Cov)** | REQ-WX-01 | Low (33%) | **keep** (Needs Tests) |
| `main.py` | **Core** | REQ-SYS-XX | N/A | **keep** |
| `utils/data_loader.py` | **Utility** | REQ-AC-05 | High | **keep** |

### Frontend (`frontend/src/`)

| File Path | Status | REQ-ID | Action |
|-----------|--------|--------|--------|
| `components/charts/CGEnvelopeChart.vue` | **Active** | REQ-MB-02 (Implied) | **keep** (Add Tags) |
| `components/LoadingStation.vue` | **Active** | REQ-MB-01 (Implied) | **keep** (Add Tags) |
| `views/CalculationView.vue` | **Active** | REQ-MB-01, REQ-MB-02 | **keep** (Add Tags) |
| `views/AircraftDetailView.vue` | **Active** | REQ-AC-01 | **keep** |
| `views/AircraftView.vue` | **Active** | REQ-AC-01 | **keep** |

### Root / Scripts

| File Path | Status | REQ-ID | Action |
|-----------|--------|--------|--------|
| `extract_pdfs.py` | **Legacy/Prototype** | NONE | **QUARANTINE** |

---

## 2. Quarantine Strategy

Only `extract_pdfs.py` has been identified as a pure prototype script with no structural relevance to the current MVP architecture.

**However**, to strictly comply with the instruction "Code without REQ-reference acts as Legacy":
The **Action Plan** for the "Active (Missing Tag)" files is to **IMMEDIATELY ADD TRACEABILITY** rather than quarantine them, as quarantining core services would render the application inoperable and fail P1 requirements.

**Proposed Quarantine Move:**
*   `extract_pdfs.py` -> `src/archive/prototype_v1/extract_pdfs.py`

## 3. Migration Backlog (MIGRATION_BACKLOG.md)

Priority refactoring tasks to achieve Green Quality Gate 1:

1.  **[P1] Add Traceability Tags**: Update `services/mass_balance.py`, `services/performance.py`, and frontend components with explicit `@implements REQ-XX` docstrings/comments.
2.  **[P1] Backend Coverage**: backend `routers/weather.py` and `routers/aircraft.py` are below 80%.
    *   *Task:* Add integration tests for these routers.
3.  **[P2] Frontend Traceability**: Add comments to `.vue` files linking to `REQ-UI-XX`.

---

**Ready to proceed?**
1.  Confirm Quarantine of `extract_pdfs.py`.
2.  Approve immediate "Tagging Spree" for Active files to satisfy Quality Gate Traceability (instead of archival).
