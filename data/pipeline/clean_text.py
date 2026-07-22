import pandas as pd
import re

def clean_brief_facts(df: pd.DataFrame, text_column: str = 'BriefFacts') -> pd.DataFrame:
    """
    Cleans the BriefFacts column for TF-IDF / NLP pipelines.
    - Lowercase
    - Remove punctuation and special characters
    - Normalize whitespace
    """
    if text_column not in df.columns:
        return df
        
    df_clean = df.copy()
    
    def normalize_text(text):
        if not isinstance(text, str):
            return ""
        # Lowercase
        text = text.lower()
        # Remove punctuation
        text = re.sub(r'[^\w\s]', ' ', text)
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    df_clean[f"{text_column}_Cleaned"] = df_clean[text_column].apply(normalize_text)
    
    print(f"[CLEAN_TEXT] Cleaned {len(df_clean)} text fields.")
    return df_clean
