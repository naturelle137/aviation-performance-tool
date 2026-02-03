# Contributing to Aviation Performance Tool

Welcome! This document outlines how to contribute to the Aviation Performance Tool while maintaining the safety-critical standards required for aviation software.

## 🛡️ Safety-First Development Philosophy

> "Software calculates, the pilot decides – the documentation ensures that the basis for the calculation is correct."

This is **safety-critical aviation software**. Every contribution must:
1. **Trace to Requirements**: Link code changes to specific REQ-IDs
2. **Consider Hazards**: Check the Safety Traceability Matrix for affected hazards
3. **Prioritize Correctness**: Prefer correct over fast, tested over clever
4. **Respect Priority Isolation**: P1 code must never depend on P2/P3 code

---

## 📋 Before You Start

1. **Read the Requirements**: [docs/requirements/initial_requirements.md](docs/requirements/initial_requirements.md)
2. **Understand Priority Architecture**: [docs/architecture/ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md)
3. **Review the Safety Matrix**: [docs/requirements/safety_traceability_matrix.md](docs/requirements/safety_traceability_matrix.md)
4. **Understand the Branching Strategy**: [docs/development/BRANCHING_STRATEGY.md](docs/development/BRANCHING_STRATEGY.md)

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

## ✅ Quality Gates (3-Tier System)

Every PR must pass **3 automated quality gates** in CI, aligned with the [Priority Definitions](docs/requirements/initial_requirements.md):

| Gate | Priority | Coverage | Files | Enforcement |
|------|----------|----------|-------|-------------|
| **Gate 1** | P1 (Critical/Safety) | $90\%$ | `services/*/core.py`, `units.py`, `cg_validation.py` | **Blocks merge** |
| **Gate 2** | P2 (Operational) | $80\%$ | `services/*/logic.py`, `weather.py`, `routers/` | **Blocks merge** |
| **Gate 3** | P3 (Global Baseline) | $70\%$ | All `backend/app/` | **Blocks merge** |

> [!IMPORTANT]
> Gate 3 is a **gapless catch-all**: any P3 component not explicitly covered by Gates 1 or 2 is automatically included in the $70\%$ global threshold.

### Local Development (Pre-Push)

Before pushing, the `.husky/pre-push` hook runs automatically:

1. **Frontend Type Check**: `npm run type-check`
2. **Frontend Tests**: `npm run test:coverage`
3. **Backend P1 Gate**: $90\%$ coverage for `core.py`, `units.py`, `cg_validation.py`
4. **Backend Global Gate**: $70\%$ coverage for `backend/app/`

> [!NOTE]
> P2 Gate ($80\%$) is validated **only in CI** to optimize local push times.

**Setup:**
```bash
npm install  # Activates Husky hooks
```

> [!CAUTION]
> Using `git push --no-verify` to bypass these checks is **strictly prohibited**. Broken quality gates must be fixed locally before pushing.

### Pull Request (CI Gates)

Required for merge to `develop`:
- [ ] All 3 CI quality gates pass
- [ ] Import-linter passes (P1 isolation check)
- [ ] Code review approved (1 reviewer minimum)
- [ ] REQ-ID referenced in PR description
- [ ] Safety implications documented (if applicable)

### Release Branch

Required for merge to `main`:
- [ ] All unit tests pass ($90\%$+ coverage for P1)
- [ ] Integration tests pass
- [ ] Safety-critical tests pass (H-01 through H-14)
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] Version number bumped

---

## 🏗️ P1 Architectural Constraints

Code in **P1 modules** (`core.py`, `units.py`, `cg_validation.py`) must:

1. **Be side-effect free**: Pure functions only – deterministic output for given input
2. **Have no I/O**: No file reads, no database calls, no HTTP requests
3. **Have no mutable state**: No global variables, no class instance state
4. **Never import from P2/P3**: Import only standard library and approved packages

> [!CAUTION]
> **Import Direction Rule**: P1 → ✗ P2/P3. This is enforced by `import-linter` in CI. See [.importlinter](/.importlinter).

Example of compliant P1 code:
```python
# services/mass_balance/core.py (P1)
from app.services.units import Kilogram, Meter, KilogramMeter

def calculate_moment(weight: Kilogram, arm: Meter) -> KilogramMeter:
    """Pure function. REQ-MB-11."""
    return KilogramMeter(weight * arm)  # No I/O, no state
```

Example of **non-compliant** P1 code:
```python
# ❌ WRONG: P1 module importing from P2
from app.services.weather import fetch_metar  # Import-linter will fail!
```

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

### Priority Markers

Use pytest markers to categorize tests by priority:

```python
@pytest.mark.p1
@pytest.mark.safety
def test_cg_outside_envelope_triggers_warning():
    """REQ-MB-03: Visual warning for out-of-envelope CG."""
    ...

@pytest.mark.p2
def test_metar_auto_populates_temperature():
    """REQ-WX-02: Auto-populate from METAR."""
    ...
```

### Safety Test Requirements

Every hazard in the Safety Traceability Matrix must have:
1. **At least one dedicated test case**
2. **Edge-case stress tests**
3. **Clear assertion messages referencing H-XX**

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
- [ ] P1 isolation maintained (no new P2/P3 imports in core.py)

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
1. **Have comprehensive test coverage** ($90\%$+)
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
