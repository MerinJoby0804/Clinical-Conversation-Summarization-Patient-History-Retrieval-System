from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    pipeline
)
import torch
from typing import Dict, Optional, List
from loguru import logger
import os


class ClinicalSummarizer:
    """
    Generate clinical summaries using transformer models
    """

    def __init__(
            self,
            model_name: str = "facebook/bart-large-cnn",
            device: Optional[str] = None
    ):
        """
        Initialize summarizer

        Args:
            model_name: HuggingFace model name
            device: Device to use ('cuda' or 'cpu')
        """
        self.model_name = model_name

        # Set device
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        logger.info(f"Loading summarization model: {model_name}")
        logger.info(f"Using device: {self.device}")

        # Load model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        self.model.to(self.device)

        # Create pipeline
        self.summarizer = pipeline(
            "summarization",
            model=self.model,
            tokenizer=self.tokenizer,
            device=0 if self.device == "cuda" else -1
        )

        logger.info("Summarization model loaded successfully")

    def summarize_conversation(
            self,
            text: str,
            max_length: int = 200,
            min_length: int = 50,
            do_sample: bool = False
    ) -> str:
        """
        Generate summary of clinical conversation

        Args:
            text: Clinical conversation text
            max_length: Maximum summary length
            min_length: Minimum summary length
            do_sample: Whether to use sampling

        Returns:
            Generated summary
        """
        try:
            # Check input length
            tokens = self.tokenizer.encode(text, truncation=True, max_length=1024)

            if len(tokens) < 10:
                logger.warning("Input text too short for meaningful summarization")
                return text

            # Generate summary
            summary = self.summarizer(
                text,
                max_length=max_length,
                min_length=min_length,
                do_sample=do_sample,
                truncation=True
            )

            summary_text = summary[0]['summary_text']
            logger.info(f"Generated summary of {len(summary_text)} characters")

            return summary_text

        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return ""

    def generate_soap_summary(
            self,
            conversation: str,
            entities: Optional[Dict] = None
    ) -> Dict[str, str]:
        """
        Generate SOAP-formatted clinical summary

        Args:
            conversation: Full conversation text
            entities: Pre-extracted entities (optional)

        Returns:
            Dictionary with SOAP components
        """
        soap = {
            'subjective': '',
            'objective': '',
            'assessment': '',
            'plan': ''
        }

        # Split conversation into sections if available
        sections = self._split_conversation_sections(conversation)

        # Generate each SOAP component
        if 'patient_symptoms' in sections:
            soap['subjective'] = self.summarize_conversation(
                sections['patient_symptoms'],
                max_length=150,
                min_length=30
            )

        if 'examination' in sections:
            soap['objective'] = self.summarize_conversation(
                sections['examination'],
                max_length=150,
                min_length=30
            )

        if 'diagnosis' in sections:
            soap['assessment'] = self.summarize_conversation(
                sections['diagnosis'],
                max_length=100,
                min_length=20
            )

        if 'treatment_plan' in sections:
            soap['plan'] = self.summarize_conversation(
                sections['treatment_plan'],
                max_length=150,
                min_length=30
            )

        # If no sections identified, generate from full text
        if not any(soap.values()):
            full_summary = self.summarize_conversation(conversation)
            soap['subjective'] = full_summary

        return soap

    def _split_conversation_sections(self, conversation: str) -> Dict[str, str]:
        """
        Split conversation into clinical sections

        Args:
            conversation: Full conversation text

        Returns:
            Dictionary of sections
        """
        sections = {}

        # Keywords for different sections
        symptom_keywords = ['complaint', 'symptoms', 'feel', 'pain', 'problem']
        exam_keywords = ['examination', 'vital', 'check', 'blood pressure', 'temperature']
        diagnosis_keywords = ['diagnosis', 'condition', 'looks like', 'seems to be']
        plan_keywords = ['prescribe', 'treatment', 'medication', 'follow-up', 'recommend']

        lines = conversation.split('\n')
        current_section = None
        section_content = {
            'patient_symptoms': [],
            'examination': [],
            'diagnosis': [],
            'treatment_plan': []
        }

        for line in lines:
            line_lower = line.lower()

            # Detect section based on keywords
            if any(kw in line_lower for kw in symptom_keywords):
                current_section = 'patient_symptoms'
            elif any(kw in line_lower for kw in exam_keywords):
                current_section = 'examination'
            elif any(kw in line_lower for kw in diagnosis_keywords):
                current_section = 'diagnosis'
            elif any(kw in line_lower for kw in plan_keywords):
                current_section = 'treatment_plan'

            # Add to current section
            if current_section and line.strip():
                section_content[current_section].append(line)

        # Join sections
        for section, lines in section_content.items():
            if lines:
                sections[section] = '\n'.join(lines)

        return sections

    def generate_patient_history_summary(
            self,
            conversations: List[Dict],
            symptom_focus: Optional[List[str]] = None
    ) -> str:
        """
        Generate summary of patient's historical conversations
        Focused on specific symptoms if provided

        Args:
            conversations: List of conversation dictionaries
            symptom_focus: List of symptoms to focus on (optional)

        Returns:
            Summary of patient history
        """
        if not conversations:
            return "No previous medical history available."

        # Combine relevant conversations
        combined_text = ""
        for conv in conversations:
            if symptom_focus:
                # Filter for relevant conversations
                conv_text = conv.get('transcription', '') + ' ' + conv.get('summary', '')
                if any(symptom.lower() in conv_text.lower() for symptom in symptom_focus):
                    combined_text += f"\n\nVisit on {conv.get('date', 'Unknown')}:\n{conv_text}"
            else:
                combined_text += f"\n\nVisit on {conv.get('date', 'Unknown')}:\n"
                combined_text += conv.get('summary', conv.get('transcription', ''))

        if not combined_text.strip():
            return "No relevant medical history found for the specified symptoms."

        # Generate summary
        history_summary = self.summarize_conversation(
            combined_text,
            max_length=300,
            min_length=100
        )

        return history_summary

    def extract_key_points(
            self,
            text: str,
            num_points: int = 5
    ) -> List[str]:
        """
        Extract key points from clinical text

        Args:
            text: Clinical text
            num_points: Number of key points to extract

        Returns:
            List of key points
        """
        # Split into sentences
        sentences = [s.strip() for s in text.split('.') if s.strip()]

        # Score sentences by medical relevance (simple heuristic)
        medical_keywords = [
            'diagnosis', 'symptoms', 'treatment', 'medication', 'procedure',
            'pain', 'fever', 'pressure', 'test', 'result'
        ]

        scored_sentences = []
        for sent in sentences:
            score = sum(1 for kw in medical_keywords if kw in sent.lower())
            if score > 0:
                scored_sentences.append((score, sent))

        # Sort by score and return top N
        scored_sentences.sort(reverse=True, key=lambda x: x[0])
        key_points = [sent for _, sent in scored_sentences[:num_points]]

        return key_points


class SymptomConditionedSummarizer(ClinicalSummarizer):
    """
    Extended summarizer that generates symptom-focused summaries
    for patient history retrieval
    """

    def generate_symptom_focused_summary(
            self,
            patient_history: str,
            current_symptoms: List[str],
            max_length: int = 250
    ) -> str:
        """
        Generate summary focused on specific symptoms

        Args:
            patient_history: Patient's medical history
            current_symptoms: Current symptoms to focus on
            max_length: Maximum summary length

        Returns:
            Symptom-focused summary
        """
        # Create symptom-focused prompt
        symptom_list = ', '.join(current_symptoms)
        focused_text = f"Patient presenting with {symptom_list}. "
        focused_text += f"Relevant medical history: {patient_history}"

        # Generate summary
        summary = self.summarize_conversation(
            focused_text,
            max_length=max_length,
            min_length=50
        )

        return summary


# Convenience functions
def summarize_clinical_conversation(text: str) -> str:
    """
    Quick function to summarize clinical conversation

    Args:
        text: Clinical conversation text

    Returns:
        Generated summary
    """
    summarizer = ClinicalSummarizer()
    return summarizer.summarize_conversation(text)


def generate_soap_summary(text: str) -> Dict[str, str]:
    """
    Quick function to generate SOAP summary

    Args:
        text: Clinical conversation text

    Returns:
        SOAP-formatted summary
    """
    summarizer = ClinicalSummarizer()
    return summarizer.generate_soap_summary(text)