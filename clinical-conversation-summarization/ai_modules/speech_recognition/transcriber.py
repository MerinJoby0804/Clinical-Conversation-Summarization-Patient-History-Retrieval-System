import os
import whisper
from typing import Optional
from loguru import logger


class SpeechRecognizer:
    """
    Speech-to-text conversion using OpenAI Whisper (Multilingual)
    """

    def __init__(self, model_name: str = "base"):
        """
        Initialize Whisper model.
        Model options: 'tiny', 'base', 'small', 'medium', 'large'
        'base' is ideal for a B.Tech project—fast and multilingual.
        """
        # Whisper automatically downloads the model to ~/.cache/whisper
        # No more manual file path errors!
        logger.info(f"Loading Whisper model: {model_name}")
        try:
            self.model = whisper.load_model(model_name)
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {str(e)}")
            raise

    def transcribe_audio(self, audio_file_path: str) -> dict:
        """
        Transcribe audio file to text using Whisper.
        Whisper handles format conversion internally.
        """
        try:
            if not os.path.exists(audio_file_path):
                raise FileNotFoundError(f"Audio file not found at {audio_file_path}")

            logger.info(f"Starting Whisper transcription for: {audio_file_path}")

            # Whisper detects the language automatically
            # fp16=False is used to ensure it runs smoothly on CPU/Standard laptops
            result = self.model.transcribe(audio_file_path, fp16=False)

            full_text = result.get("text", "").strip()
            detected_lang = result.get("language", "unknown")

            logger.info(f"Transcription completed. Language detected: {detected_lang}")

            return {
                'transcription': full_text,
                'detected_language': detected_lang,
                'segments': result.get("segments", []),
                'audio_file': audio_file_path,
                'success': True
            }

        except Exception as e:
            logger.error(f"Error during Whisper transcription: {str(e)}")
            return {
                'transcription': '',
                'detected_language': '',
                'audio_file': audio_file_path,
                'success': False,
                'error': str(e)
            }

    def transcribe_with_speaker_diarization(self, audio_file_path: str) -> dict:
        """
        Transcribe with speaker segments.
        Whisper provides segments by default, which we can map to Doctor/Patient.
        """
        result = self.transcribe_audio(audio_file_path)

        if not result['success']:
            return result

        # We can format Whisper's native segments to match your previous structure
        formatted_segments = []
        for i, seg in enumerate(result['segments']):
            formatted_segments.append({
                'speaker': "Doctor" if i % 2 == 0 else "Patient",  # Simplified turn-taking
                'text': seg['text'].strip(),
                'start': seg['start'],
                'end': seg['end']
            })

        result['segments'] = formatted_segments
        return result


# Convenience function for main.py
def transcribe_clinical_audio(audio_file_path: str) -> dict:
    """
    Quick function to transcribe clinical audio using Whisper
    """
    recognizer = SpeechRecognizer()
    return recognizer.transcribe_with_speaker_diarization(audio_file_path)