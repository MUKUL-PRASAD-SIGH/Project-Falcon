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

## 🚀 Key Features

*   **Conversational Intelligence:** Query case files naturally using **Catalyst QuickML** (LLM + RAG). Voice input is handled directly via **Zia Services** for Speech-to-Text and Translation (Kannada ↔ English).
*   **Predictive Hotspot Forecasting:** Utilizing SARIMA models hosted on **Catalyst AppSail** to predict future crime spikes, combined with real-time **Catalyst Push Notifications** for live dashboard alerts.
*   **Automated Offender Profiling:** A 0-100 risk scoring engine trained entirely via **Zia AutoML**, continuously classifying repeat offenders based on demographic and operational data.
*   **Criminal Network Discovery:** Interactive node graphs (Cytoscape.js) resolving Accused ↔ FIR ↔ Victim links through Louvain community detection.
*   **Explainable AI (Evidence Trail):** Every generative response is grounded in the database; **Catalyst Circuits** enforces strict RAG pipelines ensuring all AI claims cite the specific FIR number.

## 🏗️ Architecture & Monorepo Structure

Project Falcon operates on a strict microservice monorepo structure. For detailed architectural flows, please refer to the [Architecture & Metrics Guide](docs/architecture_and_metrics.md).

```text
/Project Falcon-KSP
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
4.  **[Division of Labor](docs/division_of_labor.md):** Human-Agent collaboration framework.

## ⚙️ Quick Start Setup

### Prerequisites
*   Zoho Catalyst Account (Hackathon specific workspace)
*   Node.js 18+ & Python 3.10+
*   Catalyst CLI: `npm install -g @zohocloud/catalyst-cli`

### Installation Steps

1.  **Initialize Platform (P1)**
    *   Login via `catalyst login`
    *   Enable all required Catalyst services (AppSail, QuickML, Zia AutoML, Circuits, Signals, Push, Slate)
    *   Run data migrations from `/data` via the Catalyst DataStore console.

2.  **Spin Up Backend (P1/P2)**
    ```bash
    cd backend
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    docker compose up
    ```

3.  **Launch Frontend (P3)**
    ```bash
    cd frontend
    npm install
    npm run dev
    ```

## 🔐 Security & Governance
Project Falcon adheres to strict governance models suitable for law enforcement:
*   **Catalyst API Gateway:** Rate limiting enforced at 100 requests/minute.
*   **Audit Logging:** Every query executed is logged with the user's ID, timestamp, and IP address.
*   **RBAC & Data Masking:** Role-based access via Catalyst Auth restricts sensitive victim data from Analyst roles, ensuring only high-clearance Investigators access unmasked PII.

---
*Built by Team Project Falcon for KSP Hackathon 2025.*
