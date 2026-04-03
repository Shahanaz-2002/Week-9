from pydantic import BaseModel, Field, validator
from typing import List, Optional


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

    # 🔹 VALIDATORS

    @validator("patient_id")
    def validate_patient_id(cls, v):
        if not v or not v.strip():
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