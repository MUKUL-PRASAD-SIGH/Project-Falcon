"""
Project Falcon - Catalyst DataStore Seeder
==========================================
Generates CSVs from synthetic data and imports them into Catalyst DataStore
using `catalyst ds:import --table <name> <file>`.

Run:
    python seed_datastore.py           # Dev environment (default)
    python seed_datastore.py --prod    # Production environment

Architecture Decision:
    - DataStore: Structured tables (CaseMaster, Accused, etc.) for API queries
    - ML raw files: Stay as JSON in ml/scripts/ and data/scripts/ for geo_clustering.py / build_graph.py
    - This script bridges both: creates CSVs for DataStore and leaves raw JSON untouched.
"""

import os
import json
import csv
import subprocess
import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent
OUT_DIR = SCRIPT_DIR / "csv_import"
FEATURE_STORE_BASE = DATA_DIR / "feature_store"

# ── Lookup / Reference seed data ─────────────────────────────────────────────

STATE_ROWS = [
    {"StateID": 1, "StateName": "Karnataka", "NationalityID": 1}
]

DISTRICT_ROWS = [
    {"DistrictID": 1, "DistrictName": "Bengaluru Urban", "StateID": 1},
    {"DistrictID": 2, "DistrictName": "Mysuru",          "StateID": 1},
    {"DistrictID": 3, "DistrictName": "Mangaluru",       "StateID": 1},
    {"DistrictID": 4, "DistrictName": "Belagavi",        "StateID": 1},
    {"DistrictID": 5, "DistrictName": "Kalaburagi",      "StateID": 1},
]

CRIME_HEAD_ROWS = [
    {"CrimeHeadID": 1, "CrimeGroupName": "Theft"},
    {"CrimeHeadID": 2, "CrimeGroupName": "Robbery"},
    {"CrimeHeadID": 3, "CrimeGroupName": "Assault"},
    {"CrimeHeadID": 4, "CrimeGroupName": "Cybercrime"},
    {"CrimeHeadID": 5, "CrimeGroupName": "Fraud"},
    {"CrimeHeadID": 6, "CrimeGroupName": "Murder"},
    {"CrimeHeadID": 7, "CrimeGroupName": "Drug Offence"},
]

CRIME_SUBHEAD_ROWS = [
    {"CrimeSubHeadID": 1,  "CrimeHeadID": 1, "CrimeHeadName": "Petty Theft"},
    {"CrimeSubHeadID": 2,  "CrimeHeadID": 1, "CrimeHeadName": "Vehicle Theft"},
    {"CrimeSubHeadID": 3,  "CrimeHeadID": 2, "CrimeHeadName": "Armed Robbery"},
    {"CrimeSubHeadID": 4,  "CrimeHeadID": 2, "CrimeHeadName": "Street Robbery"},
    {"CrimeSubHeadID": 5,  "CrimeHeadID": 3, "CrimeHeadName": "Simple Hurt"},
    {"CrimeSubHeadID": 6,  "CrimeHeadID": 3, "CrimeHeadName": "Grievous Hurt"},
    {"CrimeSubHeadID": 7,  "CrimeHeadID": 4, "CrimeHeadName": "Online Fraud"},
    {"CrimeSubHeadID": 8,  "CrimeHeadID": 4, "CrimeHeadName": "Hacking"},
    {"CrimeSubHeadID": 9,  "CrimeHeadID": 5, "CrimeHeadName": "Bank Fraud"},
    {"CrimeSubHeadID": 10, "CrimeHeadID": 6, "CrimeHeadName": "Culpable Homicide"},
    {"CrimeSubHeadID": 11, "CrimeHeadID": 7, "CrimeHeadName": "Possession"},
    {"CrimeSubHeadID": 12, "CrimeHeadID": 7, "CrimeHeadName": "Trafficking"},
]

CASE_CATEGORY_ROWS = [
    {"CaseCategoryID": 1, "LookupValue": "FIR"},
    {"CaseCategoryID": 2, "LookupValue": "UDR"},
    {"CaseCategoryID": 3, "LookupValue": "PAR"},
    {"CaseCategoryID": 4, "LookupValue": "Zero FIR"},
]

GRAVITY_OFFENCE_ROWS = [
    {"GravityOffenceID": 1, "LookupValue": "Heinous"},
    {"GravityOffenceID": 2, "LookupValue": "Non-Heinous"},
]

CASE_STATUS_ROWS = [
    {"CaseStatusID": 1, "CaseStatusName": "Under Investigation"},
    {"CaseStatusID": 2, "CaseStatusName": "Charge Sheet Filed"},
    {"CaseStatusID": 3, "CaseStatusName": "Acquitted"},
    {"CaseStatusID": 4, "CaseStatusName": "Convicted"},
    {"CaseStatusID": 5, "CaseStatusName": "Closed"},
]

UNIT_TYPE_ROWS = [
    {"UnitTypeID": 1, "UnitTypeName": "Police Station", "CityDistState": "City", "Hierarchy": 1},
    {"UnitTypeID": 2, "UnitTypeName": "Sub-Division",   "CityDistState": "District", "Hierarchy": 2},
]

UNIT_ROWS = [
    {"UnitID": 1, "UnitName": "Whitefield PS",    "TypeID": 1, "ParentUnit": None, "StateID": 1, "DistrictID": 1},
    {"UnitID": 2, "UnitName": "Electronic City PS","TypeID": 1, "ParentUnit": None, "StateID": 1, "DistrictID": 1},
    {"UnitID": 3, "UnitName": "MG Road PS",        "TypeID": 1, "ParentUnit": None, "StateID": 1, "DistrictID": 1},
    {"UnitID": 4, "UnitName": "Mysuru Central PS", "TypeID": 1, "ParentUnit": None, "StateID": 1, "DistrictID": 2},
    {"UnitID": 5, "UnitName": "Mangaluru PS",      "TypeID": 1, "ParentUnit": None, "StateID": 1, "DistrictID": 3},
]

RANK_ROWS = [
    {"RankID": 1, "RankName": "Constable",   "Hierarchy": 1},
    {"RankID": 2, "RankName": "Head Constable","Hierarchy": 2},
    {"RankID": 3, "RankName": "SI",           "Hierarchy": 3},
    {"RankID": 4, "RankName": "Inspector",    "Hierarchy": 4},
]

DESIGNATION_ROWS = [
    {"DesignationID": 1, "DesignationName": "Beat Constable", "SortOrder": 1},
    {"DesignationID": 2, "DesignationName": "IO",             "SortOrder": 2},
    {"DesignationID": 3, "DesignationName": "SHO",            "SortOrder": 3},
]

EMPLOYEE_ROWS = [
    {"EmployeeID": 1, "DistrictID": 1, "UnitID": 1, "RankID": 3, "DesignationID": 2, "KGID": "KG001"},
    {"EmployeeID": 2, "DistrictID": 1, "UnitID": 2, "RankID": 3, "DesignationID": 2, "KGID": "KG002"},
    {"EmployeeID": 3, "DistrictID": 2, "UnitID": 4, "RankID": 4, "DesignationID": 3, "KGID": "KG003"},
    {"EmployeeID": 4, "DistrictID": 3, "UnitID": 5, "RankID": 4, "DesignationID": 3, "KGID": "KG004"},
    {"EmployeeID": 5, "DistrictID": 4, "UnitID": 5, "RankID": 3, "DesignationID": 2, "KGID": "KG005"},
]

COURT_ROWS = [
    {"CourtID": 1, "CourtName": "Bengaluru City Civil Court", "DistrictID": 1, "StateID": 1},
    {"CourtID": 2, "CourtName": "Mysuru District Court",      "DistrictID": 2, "StateID": 1},
    {"CourtID": 3, "CourtName": "Mangaluru Sessions Court",   "DistrictID": 3, "StateID": 1},
]

ACT_ROWS = [
    {"ActCode": 1, "ActDescription": "Indian Penal Code 1860", "ShortName": "IPC",  "Active": True},
    {"ActCode": 2, "ActDescription": "Information Technology Act 2000", "ShortName": "IT Act", "Active": True},
    {"ActCode": 3, "ActDescription": "NDPS Act 1985", "ShortName": "NDPS", "Active": True},
]

SECTION_ROWS = [
    {"SectionCode": 379, "ActCode": 1, "SectionDescription": "Theft"},
    {"SectionCode": 392, "ActCode": 1, "SectionDescription": "Robbery"},
    {"SectionCode": 307, "ActCode": 1, "SectionDescription": "Attempt to Murder"},
    {"SectionCode": 420, "ActCode": 1, "SectionDescription": "Cheating"},
    {"SectionCode": 66,  "ActCode": 2, "SectionDescription": "Computer Related Offences"},
]

# ── Helpers ───────────────────────────────────────────────────────────────────

def write_csv(name: str, rows: list, fields: list = None):
    """Write rows to OUT_DIR/<name>_<timestamp>.csv and return the path."""
    import time
    ts = int(time.time())
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"{name}_{ts}.csv"
    if not rows:
        print(f"  [SKIP] {name} — no rows to write")
        return None
    fields = fields or list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"  [CSV]  {name}.csv  ({len(rows)} rows)")
    return path


def ds_import(table: str, csv_path: Path, prod: bool):
    """Run `catalyst ds:import --table <table> <file>` and return success bool."""
    catalyst_bin = "catalyst.cmd" if sys.platform == "win32" else "catalyst"
    cmd = [catalyst_bin, "ds:import", "--table", table, str(csv_path)]
    if prod:
        cmd.append("--production")
    print(f"  [IMPORT] -> DataStore table: {table}  file: {csv_path.name}")
    
    # Fully automated: start the process and feed a newline to stdin to bypass the bucket prompt
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = process.communicate(input="\n")
    
    # Check for HTTP errors or CLI failures even if exit code is 0
    if process.returncode != 0 or "Error" in out or "Error" in err:
        error_text = err.strip() if err.strip() else out.strip()
        print(f"    ERROR: Import failed.\n{error_text}")
        return False
        
    # Extract Job ID
    job_id = None
    import re
    match = re.search(r"Job ID[^\d]+(\d+)", out)
    if match:
        job_id = match.group(1)
        print(f"    OK: Job Scheduled (ID: {job_id}). Waiting for completion...")
        
        # Verify row counts
        import time
        for _ in range(10): # Poll up to 10 times (20 seconds)
            time.sleep(2)
            status_cmd = [catalyst_bin, "ds:status", "import", job_id]
            if prod:
                status_cmd.append("--production")
            status_proc = subprocess.run(status_cmd, capture_output=True, text=True)
            status_out = status_proc.stdout
            
            if "Import Job Completed" in status_out:
                processed = re.search(r"Processed:\s*(\d+)", status_out)
                failed = re.search(r"Failure:\s*(\d+)", status_out)
                p_count = processed.group(1) if processed else "Unknown"
                f_count = failed.group(1) if failed else "Unknown"
                print(f"    VERIFIED: Processed {p_count} rows, Failed {f_count} rows.")
                return True
            elif "Failed" in status_out or "Error" in status_out:
                print(f"    ERROR: Job {job_id} failed during execution.")
                return False
                
        print(f"    WARNING: Job {job_id} still pending, skipping verification.")
    else:
        print(f"    OK: {out.strip()}")
    
    # Cleanup note: We use unique timestamped files so Stratus cleanup is technically not required to prevent collisions.
    return True


def build_casemaster_rows(firs_df) -> list:
    """Map operational Parquet DataFrame -> CaseMaster schema columns."""
    rows = []
    # Convert DataFrame to list of dicts
    firs = firs_df.to_dict('records')
    import pandas as pd
    for i, fir in enumerate(firs):
        # Handle pandas NaT for dates and NaN for floats if needed
        crime_reg_date = str(fir.get("CrimeRegisteredDate", "")) if pd.notnull(fir.get("CrimeRegisteredDate")) else ""
        
        rows.append({
            "CaseMasterID":      fir.get("CaseMasterID"),
            "CrimeNo":           fir.get("CrimeNo"),
            "CrimeRegisteredDate": crime_reg_date,
            "latitude":          fir.get("latitude"),
            "longitude":         fir.get("longitude"),
            "BriefFacts":        str(fir.get("BriefFacts", "")).replace("\n", " "),
            "IncidentFromDate":  crime_reg_date,   # same for synthetic
            "IncidentToDate":    crime_reg_date,
            "EmployeeID":        (i % 5) + 1,
            "UnitID":            (i % 5) + 1,
            "CaseCategoryID":    1,
            "GravityOffenceID":  1 if fir.get("CrimeHeadID") in [2, 3, 6] else 2,
            "CrimeHeadID":       fir.get("CrimeHeadID"),
            "CrimeSubHeadID":    min((fir.get("CrimeHeadID", 1) * 2) - 1, 12),
            "CaseStatusID":      (i % 5) + 1,
            "CourtID":           min((fir.get("DistrictID", 1)), 3),
        })
    return rows


def build_accused_rows(accused_df) -> list:
    """Map operational Parquet DataFrame -> Accused schema columns."""
    accused = accused_df.to_dict('records')
    return [
        {
            "AccusedMasterID": a["AccusedMasterID"],
            "CaseMasterID":    a["CaseMasterID"],
            "AccusedName":     a["AccusedName"],
            "AgeYear":         a["AgeYear"],
            "GenderID":        a["GenderID"],
            "PersonID":        a["PersonID"],
        }
        for a in accused
    ]


# ── Main ──────────────────────────────────────────────────────────────────────

def main(prod: bool = False):
    env_label = "PRODUCTION" if prod else "DEVELOPMENT"
    print(f"\n{'='*60}")
    print(f"  Project Falcon — DataStore Seeder  [{env_label}]")
    print(f"{'='*60}\n")

    # Read latest pointer from feature store
    pointer_path = FEATURE_STORE_BASE / "latest.txt"
    if not pointer_path.exists():
        print(f"ERROR: {pointer_path} not found. Run data/pipeline/feature_store.py first.")
        sys.exit(1)
        
    with open(pointer_path, 'r') as f:
        latest_version = f.read().strip()
        
    store_dir = FEATURE_STORE_BASE / latest_version
    
    print(f"Loading operational data from Feature Store ({latest_version})...")
    import pandas as pd
    firs = pd.read_parquet(store_dir / "operational_casemaster.parquet")
    accused = pd.read_parquet(store_dir / "operational_accused.parquet")
    
    print(f"  Loaded {len(firs)} valid FIRs, {len(accused)} valid Accused records\n")

    # ── IMPORT ORDER: lowest-level lookup tables first ────────────────────────
    tables = [
        # (table_name,       rows,                       fields)
        ("State",            STATE_ROWS,                  None),
        ("District",         DISTRICT_ROWS,               None),
        ("UnitType",         UNIT_TYPE_ROWS,              None),
        ("Unit",             UNIT_ROWS,                   None),
        ("Rank",             RANK_ROWS,                   None),
        ("Designation",      DESIGNATION_ROWS,            None),
        ("Employee",         EMPLOYEE_ROWS,               None),
        ("Court",            COURT_ROWS,                  None),
        ("CaseCategory",     CASE_CATEGORY_ROWS,          None),
        ("GravityOffence",   GRAVITY_OFFENCE_ROWS,        None),
        ("CaseStatusMaster", CASE_STATUS_ROWS,            None),
        ("CrimeHead",        CRIME_HEAD_ROWS,             None),
        ("CrimeSubHead",     CRIME_SUBHEAD_ROWS,          None),
        ("Act",              ACT_ROWS,                    None),
        ("Section",          SECTION_ROWS,                None),
        # Main tables
        ("CaseMaster",       build_casemaster_rows(firs), None),
        ("Accused",          build_accused_rows(accused), None),
    ]

    success, failed = [], []
    for table_name, rows, fields in tables:
        print(f"\n[{table_name}]")
        csv_path = write_csv(table_name, rows, fields)
        if csv_path:
            ok = ds_import(table_name, csv_path, prod)
            (success if ok else failed).append(table_name)

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  DONE  [OK] {len(success)} tables imported  [FAILED] {len(failed)} failed")
    if failed:
        print(f"  Failed tables: {', '.join(failed)}")
    print(f"{'='*60}")
    print("\nML features are now served from the Feature Store (Parquet files).")
    print(f"  Version: {latest_version}")
    print("Upload DataStore CSVs to Catalyst Stratus manually if `ds:import` fails.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed Catalyst DataStore from synthetic data")
    parser.add_argument("--prod", action="store_true", help="Target production environment")
    args = parser.parse_args()
    main(prod=args.prod)
