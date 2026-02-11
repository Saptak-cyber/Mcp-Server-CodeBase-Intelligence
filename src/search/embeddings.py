"""HuggingFace Inference API for embeddings."""

import httpx
from typing import List
from tenacity import retry, stop_after_attempt, wait_exponential
from ..config import get_settings
from ..utils.logging import get_logger

logger = get_logger(__name__)


class EmbeddingGenerator:
    """Generate embeddings using HuggingFace Inference API."""

    def __init__(self):
        """Initialize embedding generator."""
        settings = get_settings()
        self.api_key = settings.huggingface_api_key
        self.model = settings.huggingface_model
        self.api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{self.model}"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def embed(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.api_url,
                headers=self.headers,
                json={"inputs": text, "options": {"wait_for_model": True}},
            )
            response.raise_for_status()
            
            # HuggingFace returns embeddings as nested list
            embedding = response.json()
            if isinstance(embedding, list) and len(embedding) > 0:
                if isinstance(embedding[0], list):
                    return embedding[0]
                return embedding
            
            raise ValueError("Invalid embedding response format")

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        # Process in smaller batches to respect API limits
        batch_size = 32
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            
            try:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(
                        self.api_url,
                        headers=self.headers,
                        json={
                            "inputs": batch,
                            "options": {"wait_for_model": True}
                        },
                    )
                    response.raise_for_status()
                    
                    embeddings = response.json()
                    
                    # Handle different response formats
                    if isinstance(embeddings, list):
                        # If embeddings are nested lists, flatten if needed
                        for emb in embeddings:
                            if isinstance(emb, list) and len(emb) > 0:
                                if isinstance(emb[0], list):
                                    all_embeddings.append(emb[0])
                                else:
                                    all_embeddings.append(emb)
                    
                    logger.info(f"Generated {len(batch)} embeddings")
                    
            except Exception as e:
                logger.error(f"Batch embedding failed", error=str(e))
                # Fallback to individual embeddings
                for text in batch:
                    try:
                        emb = await self.embed(text)
                        all_embeddings.append(emb)
                    except Exception as e2:
                        logger.error(f"Individual embedding failed", error=str(e2))
                        # Use zero vector as fallback
                        all_embeddings.append([0.0] * 768)

        return all_embeddings
