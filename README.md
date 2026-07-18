# CrimeGPT: Catalyst-Native Intelligence Platform
**Project Falcon** - KSP Hackathon 2025 | Problem Statement 2

## Overview
CrimeGPT is a 100% Zoho Catalyst-native platform designed for the Karnataka State Police. It provides a conversational interface, criminal network analysis, spatial crime forecasting, and predictive offender profiling. The entire intelligence and orchestration stack runs on Zoho Catalyst without reliance on external third-party AI APIs.

## Key Features
- **Conversational Intelligence:** Natural language interaction using Catalyst QuickML (LLM + RAG) and Zia Services (STT/TTS in Kannada & English).
- **Network Analysis:** Graph-based identification of criminal syndicates.
- **Crime Forecasting:** Geospatial anomaly detection and temporal hotspot prediction.
- **Offender Risk Profiling:** Automated risk assessment using Zia AutoML tabular classification.
- **Real-Time Orchestration:** Catalyst Circuits for intelligent workflow routing.

## Architecture Highlights
- **Frontend:** Catalyst Slate hosting a React 18 SPA (Vite) with Leaflet and Cytoscape.js.
- **Backend:** Catalyst AppSail hosting FastAPI for computationally heavy geospatial and graph algorithms.
- **ML Layer:** Zia AutoML integrated for direct anomaly and risk detection.
- **Data Layer:** Catalyst DataStore (relational), NoSQL (session context), and Stratus (graph/geo storage).
- **Automation:** Catalyst Functions, Circuits, Signals, and Push Notifications.

## Repository Structure
This is a monorepo organizing all aspects of the architecture:

- `/docs`: Complete implementation plans, ER diagrams, architecture details, and division of labor.
- `/frontend`: The Catalyst Slate React 18 application.
- `/backend`: The Catalyst AppSail FastAPI backend.
- `/ml`: Zia AutoML configurations and initial data preparation scripts.
- `/circuits`: Catalyst Circuits workflow YAML definitions.
- `/functions`: Catalyst Serverless Functions for data validation and triggers.
- `/data`: Schema migrations for all 28 relational tables and dataset ingestion scripts.

## Getting Started
Please refer to the detailed implementation guide in the `/docs` folder:
- **[Master Implementation Plan](docs/master_plan.md)**: Step-by-step phases, division of labor (P1/P2/P3), goals, and metrics.
- **[Architecture & Metrics](docs/architecture_and_metrics.md)**: Performance benchmarks and service mapping.
- **[Database ER Diagram](docs/er_diagram.md)**: The schema mapping for the KSP FIR dataset.

## Setup Requirements
1. Zoho Catalyst Account (Hackathon specific).
2. Node.js 18+ and `npm`.
3. Python 3.10+.
4. Catalyst CLI installed globally (`npm install -g @zohocloud/catalyst-cli`).
