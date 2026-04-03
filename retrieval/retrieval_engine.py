from typing import List, Dict
import numpy as np
import logging
from retrieval.embedding import BioBERTEmbedding

logger = logging.getLogger(__name__)

embedder = BioBERTEmbedding()


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    try:
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return float(np.dot(a, b) / (norm_a * norm_b))

    except Exception as e:
        logger.error(f"Error in cosine similarity: {e}")
        return 0.0


def retrieve_similar_cases(query_text: str, case_database: List[Dict], top_k: int = 3) -> List[Dict]:
    """
    Safe and robust similarity retrieval function
    """

    # 🔹 =========================
    # INPUT VALIDATION
    # 🔹 =========================
    if not query_text or not isinstance(query_text, str) or not query_text.strip():
        logger.error("Invalid query_text received")
        raise ValueError("Query text must be a non-empty string")

    if not isinstance(case_database, list):
        logger.error("Invalid case database format")
        raise ValueError("Case database must be a list")

    if not isinstance(top_k, int) or top_k <= 0:
        logger.warning("Invalid top_k value. Defaulting to 3")
        top_k = 3

    # 🔹 =========================
    # EMBEDDING GENERATION
    # 🔹 =========================
    try:
        query_embedding = embedder.get_embedding(query_text)

        if query_embedding is None or len(query_embedding) == 0:
            logger.error("Failed to generate query embedding")
            raise ValueError("Embedding generation failed")

        query_embedding = np.array(query_embedding)

    except Exception as e:
        logger.error(f"Embedding error: {e}")
        raise ValueError("Error generating embedding")

    results = []

    # 🔹 =========================
    # SIMILARITY COMPUTATION
    # 🔹 =========================
    for case_data in case_database:
        if not isinstance(case_data, dict):
            logger.warning(f"Skipping invalid case entry: {case_data}")
            continue

        try:
            case_embedding = np.array(case_data.get("embedding", []))

            if case_embedding.size == 0:
                continue

            similarity = cosine_similarity(query_embedding, case_embedding)

            results.append({
                "case_id": case_data.get("case_id", "Unknown"),
                "similarity": similarity,
                "diagnosis": case_data.get("diagnosis", "Unknown"),
                "treatment": case_data.get("treatment", "Unknown"),
                "symptoms": case_data.get("symptoms", [])
            })

        except Exception as e:
            logger.warning(f"Skipping case due to error: {e}")
            continue

    # 🔹 =========================
    # SORTING & TOP-K SELECTION
    # 🔹 =========================
    try:
        results = sorted(results, key=lambda x: x["similarity"], reverse=True)
    except Exception as e:
        logger.error(f"Sorting error: {e}")
        return []

    return results[:top_k]