# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
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
- None

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
