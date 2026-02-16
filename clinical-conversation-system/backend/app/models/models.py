from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()


def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    """Base user model for authentication"""
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, nullable=False)  # 'doctor' or 'patient'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    doctor_profile = relationship("Doctor", back_populates="user", uselist=False)
    patient_profile = relationship("Patient", back_populates="user", uselist=False)


class Doctor(Base):
    """Doctor profile"""
    __tablename__ = "doctors"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False)
    license_number = Column(String, unique=True, nullable=False)
    specialization = Column(String)
    department = Column(String)
    phone = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="doctor_profile")
    conversations = relationship("Conversation", back_populates="doctor")


class Patient(Base):
    """Patient profile"""
    __tablename__ = "patients"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False)

    # CHANGED: nullable=True allows your simplified schema to work without manual ID input
    patient_id = Column(String, unique=True, nullable=True)

    date_of_birth = Column(DateTime)
    gender = Column(String)
    blood_group = Column(String)
    phone = Column(String)
    address = Column(Text)
    emergency_contact = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="patient_profile")
    conversations = relationship("Conversation", back_populates="patient")
    medical_history = relationship("MedicalHistory", back_populates="patient")


class Conversation(Base):
    """Stores doctor-patient conversation records"""
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=generate_uuid)
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(String, ForeignKey("doctors.id"), nullable=False)
    conversation_date = Column(DateTime, default=datetime.utcnow)
    audio_file_path = Column(String)
    transcription = Column(Text)
    chief_complaint = Column(String)
    status = Column(String, default="recorded")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    patient = relationship("Patient", back_populates="conversations")
    doctor = relationship("Doctor", back_populates="conversations")
    extracted_entities = relationship("ExtractedEntity", back_populates="conversation")
    clinical_summary = relationship("ClinicalSummary", back_populates="conversation", uselist=False)


class ExtractedEntity(Base):
    """Stores clinical entities extracted from conversations"""
    __tablename__ = "extracted_entities"

    id = Column(String, primary_key=True, default=generate_uuid)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    entity_type = Column(String, nullable=False)
    entity_value = Column(String, nullable=False)
    context = Column(Text)
    confidence_score = Column(String)
    start_position = Column(Integer)
    end_position = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="extracted_entities")


class ClinicalSummary(Base):
    """Stores AI-generated clinical summaries"""
    __tablename__ = "clinical_summaries"

    id = Column(String, primary_key=True, default=generate_uuid)
    conversation_id = Column(String, ForeignKey("conversations.id"), unique=True, nullable=False)
    subjective = Column(Text)
    objective = Column(Text)
    assessment = Column(Text)
    plan = Column(Text)
    full_summary = Column(Text)
    keywords = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="clinical_summary")


class MedicalHistory(Base):
    """Stores patient's medical history"""
    __tablename__ = "medical_history"

    id = Column(String, primary_key=True, default=generate_uuid)
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False)
    category = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    date_recorded = Column(DateTime)
    is_active = Column(Boolean, default=True)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    patient = relationship("Patient", back_populates="medical_history")


class VitalSigns(Base):
    """Stores patient vital signs over time"""
    __tablename__ = "vital_signs"

    id = Column(String, primary_key=True, default=generate_uuid)
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False)
    conversation_id = Column(String, ForeignKey("conversations.id"))
    blood_pressure_systolic = Column(Integer)
    blood_pressure_diastolic = Column(Integer)
    heart_rate = Column(Integer)
    temperature = Column(String)
    respiratory_rate = Column(Integer)
    oxygen_saturation = Column(Integer)
    weight = Column(String)
    height = Column(String)
    recorded_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient")
    conversation = relationship("Conversation")