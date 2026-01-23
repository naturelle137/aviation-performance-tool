# Frontend - Aviation Performance Tool

Vue 3 frontend for aviation M&B and performance calculations.

## Tech Stack

- **Framework**: Vue 3 + TypeScript
- **Build Tool**: Vite
- **State**: Pinia
- **Styling**: Vanilla CSS

## Quick Start

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

## Project Structure

```
frontend/
├── src/
│   ├── assets/
│   │   └── styles/
│   │       └── main.css      # Global styles
│   ├── components/
│   │   ├── CGEnvelopeChart.vue
│   │   ├── LoadingStation.vue
│   │   └── WarningBanner.vue
│   ├── views/
│   │   ├── MassBalanceView.vue
│   │   ├── PerformanceView.vue
│   │   └── AircraftManagerView.vue
│   ├── services/
│   │   └── api.ts            # API client
│   ├── stores/
│   │   ├── aircraft.ts
│   │   └── calculation.ts
│   ├── App.vue
│   └── main.ts
├── public/
├── index.html
└── vite.config.ts
```

## Development

```bash
# Start dev server (hot reload)
npm run dev

# Type check
npm run type-check

# Lint
npm run lint

# Format
npm run format
```

## Building

```bash
# Production build
npm run build

# Preview production build
npm run preview
```

## Environment Variables

Create `.env.local` for local development:

```env
VITE_API_URL=http://localhost:8000/api/v1
```

## Components

### Core Components

| Component | Purpose | Requirements |
|-----------|---------|--------------|
| `CGEnvelopeChart` | CG envelope visualization | REQ-MB-02, REQ-UI-13 |
| `LoadingStation` | Weight input per station | REQ-MB-01 |
| `WarningBanner` | Safety alerts (blinking) | REQ-PF-09, REQ-UI-10 |

### Design System

Color palette and design tokens defined in `src/assets/styles/main.css`.

**Status Colors**:
- `--color-success`: Green (within limits)
- `--color-warning`: Amber (approaching limits)
- `--color-danger`: Red (exceeds limits)
- `--color-danger-blink`: Blinking red (critical)

---

See [CONTRIBUTING.md](/CONTRIBUTING.md) for development guidelines.
