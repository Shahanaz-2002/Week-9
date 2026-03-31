from pydantic import BaseModel, Field
from typing import List

# 🔹 REQUEST MODEL
class CaseRequest(BaseModel):
    symptoms: List[str] = Field(..., min_items=1, description="List of patient symptoms")
    doctor_notes: str = Field(..., min_length=5, description="Clinical notes from the doctor")

# 🔹 SIMILAR CASE MODEL
class SimilarCase(BaseModel):
    case_id: str
    similarity_score: float = Field(..., ge=0.0, le=1.0)
    diagnosis: str
    treatment: str

# 🔹 SYSTEM METRICS MODEL
class SystemMetrics(BaseModel):
    response_time_ms: float = Field(..., ge=0)
    output_quality: str = Field(..., min_length=1)

# 🔹 FINAL RESPONSE MODEL
class CaseResponse(BaseModel):
    similar_cases: List[SimilarCase]
    predicted_diagnosis: str = Field(default="Unknown")
    suggested_treatment: str = Field(default="No treatment available")
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    confidence_level: str = Field(default="Low Confidence")
    clinical_explanation: str = Field(default="No explanation available")
    system_metrics: SystemMetrics