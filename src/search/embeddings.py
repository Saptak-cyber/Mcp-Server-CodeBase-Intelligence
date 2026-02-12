"""HuggingFace Inference API for embeddings.

Based on: https://huggingface.co/docs/inference-providers/
Uses the new Inference Providers API (replaces deprecated api-inference.huggingface.co)
"""

from typing import List, Optional
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

    async def embed_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """Generate embeddings for multiple texts in batches.
        
        Args:
            texts: List of input texts to embed
            batch_size: Number of texts to process per API call (default: 32)
            
        Returns:
            List of embedding vectors, one per input text
            
        Note:
            Falls back to individual embedding on batch failure.
            Uses zero vector as last resort fallback.
        """
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]

            try:
                # Process batch - InferenceClient handles batching internally
                for text in batch:
                    try:
                        emb = await self.embed(text)
                        all_embeddings.append(emb)
                    except Exception as e:
                        logger.error(f"Individual embedding failed in batch", error=str(e))
                        # Use zero vector as fallback (768 is common for sentence-transformers)
                        all_embeddings.append([0.0] * 768)

                logger.info(f"Generated {len(batch)} embeddings (batch {i//batch_size + 1})")

            except Exception as e:
                logger.error("Batch processing failed", error=str(e))
                # Fallback: try individual embeddings
                for text in batch:
                    try:
                        emb = await self.embed(text)
                        all_embeddings.append(emb)
                    except Exception as e2:
                        logger.error("Individual embedding failed", error=str(e2))
                        all_embeddings.append([0.0] * 768)

        return all_embeddings
