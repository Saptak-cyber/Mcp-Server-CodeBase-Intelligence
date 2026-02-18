"""HuggingFace Inference API for embeddings.

Based on: https://huggingface.co/docs/inference-providers/
Uses the new Inference Providers API (replaces deprecated api-inference.huggingface.co)
"""

from typing import List, Optional, Tuple
from tenacity import retry, stop_after_attempt, wait_exponential
from huggingface_hub import InferenceClient
from ..config import get_settings
from ..utils.logging import get_logger

logger = get_logger(__name__)


class EmbeddingGenerator:
    """Generate embeddings using HuggingFace Inference Providers API.
    
    Supports feature-extraction task for sentence-transformers models.
    See: https://huggingface.co/docs/inference-providers/tasks/feature-extraction
    
    Note: The old api-inference.huggingface.co endpoint is deprecated (returns 410).
    This implementation uses the new InferenceClient from huggingface_hub.
    """

    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None) -> None:
        """Initialize embedding generator.
        
        Args:
            model: HuggingFace model ID (e.g., 'sentence-transformers/all-MiniLM-L6-v2')
            api_key: HuggingFace API token
        """
        settings = get_settings()
        self.api_key = api_key or settings.huggingface_api_key
        self.model = model or settings.huggingface_model
        
        # Use new InferenceClient with hf-inference provider
        self.client = InferenceClient(
            provider="hf-inference",
            api_key=self.api_key,
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def embed(self, text: str) -> List[float]:
        """Generate embedding for a single text using feature-extraction task.
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats representing the embedding vector
            
        Raises:
            Exception: If API request fails or response format is invalid
        """
        try:
            # Use the new InferenceClient feature_extraction method
            # Note: This is synchronous, but wrapped in async for compatibility
            embedding = self.client.feature_extraction(
                text=text,
                model=self.model,
            )
            
            # Convert to list if needed (may be numpy array or similar)
            if hasattr(embedding, 'tolist'):
                return embedding.tolist()
            elif isinstance(embedding, list):
                return embedding
            else:
                return list(embedding)
                
        except Exception as e:
            logger.error(f"Embedding generation failed for text: {text[:50]}...", error=str(e))
            raise

    async def embed_batch(self, texts: List[str], batch_size: int = 32) -> Tuple[List[List[float]], List[int]]:
        """Generate embeddings for multiple texts concurrently.
        
        Args:
            texts: List of input texts to embed
            batch_size: Number of texts to process concurrently (default: 32)
            
        Returns:
            Tuple of (embeddings, failed_indices) where:
            - embeddings: list of embedding vectors for successful texts
            - failed_indices: list of indices that failed (skipped)
        """
        import asyncio
        
        all_embeddings: List[List[float]] = []
        failed_indices: List[int] = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            
            # Use asyncio.gather for concurrent embedding within each batch
            async def _safe_embed(text: str, idx: int) -> Tuple[Optional[List[float]], int]:
                try:
                    emb = await self.embed(text)
                    return emb, idx
                except Exception as e:
                    logger.error(f"Embedding failed for index {idx}", error=str(e))
                    return None, idx
            
            tasks = [_safe_embed(text, i + j) for j, text in enumerate(batch)]
            results = await asyncio.gather(*tasks)
            
            batch_embeddings = []
            for emb, idx in results:
                if emb is not None:
                    batch_embeddings.append(emb)
                else:
                    failed_indices.append(idx)
            
            all_embeddings.extend(batch_embeddings)
            logger.info(f"Generated {len(batch_embeddings)} embeddings (batch {i//batch_size + 1})")

        return all_embeddings, failed_indices
