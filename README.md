<div align="center">
  <img src="https://img.shields.io/badge/Zoho_Catalyst-Native_Architecture-0066FF?style=for-the-badge&logo=zohocrm&logoColor=white" alt="Zoho Catalyst Native" />
  <img src="https://img.shields.io/badge/React_18-SPA-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React 18" />
  <img src="https://img.shields.io/badge/FastAPI-AppSail-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <br />
  <h1>Project Falcon</h1>
  <p><strong>Karnataka State Police (KSP) Hackathon 2025 | Problem Statement 2</strong></p>
</div>

<hr/>

## 🎯 Project Overview
**Project Falcon** — *Named for its speed, precision, and high-altitude overview of criminal networks, enabling rapid and targeted law enforcement interventions.*

Project Falcon is a sophisticated, 100% **Zoho Catalyst-native** intelligence platform built for law enforcement agencies. Designed to meet the precise requirements of KSP Hackathon PS2, Project Falcon transforms raw FIR and case data into actionable, real-time insights without relying on a single external third-party AI API.

By leveraging Catalyst QuickML, Zia Services, AppSail, and DataStore, the platform offers an end-to-end investigative ecosystem tailored for deep criminal analysis and spatial forecasting.

## 🚀 Core Features & Capabilities

### 1. The Intelligence Orchestrator (Conversational UI)
Not just a chatbot, but a routing engine triggered by Natural Language.
*   **NL-to-SQL Pipeline:** Schema-aware Catalyst QuickML dynamically translates plain English (and Kannada) into complex SQL joins across 28 relational tables.
*   **RAG Knowledge Base:** Retrieves BriefFacts using QuickML vector store.
*   **Explainable AI (Evidence Trail):** Every AI response cites explicit FIR numbers (satisfying Requirement #9).
*   **Multi-Language Voice IO:** Kannada and English speech-to-text, translation, and text-to-speech handled entirely by **Zia Services**.

### 2. Six-Pillar ML Analytics Engine
*   **M1: Geospatial Detection (DBSCAN & K-Means):** Identifies geographical crime hotspots overlaid with district boundaries.
*   **M2: Repeat Offender Risk (Zia AutoML):** Tabular classification grading offenders with a 0-100 risk score based on historical and demographic data (AUC-ROC >0.75).
*   **M3: Crime Forecasting (SARIMA):** Time-series forecasting for 7-day and 30-day district-level crime volume predictions.
*   **M4: Anomaly Detection (Isolation Forest):** Flags irregular FIRs and investigative outliers.
*   **M5: Criminal Network Discovery (Louvain Community Algorithm):** Analyzes the Accused ↔ Case ↔ Victim graph to uncover organized syndicates.
*   **M6: Case Similarity Engine (TF-IDF):** Surfaces historically identical cases based on modus operandi and FIR BriefFacts.

### 3. Interactive Visualization (Trust Layer)
*   **Crime Heatmaps:** Interactive Leaflet maps featuring marker clusters, temporal sliders, and pulsing CSS animations for high-risk zones.
*   **Network Graphs:** Cytoscape.js rendering up to 5,000+ nodes (Accused/Victim/Case) color-coded by Louvain communities, with clickable profile cards.
*   **Predictive Dashboards:** ECharts rendering trend lines, predictive alerts, and anomaly alert panels wired to real-time **Catalyst Push Notifications**.

### 4. Enterprise Security & Governance
*   **Role-Based Access Control (RBAC):** Granular access for Investigator, Analyst, and Admin roles via Catalyst Authentication.
*   **Audit Logging:** Every query executed is recorded (User ID, Query, Timestamp, IP) in the Catalyst DataStore.
*   **Data Masking:** Sensitive victim PII is masked (`****`) for Analyst roles, accessible only to Admin/Investigators.
*   **API Security:** Catalyst API Gateway enforces rate limiting (100 req/min) and strict JWT Header Validation.

## 🤝 Human-Agent Synergy
Project Falcon represents a cutting-edge division of labor:
*   **AI as Engine Builder:** AI agents handle the rapid generation of Catalyst CLI configurations, 25+ SQL table schemas, Dockerfiles, Catalyst Pipelines (CI/CD), and boilerplate UI.
*   **Humans as Scientific Tuners:** Human leads govern model tuning (ensuring p95 latency <500ms), architectural integrity, manual data ingestion (10,000+ records), and narrative storytelling.

## 🏗️ Architecture & Monorepo Structure

Project Falcon operates on a strict microservice monorepo structure. For detailed architectural flows, please refer to the [Architecture & Metrics Guide](docs/architecture_and_metrics.md).

```text
/Project Falcon
├── /docs       # Comprehensive Implementation Plans, Architecture, & ER Diagrams
├── /frontend   # Catalyst Slate (React 18, Leaflet, Cytoscape.js, ECharts)
├── /backend    # Catalyst AppSail (FastAPI container: geo/graph computing)
├── /ml         # Zia AutoML configurations and Python ETL scripts
├── /circuits   # Catalyst Circuits (YAML workflow definitions)
├── /functions  # Catalyst Serverless Functions (Data Validation triggers)
└── /data       # Relational Schema migrations (28 tables) & Ingestion
```

## 📚 Official Documentation
For team members and evaluators, start here to understand the execution strategy:

1.  **[Master Implementation Plan](docs/master_plan.md):** The definitive 7-day playbook divided across 3 team members (P1, P2, P3).
2.  **[Architecture & Metrics](docs/architecture_and_metrics.md):** High-level component interactions, architectural topology, and p95 latency benchmarks.
3.  **[Database ER Diagram](docs/er_diagram.md):** Extensive map of all 28 relational tables ensuring strict referential integrity.

## ⚙️ Quick Start Setup

### Prerequisites
*   Zoho Catalyst Account (Hackathon specific workspace)
*   Node.js 18+ & Python 3.10+
*   Catalyst CLI: `npm install -g @zohocloud/catalyst-cli`

### Installation Steps

1.  **Initialize Platform**
    *   Login via `catalyst login`
    *   Enable all required Catalyst services (AppSail, QuickML, Zia AutoML, Circuits, Signals, Push, Slate)
    *   Run data migrations from `/data` via the Catalyst DataStore console.

2.  **Spin Up Backend**
    ```bash
    cd backend
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    docker compose up
    ```

3.  **Launch Frontend**
    ```bash
    cd frontend
    npm install
    npm run dev
    ```

---
*Built by Team Project Falcon for KSP Hackathon 2025.*
