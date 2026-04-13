import time

from fastapi import HTTPException

from models.models import CaseResponse, SimilarCase, SystemMetrics
from retrieval.retrieval_engine import retrieve_similar_cases
from retrieval.database import fetch_case_database
from insight.insight_aggregator import InsightAggregator
from insight.confidence_engine import ConfidenceEngine
from insight.explanation_generator import ExplanationGenerator
from config import TOP_K


#  Initialize once
case_database = fetch_case_database()

insight_aggregator = InsightAggregator()
confidence_engine = ConfidenceEngine()
explanation_generator = ExplanationGenerator()


def analyze_case_pipeline(request, request_id, log_event=None):
    start_time = time.time()

    try:
        
        # INPUT FORMATTING
        
        doctor_notes = request.doctor_notes.strip() if request.doctor_notes else ""
        query_text = " ".join(request.symptoms).strip()

        if doctor_notes:
            query_text += " " + doctor_notes

        if not query_text:
            raise HTTPException(status_code=400, detail="Query text is empty")

        if log_event:
            log_event("input_processed", request_id, "Input formatted successfully")

        
        # RETRIEVAL
        
        retrieval_start = time.time()

        if log_event:
            log_event("retrieval_started", request_id, f"Fetching top {TOP_K} cases")

        top_matches = retrieve_similar_cases(
            query_text=query_text,
            case_database=case_database,
            top_k=TOP_K
        )

        retrieval_time = round((time.time() - retrieval_start) * 1000, 2)

        if log_event:
            log_event("retrieval_completed", request_id, "Cases retrieved", {
                "num_cases": len(top_matches) if top_matches else 0,
                "retrieval_time_ms": retrieval_time
            })

       
        # NO MATCH CASE
        
        if not top_matches:
            response_time = round((time.time() - start_time) * 1000, 2)

            if log_event:
                log_event("no_cases_found", request_id, "No similar cases found")

            return CaseResponse(
                status="success",
                similar_cases=[],
                predicted_diagnosis="No matching cases found",
                suggested_treatment="Not available",
                confidence_score=0.0,
                confidence_level="Low",
                clinical_explanation="No similar clinical patterns were found in the database.",
                system_metrics=SystemMetrics(
                    response_time_ms=response_time,
                    output_quality="Poor - No Matches"
                )
            )

       
        # INSIGHT GENERATION
      
        insight = insight_aggregator.aggregate_insights(top_matches)

        if not insight:
            raise ValueError("Insight aggregation failed")

        if log_event:
            log_event("insight_generated", request_id, "Insight created", {
                "diagnosis": insight.get("diagnosis")
            })

        
        # CONFIDENCE
        
        confidence_data = confidence_engine.compute_confidence(top_matches)

        if log_event:
            log_event("confidence_computed", request_id, "Confidence calculated", {
                "score": confidence_data.get("confidence_score")
            })

       
        # EXPLANATION
        
        explanation = explanation_generator.generate_explanation(insight, top_matches)

        if log_event:
            log_event("explanation_generated", request_id, "Explanation created")

        
        # FORMAT SIMILAR CASES
        
        similar_cases_formatted = []

        for c in top_matches:
            try:
                similar_cases_formatted.append(
                    SimilarCase(
                        case_id=c.get("case_id", "Unknown"),
                        similarity_score=float(c.get("similarity", 0.0)),
                        diagnosis=c.get("diagnosis", "Unknown"),
                        treatment=c.get("treatment", "Unknown")
                    )
                )
            except Exception as e:
                if log_event:
                    log_event("case_format_warning", request_id, "Malformed case skipped", {
                        "error": str(e)
                    })

        
        # FINAL RESPONSE
        
        response_time = round((time.time() - start_time) * 1000, 2)

        if log_event:
            log_event("response_ready", request_id, "Response prepared", {
                "response_time_ms": response_time
            })

        return CaseResponse(
            status="success",
            similar_cases=similar_cases_formatted,
            predicted_diagnosis=insight.get("diagnosis", "Unknown"),
            suggested_treatment=insight.get("treatment", "Not specified"),
            confidence_score=confidence_data.get("confidence_score", 0.0),
            confidence_level=confidence_data.get("confidence_level", "Unknown"),
            clinical_explanation=explanation,
            system_metrics=SystemMetrics(
                response_time_ms=response_time,
                output_quality="High" if confidence_data.get("confidence_score", 0) > 0.7 else "Moderate"
            )
        )

    except HTTPException:
        raise

    except Exception as e:
        if log_event:
            log_event("pipeline_error", request_id, "Pipeline failure", {
                "error": str(e)
            })

        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Internal Server Error"
            }
        )