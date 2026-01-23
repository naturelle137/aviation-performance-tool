# Branching Strategy - Aviation Performance Tool

This project follows a **Release-Focused Flow** optimized for stability and point releases, suitable for safety-critical aviation software.

## Branch Types

```
main (production)          ← Only stable, tagged releases live here
  │
  ├── release/1.0.x        ← Stabilization branch for v1.0 series
  │     ├── hotfix/1.0.1-fix-cg-calc
  │     └── hotfix/1.0.2-unit-conversion
  │
  ├── release/1.1.x        ← Next point release series
  │
develop                    ← Integration branch for next release
  │
  ├── feature/mb-core      ← Feature development
  ├── feature/perf-engine
  └── feature/metar-fetch
```

---

## Branch Descriptions

| Branch | Purpose | Merges To | Lifetime |
|--------|---------|-----------|----------|
| `main` | Production-ready code only. Each commit is a tagged release. | — | Permanent |
| `develop` | Integration branch for completed features. | `release/*` | Permanent |
| `release/X.Y.x` | Stabilization for version X.Y. Bug fixes only, no new features. | `main`, `develop` | Until EOL |
| `feature/*` | New feature development. | `develop` | Until merged |
| `hotfix/*` | Critical production fixes. | `release/*`, `main`, `develop` | Until merged |

---

## Workflow

### 1. Feature Development
```bash
# Create feature branch from develop
git checkout develop
git pull origin develop
git checkout -b feature/mb-core

# Work on feature...
git commit -m "Implement M&B calculation service"

# When complete, open PR to develop
git push origin feature/mb-core
# → Create Pull Request: feature/mb-core → develop
```

### 2. Preparing a Release
```bash
# When develop is ready for release
git checkout develop
git pull origin develop
git checkout -b release/1.0.x

# Only bug fixes allowed here, no new features
# Update version numbers, changelogs, etc.
git commit -m "Prepare release 1.0.0"
```

### 3. Publishing a Release
```bash
# After QA approval on release branch
git checkout main
git merge release/1.0.x --no-ff
git tag -a v1.0.0 -m "Release 1.0.0: MVP with M&B and Performance Engine"
git push origin main --tags

# Back-merge to develop
git checkout develop
git merge release/1.0.x --no-ff
git push origin develop
```

### 4. Hotfix (Critical Production Bug)
```bash
# Branch from the release branch (not main)
git checkout release/1.0.x
git checkout -b hotfix/1.0.1-fix-cg-calc

# Fix the bug
git commit -m "Fix CG calculation for variable arm interpolation"

# Merge back to release branch
git checkout release/1.0.x
git merge hotfix/1.0.1-fix-cg-calc --no-ff
git tag -a v1.0.1 -m "Hotfix: CG calculation fix"
git push origin release/1.0.x --tags

# Also merge to main and develop
git checkout main
git merge release/1.0.x --no-ff
git push origin main

git checkout develop
git merge release/1.0.x --no-ff
git push origin develop
```

---

## Version Numbering (Semantic Versioning)

```
vMAJOR.MINOR.PATCH
  │     │     └── Bug fixes, hotfixes (1.0.1, 1.0.2)
  │     └── New features, backward compatible (1.1.0, 1.2.0)
  └── Breaking changes, major rewrites (2.0.0)
```

| Change Type | Example | Branch Origin |
|-------------|---------|---------------|
| Hotfix | 1.0.0 → 1.0.1 | `hotfix/*` from `release/1.0.x` |
| Point Release | 1.0.2 → 1.1.0 | Features merged to `develop`, then `release/1.1.x` |
| Major Release | 1.x → 2.0.0 | `develop` with breaking changes |

---

## Protected Branch Rules (GitHub Settings)

Configure these rules in **Settings → Branches → Branch protection rules**:

### `main`
- ✅ Require pull request reviews (1 approval minimum)
- ✅ Require status checks to pass (CI/Tests)
- ✅ Require branches to be up to date
- ✅ Require signed commits (recommended for aviation software)
- ✅ Do not allow force pushes
- ✅ Do not allow deletions

### `develop`
- ✅ Require pull request reviews
- ✅ Require status checks to pass
- ❌ Allow force pushes (for rebasing feature branches)

### `release/*`
- ✅ Require pull request reviews
- ✅ Require status checks to pass
- ❌ Allow maintainers to push directly (for version bumps)

---

## Release Cycle (Recommended)

```
Week 1-3: Feature development on feature/* branches
Week 4:   Feature freeze, create release/X.Y.x branch
Week 5:   QA and stabilization (bug fixes only)
Week 6:   Release to main, tag, deploy
```

For aviation software, consider:
- **Extended QA cycles** for safety-critical features
- **Beta releases** (`v1.0.0-beta.1`) for pilot testing
- **Long-Term Support (LTS)** branches for production stability

---

## Quick Reference Commands

```bash
# Start new feature
git checkout develop && git pull && git checkout -b feature/my-feature

# Finish feature (via PR)
git push origin feature/my-feature
# Open PR: feature/my-feature → develop

# Create release branch
git checkout develop && git pull && git checkout -b release/1.1.x

# Tag and release
git checkout main && git merge release/1.1.x --no-ff
git tag -a v1.1.0 -m "Release 1.1.0"
git push origin main --tags

# Emergency hotfix
git checkout release/1.0.x && git checkout -b hotfix/1.0.3-urgent-fix
# ... fix and merge back
```

---

> **Philosophy**: "Stable first, features second. Every release to `main` must be flight-ready."
