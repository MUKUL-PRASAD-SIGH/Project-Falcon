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
 |      +--> Auth (RBAC: Investigator, Analyst, Admin)     |     |
 +---------------------------------------------------------+     |
           | Secure Context                                      |
           v                                                     |
 [ BACKEND COMPUTE LAYER ]                                       |
 +---------------------------------------------------------+     |
 |   Catalyst AppSail (FastAPI Docker Container)           |     |
 |    - Geo Clustering (DBSCAN, K-Means)                   |     |
 |    - Graph Analytics (NetworkX, Louvain)                |     |
 |    - Time-Series Forecasting (SARIMA)                   |     |
 |    - Case Similarity (TF-IDF)                           |     |
 |    - Forensic Verification (SmartBrowz Kapoun Checks)   |     |
 +---------------------------------------------------------+     |
           |                                                     |
           v                                                     |
 [ MACHINE LEARNING & INTELLIGENCE LAYER ]                       |
 +---------------------------------------------------------+     |
 | Catalyst Zia AutoML | QuickML (NL-to-SQL + PICO RAG)    |     |
 | Zia Services (Voice STT/TTS & Translation)              |     |
 +---------------------------------------------------------+     |
           |                                                     |
           v                                                     |
 [ DATA & STORAGE LAYER ]                                        |
 +---------------------------------------------------------+     |
 | Catalyst DataStore (28 Relational Tables)               |     |
 |  - Includes: Police Evidence Mandate Registry (ROARMAP) |     |
 | Catalyst NoSQL (Conversational Memory)                  |     |
 | Catalyst Cache (Pre-computed hot zones)                 |     |
 +---------------------------------------------------------+     |
           |                                                     |
           v                                                     |
 [ ORCHESTRATION & NOTIFICATION LAYER ]                          |
 +---------------------------------------------------------+     |
 | Catalyst Circuits (Workflow Automation & PRISMA logic)  |     |
 | Catalyst Signals & Push Notifications ------------------------+
 | Catalyst Mail (Investigator Alerts)                     |
 +---------------------------------------------------------+
```

## Component Breakdown

| Category | Catalyst Component | Implementation Purpose |
| :--- | :--- | :--- |
| **Intelligence** | Zia AutoML | Tabular risk classification (M2) & Anomaly detection (M4) |
| **Intelligence** | QuickML | RAG for BriefFacts & NL-to-SQL Pipeline (PICO/SPIDER mapped) |
| **Intelligence** | Zia Services | Kannada/English Voice IO + Sentiment Analysis |
| **Compute** | AppSail | FastAPI container: geospatial, graph, SARIMA, TF-IDF |
| **Storage** | DataStore | 28 tables, PRISMA Tracking, Police Evidence Mandate |
| **Storage** | NoSQL | Chat history & state persistence |
| **Storage** | Cache | Redis-backed caching for heatmap initial loads |
| **Experience** | Slate | React 18 SPA hosting |
| **Experience** | Authentication | RBAC (Investigator / Analyst / Admin) |
| **Experience** | API Gateway | Rate limiting 100 req/min, JWT header validation |
| **Automation** | Catalyst Circuits | Workflow orchestration (replaces custom Python script) |
| **Automation** | Catalyst Functions | Serverless event handlers & Data validation (PRISMA Funnel) |
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
Digital intelligence harvested from external sources requires academic-level scrutiny (The 2026 Professional Standard for Scholarly Discovery). Project Falcon implements the **PRISMA (Preferred Reporting Items for Systematic Reviews)** workflow for its investigative funnel:
- **Identified**: Raw intelligence and FIRs ingested into DataStore (similar to broad discovery passes on Semantic Scholar or OpenAlex).
- **Screened**: **Catalyst Serverless Functions** filter out low-signal tips and handle automated deduplication.
- **Excluded**: **Catalyst SmartBrowz** (headless automation) acts as the final gatekeeper, scraping external intelligence and rejecting any that fail the **Kapoun Criteria** (Accuracy, Authority, Objectivity, Currency, Coverage).
- **Included**: The verified suspect graph is generated. Theoretical saturation is reached when backward/forward searching yields zero new evidence.
- **Police Evidence Mandate**: Modeled on ROAR/ROARMAP and OAI-PMH interoperability, treating Catalyst DataStore as a centralized registry of all investigative data locations and legal access policies.

## PS2 Requirements Coverage
| # | Requirement | Status | Catalyst Service |
|---|-------------|--------|------------------|
| 1 | Centralized Dashboard | âœ… Complete | Slate (React UI) |
| 2 | Crime Mapping | âœ… Complete | Slate (Leaflet) + AppSail (DBSCAN) |
| 3 | Trend Analysis | âœ… Complete | AppSail (SARIMA) + QuickML |
| 4 | Predictive Models | âœ… Complete | Zia AutoML |
| 5 | Network Graphing | âœ… Complete | Cytoscape.js + AppSail (Louvain) |
| 6 | Integration | âœ… Complete | AppSail REST API |
| 7 | Scalability | âœ… Complete | Serverless architecture |
| 8 | Multi-language (Kannada) | âœ… Complete | Zia Services (Voice/Translate) |
| 9 | Explanability | âœ… Complete | QuickML (RAG Traceability) |

## Performance SLA (Service Level Agreements)
*   **API P95 Latency:** < 500ms (via Catalyst Cache)
*   **Geospatial Query (100k points):** < 1.2s (PostgreSQL indexing on DataStore)
*   **NL-to-SQL Translation:** < 2.5s (QuickML response time)
*   **RAG Document Retrieval:** < 1.5s
*   **Uptime Target:** 99.9% (Native Catalyst SLAs)
