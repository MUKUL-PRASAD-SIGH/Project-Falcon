# 🦅 Project Falcon — Setup Guide

> **Branch:** `sunidhi`
> Last updated: 2026-07-24

---

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Python | 3.10+ | https://python.org |
| Node.js | 18+ | https://nodejs.org |
| Git | Latest | https://git-scm.com |

---

## 1. Clone & Branch

```bash
git clone https://github.com/MUKUL-PRASAD-SIGH/Project-Falcon.git
cd Project-Falcon
git checkout sunidhi
```

---

## 2. Environment Variables

Copy the sample environment files. Catalyst credentials are optional for the
fully local offline flow:

```bash
cp .env.example .env
cp frontend/.env.example frontend/.env.local
```

Edit `.env`:

```env
# Frontend (Vite)
VITE_API_BASE_URL=http://localhost:8000

# Zoho Catalyst / QuickML (optional)
CATALYST_ORG_ID=60079106947

# QuickML Risk Scoring Endpoint
QUICKML_RISK_URL=https://api.catalyst.zoho.in/quickml/v1/project/<project_id>/endpoints/predict
QUICKML_RISK_KEY=your_quickml_endpoint_key

# QuickML RAG / Chat Endpoint
QUICKML_RAG_URL=https://api.catalyst.zoho.in/quickml/v1/project/<project_id>/endpoints/predict
QUICKML_RAG_KEY=your_quickml_rag_key

# Optional Zia STT gateway
ZIA_STT_URL=
ZIA_STT_KEY=
```

> **Note:** Without Catalyst credentials the app runs fully offline using pre-computed ML artifacts in `ml/outputs/`. No keys are required for local development.

---

## 3. Python Backend

### 3a. Create virtual environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Mac/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3b. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 3c. Generate synthetic dataset (first-time only)

```bash
python data/scripts/generate_synthetic.py
```

This creates:
- `data/scripts/firs_synthetic.json` — 1,000 synthetic Karnataka FIR records
- `data/scripts/accused_synthetic.json` — synthetic accused profiles with co-accused gang networks

### 3d. Run the ML pipeline

```bash
python ml/run_pipeline.py
```

This runs all 6 steps sequentially:
1. **Build Features** — generates `data/processed/accused_features.csv` (800 unique profiles)
2. **DBSCAN Clustering** — generates `ml/outputs/clusters.geojson`
3. **TF-IDF Similarity** — generates `ml/outputs/similarity_index.json`
4. **NetworkX Gang Graph** — generates `ml/outputs/gang_network.json`
5. **SARIMA Forecasting** — generates `ml/outputs/forecasts.json`
6. **QuickML Risk Scoring** — generates `ml/outputs/offender_risk_scores.json` (800 accused, unique metrics)

### 3e. Start the backend

```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend runs at: **http://localhost:8000**
API docs (Swagger): **http://localhost:8000/docs**

---

## 4. React Frontend

```bash
cd frontend
npm install
npm run lint
npm run dev
```

Frontend runs at: **http://localhost:5173**

---

## 5. Key Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/stats` | Dashboard KPI metrics |
| `GET /api/districts` | District risk stats (cached) |
| `GET /api/clusters` | DBSCAN crime heatmap clusters |
| `GET /api/offender/risk/{id}` | Accused risk profile (unique per ID) |
| `GET /api/cases/similar?case_id={id}` | TF-IDF similar FIR cases |
| `GET /api/graph/accused/{id}` | Co-accused network subgraph |
| `GET /api/anomalies` | QuickML flagged FIR anomalies |
| `GET /api/forecast` | SARIMA 7d/30d crime forecast |
| `POST /api/chat/query` | FALCON AI chat (RAG + LLM) |
| `POST /api/voice/transcribe` | Optional Zia STT gateway with typed-input fallback |
| `POST /api/export/pdf` | Local evidence-trail PDF export |

---

## 5a. Catalyst AppSail Deployment

The repository now includes an AppSail service entry in `catalyst.json` and a
root `app-config.json`. Configure secrets in Catalyst rather than committing
them, then deploy from the project root:

```bash
npm --prefix frontend run build
catalyst deploy
```

Set the deployed AppSail URL as `VITE_API_BASE_URL` before building the client.
The local offline fallback remains available when the optional Catalyst keys are
not configured.

---

## 6. Project Structure

```
Project-Falcon/
├── backend/                # FastAPI backend
│   ├── main.py             # App entry + cache warm-up
│   ├── auth/               # JWT + RBAC middleware
│   └── routers/            # One file per feature area
│       ├── risk.py         # Accused risk profiles
│       ├── graph.py        # Co-accused network
│       ├── clusters.py     # Crime heatmap
│       ├── similarity.py   # TF-IDF case similarity
│       ├── forecast.py     # SARIMA forecasting
│       └── chat.py         # RAG AI chat
│
├── frontend/               # React + Vite frontend
│   └── src/
│       ├── api/endpoints.js        # All API call functions
│       ├── components/
│       │   ├── Profiles/           # Accused suspect profiles
│       │   │   └── ProfilesExplorer.jsx
│       │   ├── NetworkGraph.jsx    # Cytoscape co-accused graph
│       │   ├── CrimeMap.jsx        # Leaflet heatmap
│       │   ├── Dashboard/          # KPI command centre
│       │   └── Chat/               # AI chat interface
│       └── hooks/
│
├── ml/
│   ├── run_pipeline.py     # Master pipeline runner (run this first)
│   ├── models/             # ML model implementations
│   └── outputs/            # Pre-computed artifacts (committed)
│       ├── offender_risk_scores.json   # 800 unique risk profiles
│       ├── similarity_index.json
│       ├── gang_network.json
│       └── forecasts.json
│
├── data/
│   ├── scripts/
│   │   └── generate_synthetic.py   # Synthetic KSP dataset generator
│   ├── raw/                # Generated JSON datasets
│   └── processed/
│       └── accused_features.csv    # 800 ML feature rows (grouped by AccusedMasterID)
│
└── docs/
    └── master_plan.md      # Full project phase plan
```

---

## 7. What Was Fixed in This Branch

### Bug: All Accused Profiles Showing Identical Metrics
**Symptoms:** Every profile card showed `Prior Offenses: 2`, `Recency: 45d`, `Level 4/5`, `3 members`.

**Root cause (3-layer bug):**

1. **`ml/scripts/build_features.py`** — grouped accused by `AccusedName` instead of `AccusedMasterID`, collapsing 800 unique profiles into 118 names. IDs like `101`, `808` weren't in the CSV and fell through to a hardcoded fallback.

2. **`ml/models/quickml_risk_anomaly.py`** — the risk JSON export was missing `recency_days`, `max_crime_severity`, and `co_accused_count` fields.

3. **`frontend/src/api/endpoints.js`** — `fetchRiskScore` returned the full `{ status, data: {...} }` envelope but the component read `riskData.prior_offense_count` expecting the inner object. Since `prior_offense_count` was `undefined`, the `?? 2`, `?? 45` etc. defaults always kicked in.

**Fix:**
```js
// endpoints.js — unwrap the nested data
export const fetchRiskScore = (accusedId) =>
  client.get(`/api/offender/risk/${accusedId}`).then((r) => r.data?.data ?? r.data)
```

### Bug: Network Graph Crash
**Fix:** Replaced `react-cytoscapejs` with native `cytoscape` canvas management in `NetworkGraph.jsx` to fix `TypeError: Cannot read properties of null (reading 'notify')` in React 18 strict mode.

### Feature: Unique Co-Accused Gang Networks
Overhauled `generate_synthetic.py` and `network.py` to create realistic Karnataka co-accused gang structures with distinct Louvain community detection output per accused.

### Feature: Realistic FIR Narratives
Dynamic multi-pattern authentic police narrative generator for Theft, Robbery, Assault, Cybercrime, Fraud, Narcotics, Homicide with randomised Indian names, Karnataka localities, vehicle models, bank names, and M.O. details.

---

## 8. Credentials for Demo Login

| Role | Email | Password |
|------|-------|----------|
| Admin | `admin@ksp.gov.in` | `admin123` |
| Investigator | `investigator@ksp.gov.in` | `falcon123` |
| Analyst | `analyst@ksp.gov.in` | `analyst123` |

---

*Project Falcon v2 · 100% Catalyst-Native · KSP Hackathon 2025*
