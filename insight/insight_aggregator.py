from typing import List, Dict

class InsightAggregator:

    def aggregate_insights(self, top_matches: List[Dict]) -> Dict:
        if not top_matches:
            return {
                "diagnosis": "Unknown condition",
                "treatment": "No treatment pattern available"
            }

        diagnosis_score = {}
        treatment_score = {}

        for case in top_matches:
            diagnosis = case.get("diagnosis")
            treatment = case.get("treatment")
            similarity = float(case.get("similarity", 0.0))

            if diagnosis:
                diagnosis_score[diagnosis] = diagnosis_score.get(diagnosis, 0.0) + similarity
            if treatment:
                treatment_score[treatment] = treatment_score.get(treatment, 0.0) + similarity

        predicted_diagnosis = max(diagnosis_score, key=diagnosis_score.get) if diagnosis_score else "Unknown condition"
        predicted_treatment = max(treatment_score, key=treatment_score.get) if treatment_score else "No treatment pattern found"

        return {
            "diagnosis": predicted_diagnosis,
            "treatment": predicted_treatment
        }