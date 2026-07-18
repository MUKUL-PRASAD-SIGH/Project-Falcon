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

## 🌍 Strategic Foundation: The Global Hybrid Framework
In the modern threat landscape, relying on generic third-party AI providers poses significant regulatory and security risks. Project Falcon adapts a **Global Best Practices Hybrid Model**, ensuring world-class security while remaining completely within Zoho Catalyst's native free-tier ecosystem:

1.  **Israeli Sovereign AI Model (Data Autonomy):** By keeping 100% of the architecture within the Zoho Catalyst ecosystem, we eliminate corporate dependency on foreign AI vendors (e.g., OpenAI, Anthropic). The state maintains absolute administrative control.
2.  **EU AI Act (Explainable AI & Privacy):** Every AI decision must be traceable. Catalyst QuickML RAG provides explicit citations to FIRs. Furthermore, Catalyst DataStore enforces strict data masking for PII, satisfying GDPR-level privacy requirements for Analyst roles.
3.  **Estonian X-Road (Secure Interoperability):** Adapted for our microservice architecture, Catalyst API Gateway and AppSail create a decentralized, highly secure data exchange layer between the machine learning backend and the React frontend.
4.  **2026 Academic Discovery Standards:** Treating digital evidence with rigorous scientific precision.

## 🚀 Core Features & Capabilities

### 1. The Intelligence Orchestrator (PICO-Driven Conversational UI)
Not just a chatbot, but a semantic routing engine utilizing professional scholarly discovery standards.
*   **NL-to-SQL Pipeline**: Schema-aware Catalyst QuickML dynamically translates plain English (and Kannada) into complex SQL joins across 28 relational tables. Queries are structured using the **PICO Framework** (Population, Intervention, Comparison, Outcome) to map criminal patterns accurately.
*   **Evidence-Based RAG Knowledge Base**: Retrieves BriefFacts using QuickML vector store.
*   **Explainable AI**: Every AI response cites explicit FIR numbers (satisfying Requirement #9).
*   **Multi-Language Voice IO**: Kannada and English speech-to-text, translation, and text-to-speech handled entirely by **Zia Services**.

### 2. Six-Pillar ML Analytics Engine
*   **M1: Geospatial Detection (DBSCAN & K-Means)**: Identifies geographical crime hotspots overlaid with district boundaries.
*   **M2: Repeat Offender Risk (Zia AutoML)**: Tabular classification grading offenders with a 0-100 risk score (AUC-ROC >0.75).
*   **M3: Crime Forecasting (SARIMA)**: Time-series forecasting for 7-day and 30-day predictions.
*   **M4: Anomaly Detection (Isolation Forest)**: Flags irregular FIRs and investigative outliers.
*   **M5: Criminal Network Discovery (Louvain Algorithm)**: Analyzes the Accused ↔ Case ↔ Victim graph to uncover organized syndicates.
*   **M6: Case Similarity Engine (TF-IDF)**: Surfaces historically identical cases based on modus operandi.

### 3. Forensic Discovery & The PRISMA Funnel
Project Falcon treats digital evidence with rigorous academic standards, replacing manual keyword guessing with the **PRISMA (Preferred Reporting Items for Systematic Reviews)** workflow for investigations:
*   **Identified**: Raw FIRs and tips ingested into DataStore.
*   **Screened**: Catalyst Serverless Functions apply anomaly detection filtering.
*   **Excluded**: **Catalyst SmartBrowz** (headless automation) acts as a forensic gatekeeper, rejecting open-source intelligence that fails the **Kapoun Criteria** (Accuracy, Authority, Objectivity, Currency, Coverage) without external API costs.
*   **Included**: The final verified suspect graph sent to the UI.
*   **Police Evidence Mandate**: Modeled after ROAR (Registry of Open Access Repositories). DataStore acts as a centralized registry tracking the location and access mandates for all investigative data.

### 4. Interactive Visualization (Trust Layer)
*   **Crime Heatmaps**: Interactive Leaflet maps featuring marker clusters and temporal sliders.
*   **Network Graphs**: Cytoscape.js rendering up to 5,000+ nodes color-coded by Louvain communities.
*   **Predictive Dashboards**: ECharts rendering trend lines and anomaly alert panels wired to **Catalyst Push Notifications**.

### 5. Enterprise Security & Governance
*   **Role-Based Access Control (RBAC)**: Granular access for Investigator, Analyst, and Admin roles via Catalyst Authentication.
*   **Audit Logging**: Every query executed is recorded (User ID, Query, Timestamp, IP) in the Catalyst DataStore.
*   **API Security**: Catalyst API Gateway enforces rate limiting (100 req/min) and strict JWT Header Validation.

## 🤝 Human-Agent Synergy
*   **AI as Engine Builder**: AI handles rapid generation of CLI configurations, schemas, Dockerfiles, Catalyst Pipelines (CI/CD), and UI boilerplate.
*   **Humans as Scientific Tuners**: Human leads govern model tuning (p95 latency <500ms), architectural integrity, manual data ingestion (10,000+ records), and qualitative forensic validation.

## 🏗️ Architecture & Monorepo Structure

For detailed architectural flows, please refer to the [Architecture & Metrics Guide](docs/architecture_and_metrics.md).

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
For team members and evaluators:
1.  **[Master Implementation Plan](docs/master_plan.md)**: The definitive 7-day playbook divided across 3 team members.
2.  **[Architecture & Metrics](docs/architecture_and_metrics.md)**: High-level component interactions, architectural topology, and p95 latency benchmarks.
3.  **[Database ER Diagram](docs/er_diagram.md)**: Extensive map of all 28 relational tables ensuring strict referential integrity.

## ⚙️ Quick Start Setup
### Prerequisites
*   Zoho Catalyst Account
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
