import numpy as np
from typing import List
from loguru import logger
from sentence_transformers import SentenceTransformer
from config.settings import settings

def batch_iterate(lst: List, batch_size: int):
    for i in range(0, len(lst), batch_size):
        yield lst[i:i+batch_size]

class EmbedData:
    """Handles document embedding with binary quantization support."""
    def __init__(
        self, 
        embed_model_name: str = None,
        batch_size: int = None,
        cache_folder: str = None
    ):
        self.embed_model_name = embed_model_name or settings.embedding_model
        self.batch_size = batch_size or settings.batch_size
        self.cache_folder = cache_folder or settings.hf_cache_dir
        
        self.embed_model = self._load_embed_model()
        self.embeddings = []
        self.binary_embeddings = []
        self.contexts = []

    def _load_embed_model(self):
        """Load the embedding model using sentence-transformers"""
        logger.info(f"Loading embedding model: {self.embed_model_name}")
        model = SentenceTransformer(
            model_name_or_path=self.embed_model_name,
            cache_folder=self.cache_folder,
            trust_remote_code=True,
        )
        return model

    def _binary_quantize(self, embeddings: List[List[float]]):
        """Convert float32 embeddings to binary vectors."""
        embeddings_array = np.array(embeddings)
        binary_embeddings = np.where(embeddings_array > 0, 1, 0).astype(np.uint8)
        
        # Pack bits into bytes (8 dimensions per byte)
        packed_embeddings = np.packbits(binary_embeddings, axis=1)
        return [vec.tobytes() for vec in packed_embeddings]

    def generate_embedding(self, contexts: List[str]):
        embeddings = self.embed_model.encode(
            sentences=contexts,
            batch_size=min(self.batch_size, max(1, len(contexts))),
            convert_to_numpy=True,
            normalize_embeddings=False,
            show_progress_bar=False,
        )
        return embeddings.tolist()

    def embed(self, contexts: List[str]):
        self.contexts = contexts
        logger.info(f"Generating embeddings for {len(contexts)} contexts...")

        for batch_context in batch_iterate(contexts, self.batch_size):
            # Generate float32 embeddings
            batch_embeddings = self.generate_embedding(batch_context)
            self.embeddings.extend(batch_embeddings)

            # Convert to binary and store
            binary_batch = self._binary_quantize(batch_embeddings)
            self.binary_embeddings.extend(binary_batch)

        logger.info(f"Generated {len(self.embeddings)} embeddings with binary quantization")

    def get_query_embedding(self, query: str):
        # Generate embedding for a single query
        embedding = self.embed_model.encode(
            sentences=[query],
            convert_to_numpy=True,
            normalize_embeddings=False,
            show_progress_bar=False,
        )
        return embedding[0].tolist()

    def binary_quantize_query(self, query_embedding: List[float]):
        # Convert query embedding to binary format
        embedding_array = np.array([query_embedding])
        binary_embedding = np.where(embedding_array > 0, 1, 0).astype(np.uint8)
        packed_embedding = np.packbits(binary_embedding, axis=1)
        return packed_embedding[0].tobytes()

    def clear(self):
        self.embeddings.clear()
        self.binary_embeddings.clear()
        self.contexts.clear()
        logger.info("Cleared all embeddings and contexts")