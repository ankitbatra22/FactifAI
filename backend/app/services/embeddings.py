from sentence_transformers import SentenceTransformer

class EmbeddingService:
    def __init__(self):
        # Using a good model for scientific text
        self.model = SentenceTransformer('allenai/specter')
    
    def get_embedding(self, text: str) -> list[float]:
        embedding = self.model.encode(text)
        return embedding.tolist()