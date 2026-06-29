from typing import List, Dict, Any

try:
    from fastembed import TextEmbedding
except ImportError:
    raise ImportError(
        "fastembed package is required. "
        "Install it with: pip install fastembed"
    )


class FAQEmbedder:
    """
    Generates vector embeddings for FAQ child chunks
    using FastEmbed ONNX inference.
    """

    EXPECTED_DIMENSION = 384

    def __init__(
        self,
        model_name: str = "BAAI/bge-small-en-v1.5"
    ):
        self.model = TextEmbedding(model_name=model_name)

    def embed_chunks(
        self,
        chunks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Enriches chunk records with embedding vectors.
        """
        if not chunks:
            return []

        valid_chunks = [
            chunk for chunk in chunks
            if chunk.get("content")
        ]

        if not valid_chunks:
            return []

        texts_to_embed = [
            chunk["content"]
            for chunk in valid_chunks
        ]

        try:
            embeddings = list(
                self.model.embed(texts_to_embed)
            )

            enriched_chunks: List[Dict[str, Any]] = []

            for chunk, vector in zip(valid_chunks, embeddings):
                vector_list = vector.tolist()

                if len(vector_list) != self.EXPECTED_DIMENSION:
                    raise ValueError(
                        f"Embedding dimension mismatch. "
                        f"Expected {self.EXPECTED_DIMENSION}, "
                        f"got {len(vector_list)}"
                    )

                enriched = chunk.copy()
                enriched["embedding"] = vector_list

                enriched_chunks.append(enriched)

            return enriched_chunks

        except Exception as e:
            raise RuntimeError(
                f"Embedding generation failed: {str(e)}"
            )