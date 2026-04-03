from pydantic import BaseModel, Field, validator
from typing import List, Optional


# 🔹 REQUEST MODEL
class CaseRequest(BaseModel):
    patient_id: str = Field(
        ...,
        min_length=1,
        description="Unique patient identifier"
    )

    symptoms: List[str] = Field(
        ...,
        min_items=1,
        description="List of patient symptoms"
    )

    doctor_notes: Optional[str] = Field(
        None,
        description="Clinical notes from the doctor"
    )

    age: int = Field(
        ...,
        ge=0,
        le=120,
        description="Patient age"
    )

    gender: str = Field(
        ...,
        min_length=1,
        description="Patient gender (male/female/other)"
    )

    # 🔹 Validators

    @validator("patient_id")
    def validate_patient_id(cls, v):
        if not v.strip():
            raise ValueError("patient_id cannot be empty")
        return v.strip()

    @validator("symptoms")
    def validate_symptoms(cls, v):
        if not v or len(v) == 0:
            raise ValueError("Symptoms must not be empty")

        cleaned = []
        for s in v:
            if not s or not s.strip():
                raise ValueError("Symptoms list contains empty values")
            cleaned.append(s.strip())

        return cleaned

    @validator("doctor_notes", always=True)
    def validate_doctor_notes(cls, v):
        if v is None:
            return ""
        return v.strip()

    @validator("gender")
    def validate_gender(cls, v):
        if not v or not v.strip():
            raise ValueError("Gender cannot be empty")

        v_clean = v.strip().lower()

        if v_clean not in ["male", "female", "other"]:
            raise ValueError("Gender must be 'male', 'female', or 'other'")

        return v_clean


# 🔹 SIMILAR CASE MODEL
class SimilarCase(BaseModel):
    case_id: str = Field(..., min_length=1)

    similarity_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Similarity score between 0 and 1"
    )

    diagnosis: str = Field(..., min_length=1)
    treatment: str = Field(..., min_length=1)


# 🔹 SYSTEM METRICS MODEL
class SystemMetrics(BaseModel):
    response_time_ms: float = Field(
        ...,
        ge=0,
        description="API response time in milliseconds"
    )

    output_quality: str = Field(
        ...,
        min_length=1,
        description="Quality of output (High/Moderate/Poor)"
    )


# 🔹 FINAL RESPONSE MODEL
class CaseResponse(BaseModel):
    status: str = Field(
        ...,
        description="success or error"
    )

    similar_cases: List[SimilarCase]

    predicted_diagnosis: str = Field(
        default="Unknown"
    )

    suggested_treatment: str = Field(
        default="No treatment available"
    )

    confidence_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0
    )

    confidence_level: str = Field(
        default="Low"
    )

    clinical_explanation: str = Field(
        default="No explanation available"
    )

    system_metrics: SystemMetrics