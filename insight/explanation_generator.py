class ExplanationGenerator:

    def generate_explanation(self, insight: dict, retrieved_cases: list) -> str:
        if not retrieved_cases:
            return "Insufficient historical data. Clinical recommendation should be made utilizing standard diagnostic protocols."

        diagnosis = insight.get("diagnosis", "an unspecified condition")
        treatment = insight.get("treatment", "standard care")
        case_count = len(retrieved_cases)
        
        similarities = [float(case.get("similarity", 0)) for case in retrieved_cases]
        avg_similarity = (sum(similarities) / len(similarities)) * 100

        explanation = (
            f"Analysis identified {case_count} highly analogous historical cases "
            f"(Average semantic match: {avg_similarity:.1f}%). "
            f"Within this cohort, the predominant clinical diagnosis was '{diagnosis}'. "
            f"Historical patient records indicate positive therapeutic response to '{treatment}'. "
            f"This precedent suggests '{treatment}' as a highly viable intervention pathway for the current presentation."
        )

        return explanation