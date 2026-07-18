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
In the modern threat landscape, relying on generic third-party AI providers poses significant regulatory and security risks. Project Falcon adapts a **Global Best Practices Hybrid Model**, ensuring world-class security while remaining completely within Zoho Catalyst's native ecosystem:

1.  **Israeli Sovereign AI Model (Data Autonomy):** By keeping 100% of the architecture within the Zoho Catalyst ecosystem, we eliminate corporate dependency on foreign AI vendors (e.g., OpenAI, Anthropic). The state maintains absolute administrative control.
2.  **EU AI Act (Explainable AI & Privacy):** Every AI decision must be traceable. Catalyst QuickML RAG provides explicit citations to FIRs. Furthermore, Catalyst DataStore enforces strict data masking for PII, satisfying GDPR-level privacy requirements for Analyst roles.
3.  **Estonian X-Road (Secure Interoperability):** Adapted for our microservice architecture, Catalyst API Gateway and AppSail create a decentralized, highly secure data exchange layer between the machine learning backend and the React frontend.
4.  **2026 Academic Discovery Standards:** We treat digital police evidence with the rigorous scientific precision outlined in the 2026 Professional Standard for Scholarly Discovery.

## 🔬 Scientific Data Engineering: Information Architecture (IA)
The literature search is no longer a preliminary task; it is the data engineering phase of the investigation. Without a disciplined database mix, AI synthesis risks "ranking the wrong corpus," leading to high-confidence hallucinations. Project Falcon implements the **PRISMA (Preferred Reporting Items for Systematic Reviews)** workflow for its investigative funnel:

*   **Identified**: Raw FIRs and intelligence are ingested into DataStore, mimicking the broad discovery engines like Semantic Scholar and OpenAlex.
*   **Screened**: **Catalyst Serverless Functions** handle automated deduplication and initial abstract screening.
*   **Excluded**: Studies removed based on strict inclusion/exclusion criteria. We utilize **Catalyst SmartBrowz** (headless automation) as a forensic gatekeeper, rejecting open-source intelligence that fails the **Kapoun Criteria** (Accuracy, Authority, Objectivity, Currency, Coverage) without external API costs.
*   **Included**: The finalized verified corpus for synthesis (Achieving "Theoretical Saturation"). Tools like QuickML/RAG are restricted *only* to this Included corpus to mitigate hallucinations.

## 🚀 Core Features & Capabilities

### 1. The Intelligence Orchestrator (PICO-Driven Conversational UI)
Moving beyond "keyword guessing," Project Falcon transforms research questions into a machine-readable conceptual hierarchy.
*   **NL-to-SQL Pipeline**: Schema-aware Catalyst QuickML dynamically translates plain English (and Kannada) into complex SQL joins. Queries are structured using the **PICO Framework** (Population, Intervention, Comparison, Outcome) for quantitative data and **SPIDER** for qualitative phenomena to map criminal patterns accurately.
*   **Explainable RAG**: Retrieves BriefFacts using QuickML vector store.
*   **Multi-Language Voice IO**: Kannada and English speech-to-text, translation, and text-to-speech handled entirely by **Zia Services**.

### 2. Six-Pillar ML Analytics Engine
*   **M1: Geospatial Detection (DBSCAN & K-Means)**: Identifies geographical crime hotspots.
*   **M2: Repeat Offender Risk (Zia AutoML)**: Tabular classification grading offenders with a 0-100 risk score.
*   **M3: Crime Forecasting (SARIMA)**: Time-series forecasting for 7-day and 30-day predictions.
*   **M4: Anomaly Detection (Isolation Forest)**: Flags irregular FIRs and investigative outliers.
*   **M5: Criminal Network Discovery (Louvain Algorithm)**: Uncovers organized syndicates via graph analysis.
*   **M6: Case Similarity Engine (TF-IDF)**: Surfaces historically identical cases, functioning similarly to paper embeddings in Semantic Scholar.

### 3. Open-Access Registries and Metadata Graphs
The mechanics of scholarly metadata (e.g., OAI-PMH) allow for transparency and interoperability.
*   **Police Evidence Mandate**: Modeled after ROAR (Registry of Open Access Repositories) and ROARMAP. Catalyst DataStore acts as a centralized registry tracking the location and access mandates for all investigative data, providing a unified map of where case data exists and its legal protocols.

### 4. Interactive Visualization (Trust Layer)
*   **Crime Heatmaps**: Interactive Leaflet maps featuring marker clusters and temporal sliders.
*   **Network Graphs**: Cytoscape.js rendering up to 5,000+ nodes color-coded by Louvain communities.
*   **Predictive Dashboards**: ECharts rendering trend lines wired to **Catalyst Push Notifications**.

### 5. Enterprise Security & Governance
*   **Role-Based Access Control (RBAC)**: Granular access for Investigator, Analyst, and Admin roles.
*   **Audit Logging**: Every query executed is recorded (User ID, Query, Timestamp, IP).
*   **API Security**: Catalyst API Gateway enforces rate limiting (100 req/min) and strict JWT Validation.

## 🤝 Human-Agent Synergy
*   **AI as Engine Builder**: AI handles rapid generation of CLI configurations, schemas, Dockerfiles, Catalyst Pipelines (CI/CD), and UI boilerplate.
*   **Humans as Scientific Tuners**: Human leads govern model tuning (p95 latency <500ms), architectural integrity, manual data ingestion (10,000+ records), and qualitative forensic validation (verifying p-values, sample sizes, and limitations).

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
1.  **[Master Implementation Plan](docs/master_plan.md)**: The definitive playbook divided across 3 team members.
2.  **[Architecture & Metrics](docs/architecture_and_metrics.md)**: High-level component interactions and benchmarks.
3.  **[Database ER Diagram](docs/er_diagram.md)**: Map of all 28 relational tables ensuring strict referential integrity.

## ⚙️ Quick Start Setup
### Prerequisites
*   Zoho Catalyst Account
*   Node.js 18+ & Python 3.10+
*   Catalyst CLI: `npm install -g @zohocloud/catalyst-cli`

### Installation Steps
1.  **Initialize Platform**
    *   Login via `catalyst login`
    *   Enable all required Catalyst services
    *   Run data migrations from `/data`

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
