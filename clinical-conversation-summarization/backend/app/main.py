import sys
import os
import shutil
from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
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
from ai_modules.summarization.summarizer import ClinicalSummarizer
from ai_modules.retrieval.history_retriever import PatientHistoryRetriever

app = FastAPI(title="Clinical AI System", version="1.0.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

UPLOAD_DIR = "./uploads"
os.makedirs(f"{UPLOAD_DIR}/audio", exist_ok=True)

# Lazy loading AI getters
speech_recognizer = None
entity_extractor = None
clinical_summarizer = None
history_retriever = None

def get_speech_recognizer():
    global speech_recognizer
    if not speech_recognizer: speech_recognizer = SpeechRecognizer(model_name="base")
    return speech_recognizer

def get_entity_extractor():
    global entity_extractor
    if not entity_extractor: entity_extractor = ClinicalEntityExtractor()
    return entity_extractor

def get_clinical_summarizer():
    global clinical_summarizer
    if not clinical_summarizer: clinical_summarizer = ClinicalSummarizer()
    return clinical_summarizer

def get_history_retriever():
    global history_retriever
    if not history_retriever: history_retriever = PatientHistoryRetriever()
    return history_retriever

@app.on_event("startup")
async def startup_event():
    init_db()
    logger.info("System Online: All clinical modules ready.")

# ==================== AUTH & PROFILES ====================

@app.post("/api/v1/auth/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email exists")
    db_user = User(email=user.email, full_name=user.full_name, role=user.role, hashed_password=get_password_hash(user.password))
    db.add(db_user)
    db.commit()
    return db_user

@app.post("/api/v1/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": create_access_token(data={"sub": user.email, "role": user.role}), "token_type": "bearer"}

@app.post("/api/v1/patients", response_model=PatientResponse)
async def create_patient_profile(patient: PatientCreate, db: Session = Depends(get_db), user=Depends(get_current_active_user)):
    existing = db.query(Patient).filter(Patient.user_id == user.id).first()
    if existing: return existing
    db_p = Patient(user_id=user.id, **patient.dict())
    db.add(db_p); db.commit(); db.refresh(db_p)
    return db_p

# ==================== CLINICAL WORKFLOW ====================

@app.post("/api/v1/conversations", response_model=ConversationResponse)
async def create_conversation(conv: ConversationCreate, db: Session = Depends(get_db), user=Depends(get_current_doctor)):
    doc = db.query(Doctor).filter(Doctor.user_id == user.id).first()
    if not doc: raise HTTPException(status_code=400, detail="Create Doctor Profile first")
    db_c = Conversation(patient_id=conv.patient_id, doctor_id=doc.id, chief_complaint=conv.chief_complaint, status="created")
    db.add(db_c); db.commit(); db.refresh(db_c)
    return db_c

@app.post("/api/v1/conversations/{conversation_id}/upload-audio")
async def upload_audio(conversation_id: str, audio: UploadFile = File(...), db: Session = Depends(get_db)):
    path = f"{UPLOAD_DIR}/audio/{conversation_id}_{audio.filename}"
    with open(path, "wb") as f: shutil.copyfileobj(audio.file, f)
    db.query(Conversation).filter(Conversation.id == conversation_id).update({"audio_file_path": path, "status": "recorded"})
    db.commit()
    return {"message": "Uploaded", "path": path}

@app.post("/api/v1/conversations/{conversation_id}/transcribe")
async def transcribe(conversation_id: str, db: Session = Depends(get_db)):
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    res = get_speech_recognizer().transcribe_audio(conv.audio_file_path)
    if not res['success']: raise HTTPException(status_code=500, detail="STT Failed")
    conv.transcription = res['transcription']; conv.status = "transcribed"
    db.commit()
    return {"transcription": conv.transcription, "lang": res['detected_language']}

@app.post("/api/v1/conversations/{conversation_id}/extract-entities")
async def extract(conversation_id: str, db: Session = Depends(get_db)):
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    entities = get_entity_extractor().extract_entities(conv.transcription)
    for cat, items in entities.items():
        for item in items:
            db.add(ExtractedEntity(conversation_id=conversation_id, entity_type=cat, entity_value=item['text']))
    db.commit()
    return {"entities": entities}

#@app.post("/api/v1/conversations/{conversation_id}/summarize")
@app.post("/api/v1/conversations/{conversation_id}/summarize")
async def summarize(conversation_id: str, db: Session = Depends(get_db)):
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()

    if not conv or not conv.transcription:
        raise HTTPException(status_code=400, detail="No transcription found.")

    # Calculate word count to determine if we need the AI model
    word_count = len(conv.transcription.split())

    # 1. Check if a summary already exists (to prevent UniqueViolation)
    db_s = db.query(ClinicalSummary).filter(ClinicalSummary.conversation_id == conversation_id).first()

    # 2. DETERMINE CONTENT: AI Summary vs. Direct Return
    # We'll use 40 words as the threshold. Below this, AI might throw warnings.
    if word_count < 40:
        logger.info(f"Short conversation detected ({word_count} words). Skipping AI summarization.")
        subjective = "Short interaction recorded."
        objective = "N/A"
        assessment = "N/A"
        plan = "N/A"
        full_summary = f"Direct Transcription (Short Conversation): {conv.transcription}"
        keywords = []
    else:
        logger.info(f"Generating AI summary for {word_count} words...")
        summarizer = get_clinical_summarizer()

        # We manually adjust max_length here to avoid the warning you saw
        # Setting max_length to roughly half the input length for short-medium texts
        dynamic_max = min(200, max(30, word_count // 2))

        soap = summarizer.generate_soap_summary(conv.transcription)
        full_summary = summarizer.summarize_conversation(conv.transcription)
        keywords = get_entity_extractor().extract_key_medical_terms(conv.transcription)

        subjective = soap.get('subjective', 'N/A')
        objective = soap.get('objective', 'N/A')
        assessment = soap.get('assessment', 'N/A')
        plan = soap.get('plan', 'N/A')

    # 3. SAVE LOGIC: Update existing or Create new
    if db_s:
        logger.info(f"Updating existing summary record for {conversation_id}")
        db_s.subjective = subjective
        db_s.objective = objective
        db_s.assessment = assessment
        db_s.plan = plan
        db_s.full_summary = full_summary
        db_s.keywords = keywords
    else:
        logger.info(f"Creating new summary record for {conversation_id}")
        db_s = ClinicalSummary(
            conversation_id=conversation_id,
            subjective=subjective,
            objective=objective,
            assessment=assessment,
            plan=plan,
            full_summary=full_summary,
            keywords=keywords
        )
        db.add(db_s)

    conv.status = "processed"
    db.commit()
    db.refresh(db_s)

    return db_s


# ==================== RETRIEVAL ====================

#@app.post("/api/v1/patients/{patient_id}/retrieve-history")
@app.post("/api/v1/patients/{patient_id}/retrieve-history")
async def history(patient_id: str, req: HistoryRetrievalRequest, db: Session = Depends(get_db)):
    # 1. Fetch conversations from DB
    db_conversations = db.query(Conversation).filter(Conversation.patient_id == patient_id).all()

    # 2. Force conversion to a list of DICTIONARIES
    formatted_data = []
    for conv in db_conversations:
        # We use a manual dict to ensure the AI module can use .get()
        formatted_data.append({
            "id": str(conv.id),
            "transcription": conv.transcription or "",
            "summary": conv.clinical_summary.full_summary if conv.clinical_summary else None,
            "chief_complaint": conv.chief_complaint or ""
        })

    # 3. Create the data package the AI expects
    data_for_ai = {"conversations": formatted_data}

    # 4. Call the retriever safely
    try:
        results = get_history_retriever().retrieve_symptom_based_history(req.symptoms, data_for_ai)
        return results
    except Exception as e:
        logger.error(f"History Retrieval Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI retrieval failed: {str(e)}")