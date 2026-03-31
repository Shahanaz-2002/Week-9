from typing import List, Dict
import numpy as np
from retrieval.embedding import BioBERTEmbedding

embedder = BioBERTEmbedding()

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))

def retrieve_similar_cases(query_text: str, case_database: List[Dict], top_k: int = 3) -> List[Dict]:
    """
    Day 1 & 2 Objective: Sole source of truth for similarity.
    Takes a plain text string query, embeds it, and compares against the DB list.
    """
    query_embedding = embedder.get_embedding(query_text)
    results = []

    for case_data in case_database:
        case_embedding = np.array(case_data.get("embedding", []))

        if case_embedding.size == 0:
            continue

        similarity = cosine_similarity(query_embedding, case_embedding)

        results.append({
            "case_id": case_data["case_id"],
            "similarity": similarity,
            "diagnosis": case_data.get("diagnosis"),
            "treatment": case_data.get("treatment"),
            "symptoms": case_data.get("symptoms", [])
        })

    # Sort descending by similarity
    results = sorted(results, key=lambda x: x["similarity"], reverse=True)
    return results[:top_k]