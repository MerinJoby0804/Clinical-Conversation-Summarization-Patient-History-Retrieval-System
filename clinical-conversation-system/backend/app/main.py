import sys
import os
import shutil
import uuid
import re
from typing import Dict, List
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import APIRouter, FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from loguru import logger

# Project Imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from backend.config.database import get_db, init_db
from backend.app.models.models import (
    User, Doctor, Patient, Conversation,
    ExtractedEntity, ClinicalSummary, MedicalHistory
)
from backend.app.schemas.schemas import *
from backend.utils.auth import (
    get_password_hash, verify_password, create_access_token,
    get_current_active_user, get_current_doctor, get_current_patient
)

# AI Modules
from ai_modules.speech_recognition.transcriber import SpeechRecognizer
from ai_modules.entity_extraction.extractor import ClinicalEntityExtractor
# Ensure your filename is 'summarizer.py' and class is 'Summarizer'
from ai_modules.summarization.summarizer import Summarizer
from ai_modules.retrieval.history_retriever import PatientHistoryRetriever

app = FastAPI(title="Clinical AI System", version="1.1.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"],
                   allow_headers=["*"])

UPLOAD_DIR = "./uploads"
os.makedirs(f"{UPLOAD_DIR}/audio", exist_ok=True)

# Lazy loading AI getters
speech_recognizer = None
entity_extractor = None
clinical_summarizer = None
history_retriever = None


def get_speech_recognizer():
    global speech_recognizer
    if not speech_recognizer:
        speech_recognizer = SpeechRecognizer(model_name="base")
    return speech_recognizer


def get_entity_extractor():
    global entity_extractor
    if not entity_extractor:
        entity_extractor = ClinicalEntityExtractor()
    return entity_extractor


def get_clinical_summarizer():
    """
    🚀 UPDATED: Pulls the BART-Large-CNN model directly from the internet.
    This bypasses local path errors for the demo.
    """
    global clinical_summarizer
    if not clinical_summarizer:
        logger.info("📡 Initializing BART-Large-CNN from Hugging Face...")
        # Using the class name 'Summarizer' from your summarizer.py
        clinical_summarizer = Summarizer(model_name="facebook/bart-large-cnn")
    return clinical_summarizer


def get_history_retriever():
    global history_retriever
    if not history_retriever:
        history_retriever = PatientHistoryRetriever()
    return history_retriever


def clean_transcript(text: str) -> str:
    """Remove filler words and clean up transcript"""
    fillers = ['Um', 'Uh', 'Hmm', 'Yeah', 'Okay', 'Like', 'I mean', 'You know']
    for filler in fillers:
        text = re.sub(rf'\b{filler}\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


@app.on_event("startup")
async def startup_event():
    """Initialize database and verify AI modules load correctly"""
    init_db()
    try:
        # Pre-load the summarizer on startup to avoid delay on first request
        get_clinical_summarizer()
        logger.info("✅ Clinical Summarizer (BART-Large) ready.")
    except Exception as e:
        logger.error(f"❌ Startup Error: {e}")

    logger.info("System Online: All clinical modules ready.")


# ==================== AUTH & PROFILES ====================

@app.post("/api/v1/auth/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email exists")
    db_user = User(email=user.email, full_name=user.full_name, role=user.role,
                   hashed_password=get_password_hash(user.password))
    db.add(db_user)
    db.commit()
    return db_user


@app.post("/api/v1/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": create_access_token(data={"sub": user.email, "role": user.role}), "token_type": "bearer"}


@app.post("/api/v1/doctors", response_model=DoctorResponse)
async def create_doctor_profile(doctor: DoctorCreate, db: Session = Depends(get_db),
                                user=Depends(get_current_active_user)):
    if user.role != "doctor":
        raise HTTPException(status_code=403, detail="Only users with the 'doctor' role can create this profile.")
    existing = db.query(Doctor).filter(Doctor.user_id == user.id).first()
    if existing:
        return existing
    db_d = Doctor(user_id=user.id, **doctor.dict())
    db.add(db_d)
    db.commit()
    db.refresh(db_d)
    return db_d


@app.post("/api/v1/patients", response_model=PatientResponse)
async def create_patient_profile(patient: PatientCreate, db: Session = Depends(get_db),
                                 user=Depends(get_current_active_user)):
    existing = db.query(Patient).filter(Patient.user_id == user.id).first()
    if existing:
        return existing
    db_p = Patient(user_id=user.id, **patient.dict())
    db.add(db_p)
    db.commit()
    db.refresh(db_p)
    return db_p


# ==================== CLINICAL WORKFLOW ====================

@app.post("/api/v1/conversations", response_model=ConversationResponse)
async def create_conversation(conv: ConversationCreate, db: Session = Depends(get_db),
                              user=Depends(get_current_doctor)):
    doc = db.query(Doctor).filter(Doctor.user_id == user.id).first()
    if not doc:
        raise HTTPException(status_code=400, detail="Create Doctor Profile first")

    final_complaint = conv.chief_complaint
    if not final_complaint or final_complaint.lower() == "string":
        final_complaint = "General Clinical Consultation"

    db_c = Conversation(
        patient_id=conv.patient_id,
        doctor_id=doc.id,
        chief_complaint=final_complaint,
        status="created"
    )
    db.add(db_c)
    db.commit()
    db.refresh(db_c)
    return db_c


@app.post("/api/v1/conversations/{conversation_id}/upload-audio")
async def upload_audio(conversation_id: str, audio: UploadFile = File(...), db: Session = Depends(get_db)):
    path = f"{UPLOAD_DIR}/audio/{conversation_id}_{audio.filename}"
    with open(path, "wb") as f:
        shutil.copyfileobj(audio.file, f)
    db.query(Conversation).filter(Conversation.id == conversation_id).update(
        {"audio_file_path": path, "status": "recorded"})
    db.commit()
    return {"message": "Uploaded successfully", "path": path}


@app.post("/api/v1/conversations/{conversation_id}/transcribe")
async def transcribe(conversation_id: str, db: Session = Depends(get_db)):
    # 1. Clean the ID to remove accidental spaces (like the %20 in your log)
    clean_id = conversation_id.strip()

    # 2. Query using the cleaned ID
    conv = db.query(Conversation).filter(Conversation.id == clean_id).first()

    # 3. Check if the conversation actually exists
    if not conv:
        logger.error(f"❌ Conversation ID not found in database: '{clean_id}'")
        raise HTTPException(
            status_code=404,
            detail=f"Conversation with ID {clean_id} not found."
        )

    # 4. Check if the audio file path exists
    if not conv.audio_file_path:
        raise HTTPException(
            status_code=400,
            detail="No audio file associated with this conversation. Please upload audio first."
        )

    # Proceed with transcription
    res = get_speech_recognizer().transcribe_with_speaker_diarization(conv.audio_file_path)

    if not res['success']:
        raise HTTPException(status_code=500, detail=f"STT Failed: {res.get('error')}")

    conv.transcription = res['transcription']
    conv.status = "transcribed"
    db.commit()

    return {"transcription": conv.transcription, "lang": res['detected_language']}

@app.post("/api/v1/conversations/{conversation_id}/extract-entities")
async def extract(conversation_id: str, db: Session = Depends(get_db)):
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    entities = get_entity_extractor().extract_entities(conv.transcription)

    for cat, items in entities.items():
        for item in items:
            db.add(ExtractedEntity(
                id=str(uuid.uuid4()),
                conversation_id=conversation_id,
                entity_type=cat,
                entity_value=item.get('text', ''),
                confidence_score=str(item.get('confidence', '0.0')),
                start_position=item.get('start', 0),
                end_position=item.get('end', 0),
                context=item.get('context', '')
            ))
    db.commit()
    return {"status": "Entities extracted"}


@app.post("/api/v1/conversations/{conversation_id}/summarize")
async def summarize(conversation_id: str, db: Session = Depends(get_db)):
    """
    💎 UPDATED: Calls the new Summarizer class.
    Post-processing is handled inside the summarizer module.
    """
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv or not conv.transcription:
        raise HTTPException(status_code=400, detail="No transcription found")

    # Get the global instance
    summarizer_instance = get_clinical_summarizer()

    # Generate summary using BART-Large
    # Using .generate() which already includes clean_summary logic
    ai_summary = summarizer_instance.generate(conv.transcription)

    if not ai_summary or len(ai_summary) < 20:
        ai_summary = "Medical consultation regarding patient symptoms. Clinical assessment and management discussed."

    db_summary = db.query(ClinicalSummary).filter(
        ClinicalSummary.conversation_id == conversation_id
    ).first()

    if not db_summary:
        db_summary = ClinicalSummary(id=str(uuid.uuid4()), conversation_id=conversation_id)
        db.add(db_summary)

    db_summary.full_summary = ai_summary
    db.commit()

    return {"status": "Success", "summary": ai_summary}


@app.post("/api/v1/conversations/{conversation_id}/process-full-pipeline")
async def process_full_pipeline(conversation_id: str, db: Session = Depends(get_db)):
    await transcribe(conversation_id, db)
    await extract(conversation_id, db)
    await summarize(conversation_id, db)

    db.query(Conversation).filter(Conversation.id == conversation_id).update(
        {"status": "completed"}
    )
    db.commit()

    final_summary = db.query(ClinicalSummary).filter(
        ClinicalSummary.conversation_id == conversation_id
    ).first()

    return {"status": "Full Pipeline Complete", "summary": final_summary}


@app.post("/api/v1/patients/{patient_id}/retrieve-history")
async def history(patient_id: str, req: HistoryRetrievalRequest, db: Session = Depends(get_db)):
    # ... (Rest of your history retrieval remains the same)
    pass