import time
import logging
from fastapi import FastAPI, HTTPException
import uvicorn

from models.models import CaseRequest, CaseResponse, SimilarCase, SystemMetrics
from retrieval.retrieval_engine import retrieve_similar_cases
from retrieval.database import fetch_case_database
from insight.insight_aggregator import InsightAggregator
from insight.confidence_engine import ConfidenceEngine
from insight.explanation_generator import ExplanationGenerator
from config import TOP_K

# 🔹 Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [%(name)s] - %(message)s",
    force=True
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Clinical Insight Engine API", version="1.0")

# 🔹 Initialize Engines & Cache DB
logger.info("Initializing Insight Engines and loading Case Database...")

try:
    case_database = fetch_case_database()
    if not case_database:
        logger.warning("Case database is empty or failed to load!")
        case_database = []
    else:
        logger.info(f"Successfully loaded {len(case_database)} cases into memory.")
except Exception as e:
    logger.error(f"Database initialization failed: {e}")
    case_database = []

insight_aggregator = InsightAggregator()
confidence_engine = ConfidenceEngine()
explanation_generator = ExplanationGenerator()


@app.post("/analyze-case", response_model=CaseResponse)
def analyze_case(request: CaseRequest):
    start_time = time.time()

    # 🔹 =========================
    # INPUT VALIDATION (Enhanced)
    # 🔹 =========================

    # Symptoms validation
    if not request.symptoms or not isinstance(request.symptoms, list) or len(request.symptoms) == 0:
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "message": "Symptoms must be a non-empty list"
            }
        )

    # Check for empty strings inside symptoms
    if any(not s or not s.strip() for s in request.symptoms):
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "message": "Symptoms list contains empty values"
            }
        )

    # Age validation
    if request.age < 0 or request.age > 120:
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "message": "Invalid age. Must be between 0 and 120"
            }
        )

    # Gender validation
    if request.gender.lower() not in ["male", "female", "other"]:
        raise HTTPException(
            status_code=400,
            detail={
                "status": "error",
                "message": "Invalid gender value"
            }
        )

    logger.info(f"Received request | Symptoms: {len(request.symptoms)} | Age: {request.age}")

    try:
        # 🔹 =========================
        # INPUT FORMATTING
        # 🔹 =========================
        doctor_notes = request.doctor_notes.strip() if request.doctor_notes else ""

        query_text = " ".join(request.symptoms).strip()
        if doctor_notes:
            query_text += " " + doctor_notes

        # Final safety check
        if not query_text:
            raise HTTPException(
                status_code=400,
                detail={
                    "status": "error",
                    "message": "Query text is empty after processing input"
                }
            )

        logger.info("Input text formatted successfully.")

        # 🔹 =========================
        # RETRIEVAL
        # 🔹 =========================
        logger.info(f"Retrieving top {TOP_K} similar cases...")

        top_matches = retrieve_similar_cases(
            query_text=query_text,
            case_database=case_database,
            top_k=TOP_K
        )

        if not top_matches:
            logger.warning("No similar cases found.")

            response_time = round((time.time() - start_time) * 1000, 2)

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

        logger.info(f"{len(top_matches)} similar cases retrieved.")

        # 🔹 =========================
        # INSIGHT GENERATION
        # 🔹 =========================
        insight = insight_aggregator.aggregate_insights(top_matches)

        if not insight:
            raise ValueError("Insight aggregation failed")

        # 🔹 =========================
        # CONFIDENCE
        # 🔹 =========================
        confidence_data = confidence_engine.compute_confidence(top_matches)

        # 🔹 =========================
        # EXPLANATION
        # 🔹 =========================
        explanation = explanation_generator.generate_explanation(insight, top_matches)

        # 🔹 =========================
        # FORMAT SIMILAR CASES
        # 🔹 =========================
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
                logger.warning(f"Skipping malformed case: {e}")

        response_time = round((time.time() - start_time) * 1000, 2)

        logger.info(f"Request completed in {response_time} ms")

        # 🔹 =========================
        # FINAL RESPONSE
        # 🔹 =========================
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
        raise  # rethrow FastAPI errors

    except Exception as e:
        logger.error("Pipeline failure", exc_info=True)

        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Internal Server Error",
                "debug": str(e)  # remove in production if needed
            }
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)