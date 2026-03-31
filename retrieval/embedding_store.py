from retrieval.database import collection
from retrieval.embedding import BioBERTEmbedding
from config import EMBEDDING_VERSION
from datetime import datetime

embedder = BioBERTEmbedding()

def generate_and_store_embeddings():
    records = collection.find({})

    for record in records:
        case_id = record["case_id"]
        text = " ".join(record.get("symptoms", [])) + " " + record.get("doctor_notes", "")
        embedding = embedder.get_embedding(text)

        collection.update_one(
            {"case_id": case_id},
            {
                "$set": {
                    "embedding": embedding.tolist(),
                    "embedding_version": EMBEDDING_VERSION,
                    "embedding_created_at": datetime.utcnow()
                }
            }
        )
        print(f"Embedding stored for {case_id}")

if __name__ == "__main__":
    generate_and_store_embeddings()