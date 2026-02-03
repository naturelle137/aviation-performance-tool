# Critical User Journeys (CUJs) for End-to-End Testing

This document defines the primary Critical User Journeys (CUJs) that verify the system's safety and operational integrity. These scenarios serve as the basis for automated End-to-End (E2E) tests using Playwright.

Each scenario is mapped to specific Requirements (REQ-ID) and Hazards (H-ID) to ensure full traceability.

---

## CUJ 1: Standard Mass & Balance Workflow

**Goal**: A pilot loads a standard aircraft profile, enters passenger and fuel loads, and verifies that the Center of Gravity (CG) is within limits for the entire flight duration.

**Relevant Requirements**: [REQ-AC-01], [REQ-MB-01], [REQ-MB-02], [REQ-MB-07], [REQ-FE-02], [REQ-UQ-03]
**Mitigated Hazards**: [H-01], [H-05], [H-12]

**Traceability**:
- **Feature File**: `frontend/tests/e2e/features/mass-balance.feature`
- **Scenario**: "Pilot performs a standard flight preparation"

---

## CUJ 2: Performance under Extreme Conditions (High & Hot)

**Goal**: A pilot checks takeoff performance at a high-elevation airport on a hot day to verify that Density Altitude and Performance Extrapolation logic are correctly applied.

**Relevant Requirements**: [REQ-PF-05], [REQ-PF-13], [REQ-PF-14], [REQ-PF-15]
**Mitigated Hazards**: [H-06], [H-11], [H-13]

**Traceability**:
- **Feature File**: `frontend/tests/e2e/features/performance.feature`
- **Scenario**: "Pilot plans takeoff at high altitude and temperature"

---

## CUJ 3: Hazard Prevention (Intentional Misuse)

**Goal**: A pilot attempts to plan a flight with an aircraft loaded beyond Maximum Takeoff Mass (MTOM) to verify that the system effectively prevents unsafe operations.

**Relevant Requirements**: [REQ-MB-04], [REQ-UI-10], [REQ-UQ-04]
**Mitigated Hazards**: [H-01], [H-05]

**Traceability**:
- **Feature File**: `frontend/tests/e2e/features/mass-balance.feature`
- **Scenario**: "Pilot exceeds MTOM limits"
