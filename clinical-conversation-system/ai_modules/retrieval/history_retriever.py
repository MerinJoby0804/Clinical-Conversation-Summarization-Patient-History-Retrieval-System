from sentence_transformers import SentenceTransformer, util
import torch
from typing import List, Dict, Tuple
from loguru import logger
import numpy as np


class PatientHistoryRetriever:
    """
    Retrieve relevant patient history based on current symptoms
    using semantic similarity
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize retriever with sentence transformer

        Args:
            model_name: SentenceTransformer model name
        """
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        logger.info(f"Embedding model loaded on {self.device}")

    def encode_texts(self, texts: List[str]) -> np.ndarray:
        """
        Encode texts into embeddings

        Args:
            texts: List of text strings

        Returns:
            Numpy array of embeddings
        """
        embeddings = self.model.encode(
            texts,
            convert_to_tensor=True,
            show_progress_bar=False
        )
        return embeddings.cpu().numpy()

    def find_relevant_conversations(
            self,
            query_symptoms: List[str],
            conversation_history: List[Dict],
            top_k: int = 5
    ) -> List[Tuple[Dict, float]]:
        """
        Find most relevant past conversations based on symptoms

        Args:
            query_symptoms: Current symptoms
            conversation_history: List of past conversations
            top_k: Number of top results to return

        Returns:
            List of (conversation, similarity_score) tuples
        """
        if not conversation_history:
            return []

        # Create query from symptoms
        query = "Patient has: " + ", ".join(query_symptoms)

        # Prepare conversation texts
        conv_texts = []
        for conv in conversation_history:
            # Combine summary and key entities for better matching
            text = ""
            if conv.get('summary'):
                text += conv['summary'] + " "
            if conv.get('transcription'):
                text += conv['transcription'][:500]  # Limit length
            if conv.get('chief_complaint'):
                text += " Chief complaint: " + conv['chief_complaint']

            conv_texts.append(text if text else "No content")

        # Encode query and conversations
        query_embedding = self.encode_texts([query])
        conv_embeddings = self.encode_texts(conv_texts)

        # Calculate similarities
        similarities = util.cos_sim(query_embedding, conv_embeddings)[0]

        # Get top K
        top_indices = torch.topk(similarities, min(top_k, len(similarities))).indices

        results = []
        for idx in top_indices:
            idx = idx.item()
            results.append((
                conversation_history[idx],
                similarities[idx].item()
            ))

        logger.info(f"Found {len(results)} relevant conversations")
        return results

    def find_relevant_entities(
            self,
            query_symptoms: List[str],
            entity_history: List[Dict],
            entity_types: List[str] = None,
            top_k: int = 10
    ) -> List[Tuple[Dict, float]]:
        """
        Find relevant clinical entities from history

        Args:
            query_symptoms: Current symptoms
            entity_history: List of extracted entities
            entity_types: Filter by entity types (e.g., ['medication', 'diagnosis'])
            top_k: Number of results

        Returns:
            List of (entity, similarity_score) tuples
        """
        if not entity_history:
            return []

        # Filter by entity type if specified
        if entity_types:
            filtered_entities = [
                e for e in entity_history
                if e.get('entity_type', '').lower() in [t.lower() for t in entity_types]
            ]
        else:
            filtered_entities = entity_history

        if not filtered_entities:
            return []

        # Create query
        query = " ".join(query_symptoms)

        # Prepare entity texts
        entity_texts = [
            f"{e.get('entity_type', '')}: {e.get('entity_value', '')} {e.get('context', '')}"
            for e in filtered_entities
        ]

        # Encode and find similarities
        query_embedding = self.encode_texts([query])
        entity_embeddings = self.encode_texts(entity_texts)

        similarities = util.cos_sim(query_embedding, entity_embeddings)[0]
        top_indices = torch.topk(similarities, min(top_k, len(similarities))).indices

        results = []
        for idx in top_indices:
            idx = idx.item()
            results.append((
                filtered_entities[idx],
                similarities[idx].item()
            ))

        return results

    def retrieve_symptom_based_history(
            self,
            symptoms: List[str],
            patient_data: Dict,
            top_conversations: int = 5,
            top_entities: int = 10
    ) -> Dict:
        """
        Comprehensive retrieval of patient history based on symptoms

        Args:
            symptoms: List of current symptoms
            patient_data: Dictionary containing patient's historical data
            top_conversations: Number of conversations to retrieve
            top_entities: Number of entities to retrieve

        Returns:
            Dictionary with relevant historical information
        """
        result = {
            'query_symptoms': symptoms,
            'relevant_conversations': [],
            'relevant_diagnoses': [],
            'relevant_medications': [],
            'relevant_procedures': [],
            'relevant_vitals': [],
            'summary': ''
        }

        # Retrieve conversations
        if 'conversations' in patient_data:
            conv_results = self.find_relevant_conversations(
                symptoms,
                patient_data['conversations'],
                top_k=top_conversations
            )
            result['relevant_conversations'] = [
                {**conv, 'similarity_score': score}
                for conv, score in conv_results
            ]

        # Retrieve specific entity types
        if 'entities' in patient_data:
            # Diagnoses
            diagnoses = self.find_relevant_entities(
                symptoms,
                patient_data['entities'],
                entity_types=['disease', 'diagnosis', 'disorder'],
                top_k=5
            )
            result['relevant_diagnoses'] = [
                {**entity, 'similarity_score': score}
                for entity, score in diagnoses
            ]

            # Medications
            medications = self.find_relevant_entities(
                symptoms,
                patient_data['entities'],
                entity_types=['medication', 'drug'],
                top_k=5
            )
            result['relevant_medications'] = [
                {**entity, 'similarity_score': score}
                for entity, score in medications
            ]

            # Procedures
            procedures = self.find_relevant_entities(
                symptoms,
                patient_data['entities'],
                entity_types=['procedure', 'treatment'],
                top_k=5
            )
            result['relevant_procedures'] = [
                {**entity, 'similarity_score': score}
                for entity, score in procedures
            ]

        # Generate summary
        result['summary'] = self._generate_retrieval_summary(result)

        return result

    def _generate_retrieval_summary(self, retrieval_result: Dict) -> str:
        """Generate text summary of retrieval results"""
        summary_parts = []

        # Symptoms
        if retrieval_result['query_symptoms']:
            summary_parts.append(
                f"Query symptoms: {', '.join(retrieval_result['query_symptoms'])}"
            )

        # Conversations
        if retrieval_result['relevant_conversations']:
            dates = [
                conv.get('conversation_date', 'Unknown')
                for conv in retrieval_result['relevant_conversations'][:3]
            ]
            summary_parts.append(
                f"Found {len(retrieval_result['relevant_conversations'])} relevant past visits"
            )

        # Diagnoses
        if retrieval_result['relevant_diagnoses']:
            diagnoses = [
                d.get('entity_value', '')
                for d in retrieval_result['relevant_diagnoses'][:3]
            ]
            summary_parts.append(f"Previous diagnoses: {', '.join(diagnoses)}")

        # Medications
        if retrieval_result['relevant_medications']:
            meds = [
                m.get('entity_value', '')
                for m in retrieval_result['relevant_medications'][:3]
            ]
            summary_parts.append(f"Previous medications: {', '.join(meds)}")

        return ". ".join(summary_parts) + "."

    def rank_by_recency_and_relevance(
            self,
            results: List[Tuple[Dict, float]],
            recency_weight: float = 0.3,
            relevance_weight: float = 0.7
    ) -> List[Tuple[Dict, float]]:
        """
        Re-rank results considering both recency and relevance

        Args:
            results: List of (item, similarity_score) tuples
            recency_weight: Weight for recency (0-1)
            relevance_weight: Weight for relevance (0-1)

        Returns:
            Re-ranked results
        """
        from datetime import datetime

        if not results:
            return results

        # Normalize weights
        total_weight = recency_weight + relevance_weight
        recency_weight /= total_weight
        relevance_weight /= total_weight

        # Calculate recency scores
        now = datetime.utcnow()
        max_days = 365 * 5  # 5 years

        scored_results = []
        for item, sim_score in results:
            # Get date
            date_field = item.get('conversation_date') or item.get('created_at')
            if isinstance(date_field, str):
                from dateutil import parser
                item_date = parser.parse(date_field)
            elif isinstance(date_field, datetime):
                item_date = date_field
            else:
                item_date = now  # Default to now if no date

            # Calculate recency score (0-1, newer is better)
            days_old = (now - item_date).days
            recency_score = max(0, 1 - (days_old / max_days))

            # Combined score
            final_score = (
                    relevance_weight * sim_score +
                    recency_weight * recency_score
            )

            scored_results.append((item, final_score))

        # Sort by combined score
        scored_results.sort(key=lambda x: x[1], reverse=True)

        return scored_results


# Convenience function
def retrieve_patient_history(symptoms: List[str], patient_data: Dict) -> Dict:
    """
    Quick function to retrieve patient history

    Args:
        symptoms: List of symptoms
        patient_data: Patient historical data

    Returns:
        Retrieval results
    """
    retriever = PatientHistoryRetriever()
    return retriever.retrieve_symptom_based_history(symptoms, patient_data)