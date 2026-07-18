### CrimeGPT: The Definitive Catalyst-Native Master Implementation Plan (Revised)

#### 1\. Executive Strategic Alignment and Platform Vision

This revised implementation plan marks a definitive shift from a "Catalyst-assisted" architecture to a 100% **Catalyst-native** ecosystem. By migrating all logic, intelligence, and storage into the Zoho Catalyst stack, we ensure total compliance with the KSP Hackathon 2025 mandates while maximizing system scalability. This architecture eliminates the friction of third-party dependencies, providing an idempotent foundation where serverless logic and unified data governance enable real-time criminal intelligence at a state-wide scale.The following table maps the 10 core requirements of Problem Statement 2 (PS2) to the expanded Catalyst service stack, reflecting honest scoping based on the provided ER schema:| PS2 Core Requirement | Status | Catalyst Service Stack Mapping || ------ | ------ | ------ || 1. Conversational NL Interface | **Full** | Catalyst QuickML (LLM Serving) + Zia Services || 2. Criminal Network Analysis | **Full** | Catalyst Data Store + AppSail (NetworkX/Cytoscape.js) || 3. Crime Pattern & Trends | **Full** | Catalyst Data Store + AppSail (DBSCAN/K-Means) || 4. Sociological Crime Insights | **Partial** | Catalyst Data Store + Public Census Overlay || 5. Offender Profiling (Risk Score) | **Full** | **Catalyst Zia AutoML** (Tabular Classification) || 6. Investigator Decision Support | **Full** | **Catalyst Circuits** (Orchestration Workflow) || 7. Financial Crime Analysis | **Simulated** | Catalyst Data Store (Synthetic/Labelled Schema) || 8. Crime Forecasting & Alerts | **Full** | Catalyst AppSail (SARIMA) + **Catalyst Push Notifications** || 9. Explainable AI | **Full** | Catalyst QuickML (RAG + Citation Engine) || 10. Secure RBAC & Audit Logs | **Full** | Catalyst Authentication + API Gateway + Data Store |

**Winning Differentiators:** This plan mandates the immediate removal of all third-party dependencies, specifically the "Google Translate" fallback mentioned in previous versions. We will utilize **Catalyst Zia Services** exclusively for Translation, STT, and TTS. Furthermore, we are abandoning manual Python-based ML training scripts in favor of **Catalyst Zia AutoML** for tabular data. This platform-first approach ensures that our intelligence layer is robust, automated, and fully integrated into the Catalyst lifecycle. This architectural rigor begins with the idempotent foundation setup in Phase 0.

#### 2\. Phase 0: Unified Foundation and Environment Orchestration

Phase 0 establishes the "shared-truth" environment necessary for a high-velocity three-person team (P1, P2, P3). By synchronizing local dev environments with the Catalyst cloud environment, we eliminate deployment friction and ensure consistent execution of serverless logic.

##### Step 0.1: Catalyst Platform Setup (Command: P1)

**P1: Enable and initialize the following services immediately in the Catalyst Console:**

- **Compute:** AppSail (Backend), Functions (Serverless logic).
- **Intelligence:** QuickML (LLM Serving/RAG), Zia Services (Voice/Translation), **Zia AutoML** (Risk Scoring).
- **Storage:** Data Store (Relational), NoSQL (Sessions), Stratus (Model Files), **Catalyst Cache** (Performance).
- **Experience:** Slate (Frontend Hosting), Authentication, API Gateway.
- **Automation:** **Catalyst Circuits** (Workflows), **Catalyst Signals** (Event Routing), Cron, **Catalyst Mail** , **Catalyst Push** .
- **Reports:** SmartBrowz (PDF Generation).

##### Monorepo Structure and CI/CD

**P1: Initialize the project with the following monorepo structure and configure Catalyst Pipelines for automated CI/CD on every push to** **main** **.**

/CrimeGPT-KSP

├── /frontend # Catalyst Slate (React 18 + Apache ECharts)

├── /backend # Catalyst AppSail (FastAPI)

├── /ml # Zia AutoML Configs & Cleansing Functions

├── /circuits # Catalyst Circuits (Orchestration Workflows)

├── /data # Schema Migrations & Data Ingestion

└── catalyst.json # Unified Project Config

##### Team Environment Synchronization (Human Must Do)

- **P1 (Backend Lead):** Authenticate Catalyst CLI (catalyst login). Initialize project, enable all services, and share project access with P2/P3 via team settings.
- **P2 (ML Lead):** Authenticate Catalyst CLI. Set up Python venv and verify environment via: python3 -c 'import geopandas, networkx; print("OK")'. Ensure catalyst-cli access to Zia AutoML and QuickML consoles.
- **P3 (Frontend Lead):** Authenticate Catalyst CLI. Verify Node 18+ environment. Initialize the React project in /frontend and verify the catalyst hosting configuration for Slate.

#### 3\. Phase 1 & 2: Data Engineering and Automated Machine Learning

The data layer is the intelligence bedrock of CrimeGPT. We are moving away from manual script-based model management to a **Zia AutoML** approach to ensure high-fidelity predictions on tabular police data.

##### Step 1.1: Schema Migration (Command: P1)

**P1: Generate and execute SQL for the 25+ relational tables in Catalyst Data Store.**

- **Priority Focus:** Immediately migrate CaseMaster, FIRs, Accused, PreviousCriminal, and Victim.
- **Performance Requirement:** Apply indexes to all Foreign Key (FK) columns, GPS (latitude/longitude), and timestamps to ensure sub-second query performance.

##### Step 2.2: Intelligence Engine - Zia AutoML (Command: P2)

**P2: Delete all manual training scripts (** **train_repeat_offender.py** **). Implement Catalyst Zia AutoML for the following models:**

- **Repeat Offender Risk Scoring:** Upload historical accused data to Zia AutoML to generate a classification model (0-100 score).
- **Anomaly Detection:** Configure Zia AutoML to identify outlier FIRs based on Modus Operandi (MO) and incident frequency.
- **Performance Layer:** Implement **Catalyst Cache (Segmented)** to store district_stats.json and crime_clusters.geojson. Target a p95 latency of **<500ms** for high-traffic dashboard endpoints.

##### Data Validation and Cleansing Workflow

**P2: Implement the following workflow using Catalyst Serverless Functions for real-time data integrity.**| Step | Action | Catalyst Component || ------ | ------ | ------ || Ingestion | Load raw CSV/JSON (KSP Dataset) | AppSail (FastAPI) || Validation | Bounding Box check (11.5°N-18.5°N, 74°E-78.5°E) | Serverless Functions || Cleansing | UTF-8 enforcement for Kannada text | Serverless Functions || Storage | Relational persistence with FK integrity | Catalyst Data Store |

#### 4\. Phase 3: LLM Intelligence and Native Zia Voice Integration

Phase 3 establishes "Explainable AI" in the KSP context. All Generative AI responses must be grounded in the Data Store to prevent hallucination.

##### Intelligence and RAG Strategy (Command: P2)

- **NL-to-SQL:** Configure **Catalyst QuickML** with a schema-aware system prompt to translate natural language into validated SQL.
- **RAG Knowledge Base:** Implement chunking for BriefFacts from FIRs.
- **Strategy:** Use 200-token chunks with a **20-token overlap** for retrieval context.
- **Vector Store:** Index chunks into the QuickML vector store to ground all AI answers in specific case records.

##### Native Zia Voice Integration (Command: P1)

**P1: Explicitly delete all Google Translate fallback code. Maintain 100% Catalyst-native compliance.**

- **Voice Processing:** Use **Catalyst Zia Services** for STT (Kannada/English) and TTS.
- **Translation:** Use Zia Services to translate Kannada queries to English for the LLM and back to Kannada for the investigator.

##### Orchestration via Catalyst Circuits (Command: P1/P2)

**P1/P2: Replace custom Python orchestrators with Catalyst Circuits.**

- **Trigger:** Configure a POST request trigger from the API Gateway.
- **Transition Logic:** Design a workflow that classifies intent. If "Map" or "Cluster" is detected, branch to the Geospatial engine; if "Network" or "Gang" is detected, branch to the Graph Engine.
- **Evidence Trail:** Every circuit completion **must** return an "Evidence Trail" citing specific FIR numbers from the RAG retrieval.

#### 5\. Phase 4: Frontend Visualization and Real-Time Alerting

Visual Intelligence transforms raw data into actionable insights via heatmaps and network graphs.

##### Visual Intelligence Stack (Command: P3)

- **Platform:** Deploy the **React SPA** on **Catalyst Slate** .
- **Maps & Graphs:** Integrate Leaflet.js for crime heatmaps and Cytoscape.js for gang network visualization.
- **Forecasting:** Integrate **Apache ECharts** to render 7-day and 30-day crime trend lines and forecasting dashboards.

##### Real-Time Alerts and Signals (Command: P3)

**P3: Build a custom React Hook that listens for Catalyst Signals.**

- **Workflow:** When Zia AutoML or the Anomaly Engine detects a high-risk "spike zone," a **Catalyst Signal** must trigger a real-time update to the "Anomaly Alert" panel in the UI without requiring a page refresh.

##### Professional Reporting (Command: P1/P3)

**P1/P3: Implement "Export to PDF" using Catalyst SmartBrowz.**

- **Command:** Map the "Evidence Trail" variables (FIR citations and AI explanations) into the SmartBrowz PDF template to ensure investigators can submit AI-generated insights as judicial evidence.

#### 6\. Phase 5 & 6: Security, Deployment, and Demo Excellence

Sensitive police data requires the highest level of governance and security.

##### Security and Governance (Command: P1)

- **API Gateway:** Configure the **Catalyst API Gateway** with a rate limit of 100 req/min.
- **CORS Policy:** Explicitly configure CORS policies to allow requests only from the **Catalyst Slate** production domain to prevent deployment failures.
- **Audit Logging:** Implement a dedicated AuditLog table in the **Catalyst Data Store** . **P1: Must log the following fields for every query:** **user_id** **,** **query_string** **,** **timestamp** **,** **result_count** **, and** **request_IP** **.**

##### Production Push (Command: Team)

- **Deployment:** Push the backend to **Catalyst AppSail** and the frontend to **Catalyst Slate** via **Catalyst Pipelines** .
- **QA:** Verify that all environment secrets are synchronized and that the system achieves <500ms p95 latency on prediction endpoints.

##### Demo Script Strategy: Winning Differentiators

**Command the team to rehearse three high-impact scenarios for the judges:**

- **The Voice Lead:** A live Kannada voice-led hotspot query: _"Show me robbery hotspots in Electronic City,"_ rendering a pulsing heatmap.
- **The Gang Deep-Dive:** Query an accused to instantly reveal their Cytoscape network graph and Louvain-detected gang community.
- **Live Role-Switch:** Demonstrate the **Investigator vs. Admin** roles. Show the Admin dashboard's live **Audit Trail** and the data masking of sensitive victim info for non-admin roles.**Conclusion:** By adhering to this 100% Catalyst-native architecture, CrimeGPT provides the Karnataka State Police with a secure, explainable, and high-performance intelligence platform that exceeds all hackathon benchmarks.