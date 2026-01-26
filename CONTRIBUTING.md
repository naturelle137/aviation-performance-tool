# Contributing to Aviation Performance Tool

Welcome! This document outlines how to contribute to the Aviation Performance Tool while maintaining the safety-critical standards required for aviation software.

## 🛡️ Safety-First Development Philosophy

> "Software calculates, the pilot decides – the documentation ensures that the basis for the calculation is correct."

This is **safety-critical aviation software**. Every contribution must:
1. **Trace to Requirements**: Link code changes to specific REQ-IDs
2. **Consider Hazards**: Check the Safety Traceability Matrix for affected hazards
3. **Prioritize Correctness**: Prefer correct over fast, tested over clever

---

## 📋 Before You Start

1. **Read the Requirements**: [docs/requirements/initial_requirements.md](docs/requirements/initial_requirements.md)
2. **Review the Safety Matrix**: [docs/requirements/safety_traceability_matrix.md](docs/requirements/safety_traceability_matrix.md)
3. **Understand the Branching Strategy**: [docs/development/BRANCHING_STRATEGY.md](docs/development/BRANCHING_STRATEGY.md)

---

## 🔀 Branching Workflow

```
main              ← Production only, tagged releases
develop           ← Integration branch
feature/*         ← New features
hotfix/*          ← Critical production fixes
release/X.Y.x     ← Release stabilization
```

### Starting Work
```bash
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name
```

### Naming Conventions
| Branch Type | Pattern | Example |
|-------------|---------|---------|
| Feature | `feature/<component>-<description>` | `feature/mb-variable-arm-interpolation` |
| Hotfix | `hotfix/<version>-<description>` | `hotfix/1.0.1-cg-calc-fix` |
| Release | `release/<major>.<minor>.x` | `release/1.0.x` |

---

## 📝 Conventional Commits

We use **Conventional Commits** for clear, machine-readable commit history.

### Format
```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Types
| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature | `feat(mb): add variable arm interpolation` |
| `fix` | Bug fix | `fix(perf): correct density altitude formula` |
| `docs` | Documentation only | `docs: update API documentation` |
| `test` | Adding/updating tests | `test(mb): add CG migration boundary tests` |
| `refactor` | Code restructuring | `refactor(core): extract unit conversion service` |
| `chore` | Maintenance tasks | `chore: update dependencies` |
| `safety` | Safety-critical changes | `safety(perf): implement extrapolation penalty` |

### Scopes
| Scope | Area |
|-------|------|
| `mb` | Mass & Balance |
| `perf` | Performance calculations |
| `ac` | Aircraft management |
| `wx` | Weather integration |
| `ui` | User interface |
| `api` | Backend API |
| `core` | Core services/utilities |

### Requirement Traceability in Commits

**Always reference the REQ-ID in commits that implement requirements:**

```bash
# Good
git commit -m "feat(mb): implement point-in-polygon CG validation

Implements REQ-MB-06 for polygonal envelope support.
Mitigates H-05 (CG migration hazard)."

# Bad
git commit -m "fixed some CG stuff"
```

### Breaking Changes
```bash
git commit -m "feat(api)!: change aircraft profile schema

BREAKING CHANGE: fuel_tanks is now an array of objects instead of a single object.
Migration script provided in scripts/migrate-v2.py"
```

---

## ✅ Quality Gates

### Gate 1: Local Development
**Enforced by Git Hooks (Husky)**
Before pushing, the following checks runs automatically via `.husky/pre-push`:
1.  **Code Compilation**: Compilation flow checks.
2.  **Linting**:
    *   Frontend: `npm run lint`
    *   Frontend Type Check: `npm run type-check`
    *   Backend: `ruff check` (if python files present)
3.  **Tests**:
    *   Frontend: `npm run test:coverage` (Threshold: 75% Global, **90% for P1 Components**)
    *   Backend: `pytest -m p1 --cov-fail-under=90` (Strict 90% coverage for P1/Safety)

**Setup:**
Run `npm install` in the root directory to activate hooks.

**IMPORTANT:** Using `git push --no-verify` to bypass these checks is **strictly prohibited**. Broken quality gates must be fixed locally before pushing.

### Gate 2: Pull Request
Required for merge to `develop`:
- [ ] All CI checks pass
- [ ] Code review approved (1 reviewer minimum)
- [ ] REQ-ID referenced in PR description
- [ ] Safety implications documented (if applicable)

### Gate 3: Release Branch
Required for merge to `main`:
- [ ] All unit tests pass (>90% coverage for P1 requirements)
- [ ] Integration tests pass
- [ ] Safety-critical tests pass (H-01 through H-14)
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] Version number bumped

### Test Coverage Requirements

| Priority | Minimum Coverage | Testing Level |
|----------|------------------|---------------|
| **P1** (Safety) | 90% | Unit + Integration + Safety Stress Tests |
| **P2** (Operational) | 80% | Unit + Integration |
| **P3** (Comfort) | 70% | Unit |

---

## 🧪 Testing Standards

### Test File Naming
```
tests/
├── unit/
│   ├── test_mass_balance.py
│   ├── test_performance.py
│   └── test_unit_conversion.py
├── integration/
│   └── test_calculation_flow.py
└── safety/
    ├── test_hazard_h01_unit_confusion.py
    ├── test_hazard_h05_cg_migration.py
    └── test_hazard_h11_extrapolation.py
```

### Safety Test Requirements
Every hazard in the Safety Traceability Matrix must have:
1. **At least one dedicated test case**
2. **Edge-case stress tests** (see "Edge-Case Test Scenarios" in safety matrix)
3. **Clear assertion messages**

Example:
```python
def test_h05_cg_migration_alert():
    """
    Hazard H-05: Takeoff within limits, but Landing outside CG limits.
    Mitigated by: REQ-MB-10, REQ-MB-07
    """
    # Setup: Aircraft with significant fuel CG shift
    aircraft = create_test_aircraft_kl107()
    
    # Takeoff CG should be within limits
    takeoff_cg = calculate_cg(aircraft, fuel=100)
    assert is_within_envelope(takeoff_cg), "Takeoff CG should be valid"
    
    # Landing CG (zero fuel) should trigger warning
    landing_cg = calculate_cg(aircraft, fuel=0)
    assert not is_within_envelope(landing_cg), "Landing CG should exceed limits"
    assert get_warning_level() == "CRITICAL", "H-05 hazard must trigger critical alert"
```

---

## 📖 Pull Request Process

### PR Title Format
```
<type>(<scope>): <description> [REQ-XX-YY]
```
Example: `feat(mb): add CG envelope visualization [REQ-MB-02]`

### PR Description Template
```markdown
## Summary
Brief description of changes.

## Requirements Implemented
- REQ-MB-02: Real-time CG envelope chart

## Safety Considerations
- [ ] Reviewed Safety Traceability Matrix
- [ ] No new hazards introduced
- [ ] Existing mitigations preserved

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing performed

## Documentation
- [ ] API docs updated (if applicable)
- [ ] README updated (if applicable)
- [ ] Changelog entry added
```

---

## 📁 Code Style

### Python (Backend)
- Formatter: `black`
- Linter: `ruff`
- Type hints: Required for all public functions
- Docstrings: Google style

### TypeScript (Frontend)
- Formatter: `prettier`
- Linter: `eslint`
- Strict mode enabled

### Naming Conventions
| Element | Style | Example |
|---------|-------|---------|
| Python functions | snake_case | `calculate_density_altitude()` |
| Python classes | PascalCase | `MassBalanceService` |
| TypeScript functions | camelCase | `calculateDensityAltitude()` |
| TypeScript components | PascalCase | `CgEnvelopeChart.vue` |
| Constants | SCREAMING_SNAKE | `MAX_EXTRAPOLATION_PERCENT` |
| REQ-IDs | REQ-XX-YY | `REQ-MB-06` |

---

## 🚨 Safety-Critical Code Guidelines

### P1 Requirements (Safety-Critical)
Code implementing P1 requirements must:
1. **Have comprehensive test coverage** (90%+)
2. **Include defensive programming** (input validation, range checks)
3. **Never silently fail** – always raise explicit errors
4. **Log all safety-relevant decisions**

### Example: Defensive Implementation
```python
def calculate_takeoff_distance(
    weight_kg: float,
    pressure_altitude_ft: float,
    temperature_c: float
) -> float:
    """
    Calculate takeoff distance required.
    
    Implements: REQ-PF-01, REQ-PF-23
    Mitigates: H-06, H-07
    """
    # Input validation (REQ-UI-11)
    if not 0 < weight_kg <= 2000:
        raise ValueError(f"Weight {weight_kg}kg outside valid range")
    if not -2000 <= pressure_altitude_ft <= 15000:
        raise ValueError(f"Pressure altitude {pressure_altitude_ft}ft outside valid range")
    if not -40 <= temperature_c <= 50:
        raise ValueError(f"Temperature {temperature_c}°C outside valid range")
    
    # Calculation logic...
    result = _interpolate_poh_data(weight_kg, pressure_altitude_ft, temperature_c)
    
    # Minimum distance rule (REQ-PF-17, mitigates H-13)
    return max(result, POH_MINIMUM_DISTANCE)
```

---

## 📞 Getting Help

- **Questions about requirements**: Open a discussion in GitHub Discussions
- **Bug reports**: Use the bug report issue template
- **Feature requests**: Use the feature request issue template
- **Security vulnerabilities**: Email directly (do not open public issues)

---

Thank you for contributing to aviation safety! ✈️
