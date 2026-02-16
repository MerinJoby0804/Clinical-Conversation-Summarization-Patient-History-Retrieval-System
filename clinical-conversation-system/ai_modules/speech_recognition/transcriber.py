import os
import whisper
from loguru import logger


class SpeechRecognizer:
    def __init__(self, model_name: str = "base"):
        logger.info(f"🎙️ Loading Whisper model: {model_name}")
        try:
            self.model = whisper.load_model(model_name)
            logger.info("✅ Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load Whisper model: {e}")
            raise

    def transcribe_audio(self, audio_file_path: str) -> dict:
        """Base transcription logic."""
        try:
            if not os.path.exists(audio_file_path):
                raise FileNotFoundError(f"File not found: {audio_file_path}")

            # fp16=False for stability on laptops
            result = self.model.transcribe(audio_file_path, fp16=False)
            return {
                'success': True,
                'text': result.get("text", "").strip(),
                'segments': result.get("segments", []),
                'language': result.get("language", "en")
            }
        except Exception as e:
            logger.error(f"Transcription Error: {e}")
            return {'success': False, 'error': str(e)}

    def transcribe_with_speaker_diarization(self, audio_file_path: str) -> dict:
        """
        🔧 FIXED: This method must exist to stop the AttributeError.
        Includes Smart Speaker Switching logic.
        """
        result = self.transcribe_audio(audio_file_path)
        if not result['success']:
            return result

        labeled_lines = []
        current_speaker = "Doctor"  # Initial assumption

        for seg in result['segments']:
            text = seg['text'].strip()
            if not text: continue

            # Logic: First person to talk is Doctor.
            # If Doctor asks a question (?), switch to Patient.
            # If Patient ends a statement (.), switch back to Doctor.
            labeled_lines.append(f"{current_speaker}: {text}")

            if "?" in text and current_speaker == "Doctor":
                current_speaker = "Patient"
            elif text.endswith((".", "!")) and current_speaker == "Patient":
                current_speaker = "Doctor"

        # Update the result with the properly labeled transcript
        return {
            'success': True,
            'transcription': "\n".join(labeled_lines),
            'detected_language': result['language']
        }