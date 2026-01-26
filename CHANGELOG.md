# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Implemented Aircraft data model (REQ-AD-01, REQ-AD-02) including fuel tanks and weight stations
- Implemented Fuel Density Map (REQ-FE-01) supporting AvGas, Jet-A1, Mogas types (Mitigates H-02)
- Implemented Unit Conversion Service (REQ-SYS-03) handling hybrid Imperial/Metric inputs
- Added `CGEnvelopeChart` component (REQ-MB-02) with real-time visualization
- Added `LoadingStation` component (REQ-AD-09) with dynamic weight input
- Added `CalculationView` (REQ-MB-01) orchestrating full M&B workflow
- Project documentation structure
- Requirements specification with EARS syntax (`initial_requirements.md`)
- Safety Traceability Matrix with hazard log (`safety_traceability_matrix.md`)
- Branching strategy documentation (`BRANCHING_STRATEGY.md`)
- Contribution guidelines with conventional commits (`CONTRIBUTING.md`)
- Technical documentation suite:
  - Architecture documentation (`ARCHITECTURE.md`)
  - REST API documentation (`API.md`)
  - Testing strategy and requirements (`TESTING.md`)
- Component-level documentation (`backend/README.md`, `frontend/README.md`)
- Priority system (P1-P3) for requirements

### Changed
- Updated .gitignore to exclude internal scripts

### Security
- Implemented Mass Balance Calculation (REQ-MB-01) with precise moment arms
- Implemented Migration Check (REQ-MB-07, REQ-MB-10) to detect hazardous CG shifts during flight (Mitigates H-05, H-12)
- Implemented Performance Calculation (REQ-PF-01) supporting Mode B FSM 3/75 fallback (Mitigates H-07)
- Implemented Density Altitude Calculation (REQ-PF-05) to prevent accidents in "Hot & High" conditions (Mitigates H-06)
- Implemented Input Validation (REQ-UI-11) for physical plausibility limits
- Implemented FSM 3/75 Correction Factors (REQ-PF-18) for surface and slope impacts (Mitigates H-08)

---

## Version History

### Release Naming Convention
- `vMAJOR.MINOR.PATCH` (e.g., v1.0.0)
- Pre-releases: `v1.0.0-beta.1`, `v1.0.0-rc.1`

### Priority Mapping
| Priority | Changelog Section |
|----------|-------------------|
| P1 (Safety) | **Security** or **Fixed** |
| P2 (Operational) | **Added** or **Changed** |
| P3 (Comfort) | **Added** |

---

## Template for Future Releases

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New features (P2/P3 requirements)

### Changed
- Changes to existing functionality

### Deprecated
- Features that will be removed in future versions

### Removed
- Features removed in this version

### Fixed
- Bug fixes (reference hazard IDs if applicable)

### Security
- Security-related changes (P1 requirements, hazard mitigations)
```

---

[Unreleased]: https://github.com/naturelle137/aviation-performance-tool/compare/main...develop
