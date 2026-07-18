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

## Sovereign AI & Data Governance
*Adapted from the Israeli National Security Model for Sovereign AI.*
To mitigate the risk of corporate dependency and regulatory vulnerabilities inherent in third-party APIs (e.g., OpenAI, Anthropic), Project Falcon is built **exclusively on Zoho Catalyst**. 
- **Absolute Local Oversight**: Data never leaves the ecosystem.
- **Auditable Logic**: Algorithms and RAG infrastructure are entirely contained within the state's administrative control.
- **Cost-Efficiency**: Avoids the pay-per-token model of third-party platforms.

## Forensic Discovery & Verification Layer
Digital intelligence harvested from external sources requires academic-level scrutiny. Project Falcon implements:
- **Police Evidence Mandate**: Modeled on ROAR/ROARMAP, treating Catalyst DataStore as a centralized registry of all investigative data locations and legal access policies.
- **Kapoun Criteria Validation**: Using **Catalyst SmartBrowz** (headless automation), the platform scrapes and validates external open-source intelligence based on:
  1. **Accuracy**: Cross-referencing author credentials.
  2. **Authority**: Verifying `.gov`/`.edu` domains.
  3. **Objectivity**: Running quick sentiment sweeps via Zia Services.
  4. **Currency**: Validating update timestamps.
  5. **Coverage**: Ensuring full headless visibility without proprietary paywalls.

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
