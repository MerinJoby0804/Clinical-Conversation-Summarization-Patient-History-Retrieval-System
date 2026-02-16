import torch
import re
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from loguru import logger


class Summarizer:
    def __init__(self, model_name: str = "facebook/bart-large-cnn"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"🚀 Initializing {model_name} on {self.device}...")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(self.device)
            logger.info("✅ Summarizer ready!")
        except Exception as e:
            logger.error(f"❌ Load Error: {e}")
            raise

    def clean_output(self, text: str) -> str:
        """
        Scrub out 'Doctor:', 'Patient:', and weird artifacts like 'ipient'.
        """
        # 1. Remove Speaker Labels
        text = re.sub(r'(Doctor|Patient|ipient|Recipient|Speaker \d+):', '', text, flags=re.IGNORECASE)

        # 2. Fix the 'ipientPatient' artifact
        text = text.replace("ipientPatient", "The patient")
        text = text.replace("ipient", "")

        # 3. Clean up extra spaces
        text = re.sub(r'\s+', ' ', text).strip()

        # 4. Ensure it starts with a capital and ends with a period
        if text:
            text = text[0].upper() + text[1:]
            if not text.endswith('.'):
                text += "."

        return text

    def generate(self, text: str) -> str:
        try:
            if not text or len(text.strip()) < 30:
                return "Insufficient data for summary."

            # Use the 'summarize' task prefix BART was trained on
            input_text = "summarize: " + text

            inputs = self.tokenizer(
                input_text,
                return_tensors="pt",
                truncation=True,
                max_length=1024
            ).to(self.device)

            output_ids = self.model.generate(
                input_ids=inputs.input_ids,
                max_new_tokens=150,
                min_new_tokens=40,
                num_beams=4,
                repetition_penalty=1.2,
                no_repeat_ngram_size=3,
                early_stopping=True
            )

            raw_summary = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)

            # Apply the cleaning layer
            return self.clean_output(raw_summary)

        except Exception as e:
            logger.error(f"Inference Error: {e}")
            return "Error generating clinical summary."