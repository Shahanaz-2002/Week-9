from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class InsightAggregator:

    def aggregate_insights(self, top_matches: List[Dict]) -> Dict:
        # 🔹 Input Validation
        if not isinstance(top_matches, list):
            logger.error("Invalid input: top_matches is not a list")
            raise ValueError("top_matches must be a list")

        if not top_matches:
            logger.warning("No matches provided to aggregator")
            return {
                "diagnosis": "Unknown condition",
                "treatment": "No treatment pattern available"
            }

        diagnosis_score = {}
        treatment_score = {}

        # 🔹 Process Each Case Safely
        for case in top_matches:
            if not isinstance(case, dict):
                logger.warning(f"Skipping invalid case (not dict): {case}")
                continue

            try:
                diagnosis = case.get("diagnosis")
                treatment = case.get("treatment")
                similarity = float(case.get("similarity", 0.0))

                # Skip invalid similarity
                if similarity < 0:
                    logger.warning(f"Invalid similarity value: {similarity}")
                    continue

                # Aggregate diagnosis scores
                if diagnosis and isinstance(diagnosis, str) and diagnosis.strip():
                    diagnosis_clean = diagnosis.strip()
                    diagnosis_score[diagnosis_clean] = (
                        diagnosis_score.get(diagnosis_clean, 0.0) + similarity
                    )

                # Aggregate treatment scores
                if treatment and isinstance(treatment, str) and treatment.strip():
                    treatment_clean = treatment.strip()
                    treatment_score[treatment_clean] = (
                        treatment_score.get(treatment_clean, 0.0) + similarity
                    )

            except Exception as e:
                logger.warning(f"Skipping malformed case due to error: {e}")
                continue

        # 🔹 Final Prediction
        if diagnosis_score:
            predicted_diagnosis = max(diagnosis_score, key=diagnosis_score.get)
        else:
            predicted_diagnosis = "Unknown condition"

        if treatment_score:
            predicted_treatment = max(treatment_score, key=treatment_score.get)
        else:
            predicted_treatment = "No treatment pattern found"

        logger.info(f"Predicted Diagnosis: {predicted_diagnosis}")
        logger.info(f"Predicted Treatment: {predicted_treatment}")

        return {
            "diagnosis": predicted_diagnosis,
            "treatment": predicted_treatment
        }