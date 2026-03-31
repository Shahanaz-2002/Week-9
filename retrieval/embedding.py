import numpy as np
from typing import Dict, Any
import torch
from transformers import AutoTokenizer, AutoModel

class BioBERTEmbedding:
    _instance = None 

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BioBERTEmbedding, cls).__new__(cls)
            cls._instance.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            cls._instance.MODEL_NAME = "emilyalsentzer/Bio_ClinicalBERT"
            
            print("🔄 Loading BioClinicalBERT model... (only once)")
            cls._instance.tokenizer = AutoTokenizer.from_pretrained(cls._instance.MODEL_NAME)
            cls._instance.model = AutoModel.from_pretrained(cls._instance.MODEL_NAME)
            cls._instance.model.to(cls._instance.device)
            cls._instance.model.eval()

        return cls._instance

    def mean_pooling(self, model_output, attention_mask):
        token_embeddings = model_output.last_hidden_state
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, dim=1)
        sum_mask = torch.clamp(input_mask_expanded.sum(dim=1), min=1e-9)
        return sum_embeddings / sum_mask

    def get_embedding(self, text: str) -> np.ndarray:
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)

        embedding = self.mean_pooling(outputs, inputs["attention_mask"]).cpu().numpy()[0]
        norm = np.linalg.norm(embedding)

        if norm > 0:
            embedding = embedding / norm
        else:
            embedding = np.zeros_like(embedding)

        return embedding