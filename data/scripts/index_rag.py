import json
import pandas as pd
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_FIRS = BASE_DIR / "data" / "scripts" / "firs_synthetic.json"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

# Mappings for metadata readability
CRIME_HEAD_MAP = {
    1: "Theft",
    2: "Robbery",
    3: "Assault",
    4: "Cybercrime",
    5: "Fraud",
    6: "Narcotics",
    7: "Homicide"
}

DISTRICT_MAP = {
    1: "Bengaluru City",
    2: "Mysuru City",
    3: "Mangaluru City",
    4: "Hubballi-Dharwad",
    5: "Belagavi"
}

def format_fir_corpus():
    print("Formatting FIR corpus for QuickML RAG Knowledge Base...")
    
    if not RAW_FIRS.exists():
        print(f"Error: {RAW_FIRS} does not exist. Run generate_synthetic.py first.")
        return
        
    with open(RAW_FIRS, 'r') as f:
        firs = json.load(f)
        
    documents = []
    for fir in firs:
        case_id = fir["CaseMasterID"]
        crime_no = fir["CrimeNo"]
        date = fir["CrimeRegisteredDate"]
        brief_facts = fir["BriefFacts"]
        
        district_name = DISTRICT_MAP.get(fir["DistrictID"], "Unknown District")
        crime_name = CRIME_HEAD_MAP.get(fir["CrimeHeadID"], "Unknown Crime")
        
        # Build structured text block for the Vector Store / Knowledge Base
        document_text = (
            f"Case ID: {case_id}\n"
            f"FIR Number: {crime_no}\n"
            f"Date Registered: {date}\n"
            f"District: {district_name}\n"
            f"Crime Category: {crime_name}\n"
            f"Facts of Case: {brief_facts}"
        )
        
        documents.append({
            "document_id": f"FIR_{case_id}",
            "case_master_id": case_id,
            "crime_no": crime_no,
            "text": document_text
        })
        
    df = pd.DataFrame(documents)
    
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = PROCESSED_DIR / "fir_rag_documents.csv"
    df.to_csv(csv_path, index=False)
    
    print(f"Successfully generated RAG dataset: {csv_path}")
    print(f"Total documents prepared: {len(df)}")
    
if __name__ == "__main__":
    format_fir_corpus()
