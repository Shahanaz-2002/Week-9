from config import TOP_K

class ConfidenceEngine:

    def compute_confidence(self, retrieved_cases: list) -> dict:
        if not retrieved_cases:
            return {
                "confidence_score": 0.0,
                "confidence_level": "None"
            }

        similarities = [float(case.get("similarity", 0)) for case in retrieved_cases]
        avg_similarity = sum(similarities) / len(similarities)

        # Scale based on how many cases we actually found vs how many we wanted
        support_ratio = len(retrieved_cases) / TOP_K if TOP_K > 0 else 0
        confidence_score = (0.75 * avg_similarity) + (0.25 * support_ratio)

        if confidence_score >= 0.85:
            level = "Very High"
        elif confidence_score >= 0.70:
            level = "High"
        elif confidence_score >= 0.50:
            level = "Moderate"
        else:
            level = "Low"

        return {
            "confidence_score": round(confidence_score, 3),
            "confidence_level": level
        }