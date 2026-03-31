# utils.py

import pandas as pd
import logging
from typing import Dict, Any

# 🔹 Configure utility logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# 🔹 DATA MIGRATION LOADER (CSV to Dictionary format for DB Insertion)
def load_cases_from_csv(file_path: str) -> Dict[str, Dict[str, Any]]:
    """
    Utility function to load historical cases from a CSV file 
    so they can be passed to embedding_store.py and inserted into MongoDB.
    """
    try:
        df = pd.read_csv(file_path)
        case_database: Dict[str, Dict[str, Any]] = {}

        for _, row in df.iterrows():
            case_id = str(row["case_id"]).strip()

            # Convert comma-separated symptoms string into a clean list
            symptoms_raw = str(row.get("symptoms", ""))
            symptoms_list = [s.strip() for s in symptoms_raw.split(",") if s.strip()]

            case_database[case_id] = {
                "case_id": case_id,  
                "symptoms": symptoms_list,
                "diagnosis": str(row.get("diagnosis", "")).strip(),
                "treatment": str(row.get("treatment", "")).strip(),
                "doctor_notes": str(row.get("doctor_notes", "")).strip(),
                "duration_days": row.get("duration_days", 0),
                "clinic_id": str(row.get("clinic_id", "")),
                "patient_age": row.get("patient_age", 0),
                "patient_gender": str(row.get("patient_gender", "")),
                "outcome": str(row.get("outcome", "")).strip(),
                "recovery_days": row.get("recovery_days", 0),
            }

        logger.info(f"Successfully loaded {len(case_database)} cases from {file_path}")
        return case_database

    except Exception as e:
        logger.error(f"Failed to load CSV file at {file_path}: {e}")
        return {}