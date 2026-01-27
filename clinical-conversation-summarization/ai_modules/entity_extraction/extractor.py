import spacy
from typing import List, Dict, Tuple
from loguru import logger
import re


class ClinicalEntityExtractor:
    """
    Extract clinical entities from medical text using scispaCy
    """

    def __init__(self, model_name: str = "en_core_sci_sm"):
        """
        Initialize entity extractor

        Args:
            model_name: spaCy model name (default: en_core_sci_sm)
        """
        try:
            logger.info(f"Loading spaCy model: {model_name}")
            self.nlp = spacy.load(model_name)
            logger.info("spaCy model loaded successfully")
        except OSError:
            logger.error(f"Model {model_name} not found. Installing...")
            import subprocess
            subprocess.run([
                "pip", "install",
                "https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.3/en_core_sci_sm-0.5.3.tar.gz"
            ])
            self.nlp = spacy.load(model_name)

        # Define clinical entity patterns
        self.entity_patterns = self._create_entity_patterns()

    def _create_entity_patterns(self) -> Dict[str, List[str]]:
        """Create patterns for different clinical entities"""
        return {
            'vital_signs': [
                r'blood pressure.*?(\d+/\d+)',
                r'bp.*?(\d+/\d+)',
                r'heart rate.*?(\d+)',
                r'pulse.*?(\d+)',
                r'temperature.*?(\d+\.?\d*)',
                r'temp.*?(\d+\.?\d*)',
                r'respiratory rate.*?(\d+)',
                r'spo2.*?(\d+)',
                r'oxygen saturation.*?(\d+)',
            ],
            'medications': [
                r'(aspirin|ibuprofen|paracetamol|metformin|lisinopril|atorvastatin|amlodipine)',
                r'(\w+cillin)',  # Antibiotics
                r'(\w+pril)',  # ACE inhibitors
                r'(\w+statin)',  # Statins
            ],
            'symptoms': [
                r'(pain|ache|fever|cough|nausea|vomiting|dizziness|fatigue|weakness)',
                r'(headache|backache|stomachache)',
                r'(shortness of breath|difficulty breathing)',
            ],
            'temporal': [
                r'(\d+\s+(?:days?|weeks?|months?|years?)\s+ago)',
                r'(since\s+\d+)',
                r'(for\s+\d+\s+(?:days?|weeks?|months?|years?))',
                r'(yesterday|today|last\s+\w+)',
            ]
        }

    def extract_entities(self, text: str) -> Dict[str, List[Dict]]:
        """
        Extract all clinical entities from text

        Args:
            text: Input clinical text

        Returns:
            Dictionary of entity types and their values
        """
        doc = self.nlp(text)

        entities = {
            'diseases': [],
            'symptoms': [],
            'medications': [],
            'procedures': [],
            'anatomy': [],
            'vital_signs': [],
            'temporal': [],
            'general_entities': []
        }

        # Extract using spaCy NER
        for ent in doc.ents:
            entity_info = {
                'text': ent.text,
                'label': ent.label_,
                'start': ent.start_char,
                'end': ent.end_char,
                'context': self._get_context(text, ent.start_char, ent.end_char)
            }

            # Categorize entities
            if ent.label_ in ['DISEASE', 'DISORDER']:
                entities['diseases'].append(entity_info)
            elif ent.label_ in ['SYMPTOM', 'SIGN']:
                entities['symptoms'].append(entity_info)
            elif ent.label_ in ['MEDICATION', 'DRUG', 'CHEMICAL']:
                entities['medications'].append(entity_info)
            elif ent.label_ in ['PROCEDURE', 'TREATMENT']:
                entities['procedures'].append(entity_info)
            elif ent.label_ in ['ANATOMY', 'BODY_PART']:
                entities['anatomy'].append(entity_info)
            else:
                entities['general_entities'].append(entity_info)

        # Extract using regex patterns
        entities.update(self._extract_with_patterns(text))

        # Remove duplicates
        for category in entities:
            entities[category] = self._remove_duplicate_entities(entities[category])

        logger.info(f"Extracted {sum(len(v) for v in entities.values())} entities")

        return entities

    def _extract_with_patterns(self, text: str) -> Dict[str, List[Dict]]:
        """Extract entities using regex patterns"""
        pattern_entities = {
            'vital_signs': [],
            'temporal': []
        }

        for category, patterns in self.entity_patterns.items():
            if category not in pattern_entities:
                pattern_entities[category] = []

            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    entity_info = {
                        'text': match.group(0),
                        'label': category.upper(),
                        'start': match.start(),
                        'end': match.end(),
                        'context': self._get_context(text, match.start(), match.end())
                    }
                    pattern_entities[category].append(entity_info)

        return pattern_entities

    def _get_context(self, text: str, start: int, end: int, window: int = 50) -> str:
        """Get surrounding context for an entity"""
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        return text[context_start:context_end]

    def _remove_duplicate_entities(self, entities: List[Dict]) -> List[Dict]:
        """Remove duplicate entities based on text and position"""
        seen = set()
        unique_entities = []

        for entity in entities:
            key = (entity['text'].lower(), entity['start'], entity['end'])
            if key not in seen:
                seen.add(key)
                unique_entities.append(entity)

        return unique_entities

    def extract_soap_components(self, text: str) -> Dict[str, str]:
        """
        Extract SOAP (Subjective, Objective, Assessment, Plan) components

        Args:
            text: Clinical conversation text

        Returns:
            Dictionary with SOAP components
        """
        soap = {
            'subjective': '',
            'objective': '',
            'assessment': '',
            'plan': ''
        }

        # Simple keyword-based extraction
        # In production, use more sophisticated NLP

        lines = text.split('\n')
        current_section = None

        for line in lines:
            line_lower = line.lower()

            # Detect section headers
            if 'subjective' in line_lower or 'chief complaint' in line_lower:
                current_section = 'subjective'
                continue
            elif 'objective' in line_lower or 'examination' in line_lower:
                current_section = 'objective'
                continue
            elif 'assessment' in line_lower or 'diagnosis' in line_lower:
                current_section = 'assessment'
                continue
            elif 'plan' in line_lower or 'treatment' in line_lower:
                current_section = 'plan'
                continue

            # Add content to current section
            if current_section and line.strip():
                soap[current_section] += line + '\n'

        # If no explicit SOAP structure, infer from content
        if not any(soap.values()):
            entities = self.extract_entities(text)

            # Subjective: symptoms and patient statements
            if entities['symptoms']:
                soap['subjective'] = 'Patient reports: ' + ', '.join(
                    [e['text'] for e in entities['symptoms'][:5]]
                )

            # Objective: vital signs and examination findings
            if entities['vital_signs']:
                soap['objective'] = 'Vitals: ' + ', '.join(
                    [e['text'] for e in entities['vital_signs']]
                )

            # Assessment: diseases and diagnoses
            if entities['diseases']:
                soap['assessment'] = 'Diagnosis: ' + ', '.join(
                    [e['text'] for e in entities['diseases'][:3]]
                )

            # Plan: medications and procedures
            plan_items = []
            if entities['medications']:
                plan_items.extend([e['text'] for e in entities['medications'][:3]])
            if entities['procedures']:
                plan_items.extend([e['text'] for e in entities['procedures'][:3]])

            if plan_items:
                soap['plan'] = 'Treatment: ' + ', '.join(plan_items)

        return soap

    def extract_key_medical_terms(self, text: str, top_n: int = 10) -> List[str]:
        """
        Extract key medical terms for indexing and retrieval

        Args:
            text: Clinical text
            top_n: Number of top terms to return

        Returns:
            List of key medical terms
        """
        entities = self.extract_entities(text)

        # Collect all medical terms
        terms = []
        for category in ['diseases', 'symptoms', 'medications', 'procedures']:
            terms.extend([e['text'] for e in entities.get(category, [])])

        # Remove duplicates and return top N
        unique_terms = list(dict.fromkeys(terms))
        return unique_terms[:top_n]


# Convenience function
def extract_clinical_entities(text: str) -> Dict:
    """
    Quick function to extract clinical entities

    Args:
        text: Clinical text

    Returns:
        Dictionary of extracted entities
    """
    extractor = ClinicalEntityExtractor()
    return extractor.extract_entities(text)