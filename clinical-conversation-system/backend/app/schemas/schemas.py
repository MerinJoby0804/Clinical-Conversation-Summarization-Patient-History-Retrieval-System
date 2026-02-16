from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict
from datetime import datetime


# ===== Authentication Schemas =====

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: str = Field(..., pattern="^(doctor|patient)$")


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None


# ===== User Response Schemas =====

class UserResponse(UserBase):
    id: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ===== Doctor Schemas =====

class DoctorCreate(BaseModel):
    license_number: str
    specialization: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None


class DoctorResponse(DoctorCreate):
    id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True


# ===== Patient Schemas =====

class PatientCreate(BaseModel):
    #patient_id: str
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None


class PatientResponse(PatientCreate):
    id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True


# ===== Conversation Schemas =====

class ConversationCreate(BaseModel):
    patient_id: str
    doctor_id: str
    chief_complaint: Optional[str] = None


class ConversationUpdate(BaseModel):
    transcription: Optional[str] = None
    status: Optional[str] = None


class ConversationResponse(BaseModel):
    id: str
    patient_id: str
    doctor_id: str
    conversation_date: datetime
    audio_file_path: Optional[str] = None
    transcription: Optional[str] = None
    chief_complaint: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ===== Entity Extraction Schemas =====

class ExtractedEntityCreate(BaseModel):
    conversation_id: str
    entity_type: str
    entity_value: str
    context: Optional[str] = None
    confidence_score: Optional[float] = None
    start_position: Optional[int] = None
    end_position: Optional[int] = None


class ExtractedEntityResponse(ExtractedEntityCreate):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


# ===== Clinical Summary Schemas =====

class ClinicalSummaryCreate(BaseModel):
    conversation_id: str
    subjective: Optional[str] = None
    objective: Optional[str] = None
    assessment: Optional[str] = None
    plan: Optional[str] = None
    full_summary: Optional[str] = None
    keywords: Optional[List[str]] = None


class ClinicalSummaryResponse(ClinicalSummaryCreate):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===== Medical History Schemas =====

class MedicalHistoryCreate(BaseModel):
    patient_id: str
    category: str
    description: str
    date_recorded: Optional[datetime] = None
    is_active: bool = True
    notes: Optional[str] = None


class MedicalHistoryResponse(MedicalHistoryCreate):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


# ===== Audio Upload Schema =====

class AudioUploadResponse(BaseModel):
    conversation_id: str
    file_path: str
    message: str


# ===== Transcription Schema =====

class TranscriptionRequest(BaseModel):
    conversation_id: str


class TranscriptionResponse(BaseModel):
    conversation_id: str
    transcription: str
    status: str


# ===== Summarization Request =====

class SummarizationRequest(BaseModel):
    conversation_id: str
    include_history: bool = True


# ===== Patient History Retrieval =====

class HistoryRetrievalRequest(BaseModel):
    patient_id: str
    symptoms: List[str]
    include_vitals: bool = True
    include_medications: bool = True
    limit: int = 10


class HistoryRetrievalResponse(BaseModel):
    patient_id: str
    relevant_conversations: List[ConversationResponse]
    relevant_summaries: List[ClinicalSummaryResponse]
    medical_history: List[MedicalHistoryResponse]

    class Config:
        from_attributes = True


# ===== Voice-based Symptom Input =====

class VoiceSymptomRequest(BaseModel):
    patient_id: str
    audio_file_path: str


class VoiceSymptomResponse(BaseModel):
    patient_id: str
    extracted_symptoms: List[str]
    transcription: str
    relevant_history: HistoryRetrievalResponse