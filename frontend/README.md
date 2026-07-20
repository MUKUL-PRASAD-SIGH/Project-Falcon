# Project Falcon &mdash; Frontend Scaffold

This is a placeholder-data skeleton of the Catalyst Slate frontend described in
`docs/master_plan.md`. It's meant to drop straight into your monorepo at `/frontend`
and give the team something clickable on day 0, before any backend/API is live.

## Run it

```bash
cd frontend
npm install
npm run dev
```

Opens at `localhost:5173`.

## What's in here

- **Command Center** (`/`) &mdash; stat cards, forecast chart slot, live anomaly feed slot, district risk table
- **Intelligence Chat** (`/chat`) &mdash; chat UI with mandatory FIR citation chips (Req #9 Evidence Trail), voice/language toggle stubs
- **Crime Map** (`/map`) &mdash; filter sidebar + Leaflet mount point + pulsing spike-zone markers
- **Network Graph** (`/network`) &mdash; Cytoscape mount point, node-type legend, accused profile card slot
- **Audit & Access** (`/admin`) &mdash; RBAC-gated route (only renders for `Admin` role), audit log table, masked/unmasked victim data demo

Switch roles in the top-right selector to see the RBAC gate on `/admin` react live &mdash;
this is a placeholder for the real Catalyst Authentication route guard from step 4.6.

## Not wired up yet (by design)

- No real API calls &mdash; everything is mock/seed data inline in each component
- `react-leaflet`, `cytoscape`/`react-cytoscapejs`, `echarts-for-react` aren't installed yet;
  install them when you build the real map/graph/chart layers (steps 4.2&ndash;4.4)
- No Catalyst Auth / JWT &mdash; the role selector is local React state only
- No Zia STT/TTS &mdash; the mic and language toggle buttons are inert

## Design notes

Palette and type are a deliberate "KSP command console" identity, not a generic dashboard theme:

- **Navy** (`#0B1526` / `#131F38`) grounds it as an operations console, not a marketing page
- **Gold** (`#C9A227`) references police insignia/braid, used only for active states and emphasis
- **Khaki** (`#A98E5C`) is a secondary data accent, nodding to the uniform
- **Alert red** (`#D8503A`) is reserved for anomalies/risk only &mdash; never decorative
- Headings use **Oswald** (condensed, official-looking), body text uses **Inter**, and every
  FIR number / case ID / timestamp renders in **IBM Plex Mono** as a recurring "evidence tag"
  motif &mdash; this ties directly into the Evidence Trail requirement (#9) so citations look the
  same whether they're in chat, on the map, in the graph, or in the audit log
- The badge in the top-left has a slow radar-sweep animation &mdash; the one deliberate flourish,
  everything else is intentionally quiet
