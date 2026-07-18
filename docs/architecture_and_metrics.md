# Architecture and Metrics

## System Architecture Diagram

```text
=============================================================================
                          PROJECT FALCON ARCHITECTURE
=============================================================================

 [ FRONTEND LAYER ]
 +---------------------------------------------------------+
 |                 Catalyst Slate (React 18)               |<----+
 |         Maps (Leaflet) | Networks (Cytoscape)           |     |
 +---------------------------------------------------------+     |
           | HTTP Requests                                       | WebSocket
           v                                                     | Push
 [ API & ROUTING LAYER ]                                         |
 +---------------------------------------------------------+     |
 | Catalyst API Gateway (Rate Limits, JWT)                 |     |
 |      |                                                  |     |
 |      v                                                  |     |
 | Catalyst Circuits (Orchestrator)                        |     |
 +---------------------------------------------------------+     |
      |             |                   |                        |
      | Voice IO    | NL-to-SQL / RAG   | Geo/Graph Compute      |
      v             v                   v                        |
 [ INTELLIGENCE ]  [ INTELLIGENCE ]    [ COMPUTE LAYER ]         |
 +--------------+  +----------------+  +--------------------+    |
 | Zia Services |  | Catalyst QuickML| | Catalyst AppSail   |    |
 | (STT, TTS,   |  | (LLM + Vector   | | (FastAPI)          |    |
 | Translation) |  |  Store)         | +--------------------+    |
 +--------------+  +----------------+    |            |          |
                          |              | Validate   | Predict  |
                          | Context      v            v          |
                          |    +--------------+  +------------+  |
                          |    | Functions    |  | Zia AutoML |-.|
                          |    | (Serverless) |  | (Risk/MO)  |  |
                          v    +--------------+  +------------+  |
                    [ STORAGE & DATA LAYER ]              |      |
 +---------------------------------------------------+    |      |
 |  Catalyst DataStore (28 Relational Tables)        |<---+      |
 |  Catalyst NoSQL (Chat Session Memory)             |           |
 |  Catalyst Stratus (GeoJSON/Graph Outputs)         |           |
 |  Segmented Cache (Fast Access for UI Dashboards)  |           |
 +---------------------------------------------------+           |
                                                                 |
 [ ALERTS & NOTIFICATIONS LAYER ]                                |
 +---------------------------------------------------------+     |
 | Catalyst Signals (Event Router)                         |<----+ (Anomaly)
 |      |                                                  |
 |      +--> Catalyst Push Notifications ------------------+
 |      |
 |      +--> Catalyst Mail (Investigator Email Alerts)
 +---------------------------------------------------------+
```

## Complete Catalyst Service Stack
| Category | Catalyst Service | Replaces / Purpose |
|----------|-----------------|-------------------|
| **Compute** | AppSail | FastAPI container: geospatial, graph, SARIMA, TF-IDF |
| **Compute** | Functions (Serverless) | Data validation, ETL triggers, event handlers |
| **Intelligence** | QuickML | LLM serving, NL-to-SQL, RAG vector store |
| **Intelligence** | Zia Services | STT + TTS (English + Kannada), Translation |
| **Intelligence** | **Zia AutoML** | tabular risk + anomaly |
| **Storage** | DataStore | All 28 relational tables |
| **Storage** | NoSQL | Chat session memory (multi-turn context) |
| **Storage** | Stratus | Geospatial outputs, graph index JSON, model artifacts |
| **Storage** | **Cache (Segmented)** | `district_stats.json`, `crime_clusters.geojson` → p95 < 500ms |
| **Experience** | Slate | React 18 SPA hosting |
| **Experience** | Authentication | RBAC (Investigator / Analyst / Admin) |
| **Experience** | API Gateway | Rate limiting 100 req/min, JWT header validation |
| **Automation** | Catalyst Circuits | Workflow orchestration (replaces custom Python script) |
| **Automation** | Catalyst Functions | Serverless event handlers & Data validation |
| **Automation** | Catalyst Signals | Publish-subscribe message router |
| **Automation** | Catalyst Push Notifications | Real-time WebSocket alerts to UI |
| **Automation** | Catalyst Mail | Investigator email alerts |
| **Reports/Forensics** | SmartBrowz | Headless verification (Kapoun criteria) & PDF export |

## 🌍 Global Hybrid Data Governance
*Adapted from a blend of the world's most robust data protection models.*
To mitigate the risk of corporate dependency and regulatory vulnerabilities inherent in third-party APIs (e.g., OpenAI, Anthropic), Project Falcon utilizes a **Global Best Practices Hybrid Model** built **exclusively on Zoho Catalyst**:
- **Israeli Sovereign AI (Autonomy)**: Total administrative oversight. Data never leaves the ecosystem.
- **EU AI Act & GDPR (Explainability & Privacy)**: Catalyst QuickML RAG provides explicit citations. Catalyst DataStore enforces strict data masking for PII.
- **Estonian X-Road (Interoperability)**: Catalyst API Gateway provides a secure, decentralized microservice layer between the ML AppSail container and Slate UI.

## 🔬 Forensic Discovery & PRISMA Verification Layer
Digital intelligence harvested from external sources requires academic-level scrutiny. Project Falcon implements the **PRISMA (Preferred Reporting Items for Systematic Reviews)** workflow for its investigative funnel:
- **Identified**: Raw intelligence and FIRs ingested into DataStore.
- **Screened**: Catalyst Serverless Functions filter out low-signal tips.
- **Excluded**: **Catalyst SmartBrowz** (headless automation) scrapes external intelligence and rejects any that fail the **Kapoun Criteria** (Accuracy, Authority, Objectivity, Currency, Coverage).
- **Included**: The verified suspect graph is generated.
- **Police Evidence Mandate**: Modeled on ROAR/ROARMAP, treating Catalyst DataStore as a centralized registry of all investigative data locations and legal access policies.

## PS2 Requirements Coverage
| # | Requirement | Status | Catalyst Service |
|---|-------------|--------|-----------------|
| 1 | Conversational NL Interface | ✅ Full | QuickML (LLM + RAG) + Zia Services |
| 2 | Criminal Network Analysis | ✅ Full | DataStore + AppSail (NetworkX + Cytoscape.js) |
| 3 | Crime Pattern & Trends | ✅ Full | DataStore + AppSail (DBSCAN + K-Means) |
| 4 | Sociological Crime Insights | ⚠️ Partial | DataStore + public census overlay |
| 5 | Offender Profiling (Risk Score) | ✅ Full | **Zia AutoML** tabular classification |
| 6 | Investigator Decision Support | ✅ Full | **Catalyst Circuits** orchestration |
| 7 | Financial Crime Analysis | 🔬 Simulated | DataStore (synthetic labelled schema) |
| 8 | Crime Forecasting & Alerts | ✅ Full | AppSail (SARIMA) + **Catalyst Push** |
| 9 | Explainable AI (Evidence Trail) | ✅ Full | QuickML RAG + FIR citation in every Circuits output |
| 10 | Secure RBAC & Audit Logs | ✅ Full | Authentication + API Gateway + DataStore |

## Performance Benchmarks (Non-Negotiable)
| Metric | Target | Service |
|--------|--------|---------|
| ML inference p95 latency | < 500ms | Zia AutoML + Catalyst Cache |
| Map render (10K GPS points) | < 2 seconds | Leaflet + AppSail |
| Network graph (5K nodes) | No browser freeze | Cytoscape.js |
| Concurrent LLM queries | 50 without crash | AppSail + Circuits |
| Repeat offender risk AUC-ROC | > 0.75 | Zia AutoML |
| Evidence trail | FIR number in every AI answer | QuickML RAG |
