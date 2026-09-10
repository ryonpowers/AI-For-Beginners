# Paintball Coach

A standalone Vue + Vite app for coaching paintball matches with four connected workflows:

- **Layout Designer** for building and editing bunker, lane, zone, start-box, note, and danger overlays
- **Match Board** for recording points, outcomes, rosters, coach notes, and live field events
- **Heat Map View** for filtering movement, lane pressure, elimination, snap, penalty, and win overlays on the fly
- **Session Review** for comparing points, exporting session data, and reviewing AI-ready coaching insights

## MVP features

- Layered field canvas with a reusable base map and editable tactical objects
- Shared event stream powering live tagging, review, and heat maps
- Local save/load for field layouts
- Local session persistence in the browser
- JSON session export for post-match analysis
- Coach-note parsing that converts plain text into structured tactical tags

## Project setup

```sh
npm install
```

### Compile and hot-reload for development

```sh
npm run dev
```

### Type-check and build for production

```sh
npm run build
```

## Notes

- The app stores layouts and session data in `localStorage`.
- The initial dataset includes a sample field layout and two tagged points so the heat map and review screens render immediately.
- Future AI integrations can attach computer vision for player tracking and language-model tooling for richer note parsing and tactical summaries.
