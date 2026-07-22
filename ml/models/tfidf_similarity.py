import os
import json
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_SCRIPTS_DIR = BASE_DIR / "data" / "scripts"
RAW_FIRS = DATA_SCRIPTS_DIR / "firs_synthetic.json"
OUTPUTS_DIR = BASE_DIR / "ml" / "outputs"
SCRIPTS_OUT = BASE_DIR / "ml" / "scripts"

CRIME_HEAD_MAP = {
    1: "Theft", 2: "Robbery", 3: "Assault", 4: "Cybercrime",
    5: "Fraud", 6: "Narcotics", 7: "Homicide"
}

DISTRICT_MAP = {
    1: "Bengaluru City", 2: "Mysuru City", 3: "Mangaluru City",
    4: "Hubballi-Dharwad", 5: "Belagavi"
}

class TFIDFCaseSimilarity:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=1000
        )
        self.df_firs = None
        self.tfidf_matrix = None
        self.similarity_matrix = None

    def fit_and_index(self):
        print("Loading FIR records for TF-IDF similarity model...")
        with open(RAW_FIRS, 'r') as f:
            firs_data = json.load(f)
            
        self.df_firs = pd.DataFrame(firs_data)
        self.df_firs['CrimeHeadName'] = self.df_firs['CrimeHeadID'].map(lambda x: CRIME_HEAD_MAP.get(x, "General Crime"))
        self.df_firs['DistrictName'] = self.df_firs['DistrictID'].map(lambda x: DISTRICT_MAP.get(x, "Karnataka"))
        
        # Build composite document for TF-IDF search
        self.df_firs['composite_text'] = (
            self.df_firs['BriefFacts'].fillna('') + " " +
            self.df_firs['CrimeHeadName'] + " " +
            self.df_firs['DistrictName']
        )
        
        print(f"Fitting TF-IDF Vectorizer on {len(self.df_firs)} FIR composite texts...")
        self.tfidf_matrix = self.vectorizer.fit_transform(self.df_firs['composite_text'])
        
        print("Computing Cosine Similarity matrix...")
        self.similarity_matrix = cosine_similarity(self.tfidf_matrix, self.tfidf_matrix)
        
        # Save output index JSON
        self._export_similarity_index()
        return self

    def get_similar_cases(self, case_id: int, top_n: int = 5):
        if self.df_firs is None:
            self.fit_and_index()
            
        # Find index of target case_id
        matches = self.df_firs.index[self.df_firs['CaseMasterID'] == case_id].tolist()
        if not matches:
            # Fallback to first record if not found
            target_idx = 0
        else:
            target_idx = matches[0]
            
        sim_scores = list(enumerate(self.similarity_matrix[target_idx]))
        # Sort descending by score
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        # Top N excluding self (index target_idx)
        top_indices = [idx for idx, score in sim_scores if idx != target_idx][:top_n]
        
        results = []
        for idx in top_indices:
            row = self.df_firs.iloc[idx]
            results.append({
                "CaseMasterID": int(row['CaseMasterID']),
                "CrimeNo": row['CrimeNo'],
                "similarity_score": round(float(self.similarity_matrix[target_idx][idx]), 4),
                "CrimeRegisteredDate": str(row['CrimeRegisteredDate']),
                "District": row['DistrictName'],
                "CrimeHead": row['CrimeHeadName'],
                "BriefFacts": row['BriefFacts']
            })
            
        return results

    def _export_similarity_index(self):
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        SCRIPTS_OUT.mkdir(parents=True, exist_ok=True)
        
        # Generate sample lookup dictionary for API pre-caching
        index_data = {}
        sample_cases = self.df_firs['CaseMasterID'].head(50).tolist()
        
        for case_id in sample_cases:
            index_data[str(case_id)] = self.get_similar_cases(case_id, top_n=5)
            
        with open(OUTPUTS_DIR / "similarity_index.json", 'w') as f:
            json.dump(index_data, f, indent=2)
            
        with open(SCRIPTS_OUT / "similarity_index.json", 'w') as f:
            json.dump(index_data, f, indent=2)
            
        print("Exported pre-computed similarity index to similarity_index.json")

def build_tfidf_model():
    model = TFIDFCaseSimilarity()
    model.fit_and_index()
    sample_sims = model.get_similar_cases(1, top_n=3)
    print(f"\n[TF-IDF MODEL DONE] Sample similar cases for Case #1:\n{json.dumps(sample_sims, indent=2)}")
    return model

if __name__ == "__main__":
    build_tfidf_model()
