# KSP Data Quality & Validation Report

This report documents the state of the data flowing into our Catalyst DataStore, tracking quality metrics from the Serverless PRISMA validation funnel and outlining simulated vs real data gaps.

## PRISMA Funnel Validation Results (Simulated Run)

Our Catalyst Serverless Functions (`validate_gps`, `validate_fk`, `clean_text`) run continuously to validate incoming data. Below is a snapshot of the current state based on synthetic data generation:

| Metric | Result | Notes |
|--------|--------|-------|
| **Total Records Generated** | 1,000 FIRs, 1,500 Accused | Synthetic baseline |
| **GPS Outliers Blocked** | 0% | All synthetic records generated inside Karnataka bounding box (11.5°N-18.5°N, 74°E-78.5°E) |
| **FK Integrity Violations** | 0% | All `CaseMasterID` and `CrimeHeadID` constraints pass |
| **Null BriefFacts** | 0% | Text cleaned via `clean_text` function enforcing UTF-8 |

## Data Gaps (Available vs Simulated vs Missing)

Because we are working without the official production dataset in this initial sprint, we have mocked the critical tables using Faker.

| Feature Area | Current Status | Mitigation / Strategy |
|--------------|----------------|------------------------|
| **Core FIR Data** | 🟡 Simulated | Using Parquet feature store containing mocked 1000 FIRs and 1500 Accused. |
| **Lookup Entities** | ✅ Available | 16 Lookup tables (CrimeHead, State, District, etc.) are fully seeded with actual standard codes. |
| **Financial Crime Data** | ❌ Missing | Wait for official KSP dataset release. |
| **CDR (Call Data Records)** | ❌ Out of Scope | Not attempting due to lack of standard mock formats and scope limits. |
| **Caste / Religion / Occ.** | 🟡 Simulated/Missing | Omitted from current synthetic `seed_datastore.py` script. Will be loaded once real data arrives. |

## UI / Frontend Safelist

For the Frontend Lead (P3), the following fields are confirmed **safe to display** without masking:
- `AccusedName`
- `CrimeGroupName`
- `DistrictName`
- `CaseStatusName`
- `GravityOffence`
- `BriefFacts` (Currently synthetic)

Fields needing PII masking (if actual data is eventually loaded):
- `VictimName`
- Exact `latitude`/`longitude` in public exports (approximate via cluster is safe)
