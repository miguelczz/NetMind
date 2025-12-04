"""
Utilidades para generación de embeddings
"""
from typing import List
from openai import OpenAI
from ..settings import settings

# Cliente OpenAI global para embeddings
_client = OpenAI(api_key=settings.openai_api_key)


def embedding_for_text(text: str) -> List[float]:
    """
    Genera un embedding para un texto usando OpenAI.
    
    Args:
        text: Texto a convertir en embedding
    
    Returns:
        Lista de floats representando el embedding
    """
    response = _client.embeddings.create(
        model=settings.embedding_model,
        input=text
    )
    return response.data[0].embedding


def embedding_for_text_batch(texts: List[str]) -> List[List[float]]:
    """
    Genera embeddings para una lista de textos usando OpenAI.
    Más eficiente que llamar embedding_for_text múltiples veces.
    
    Args:
        texts: Lista de textos a convertir en embeddings
    
    Returns:
        Lista de embeddings (cada uno es una lista de floats)
    """
    if not texts:
        return []

    response = _client.embeddings.create(
        model=settings.embedding_model,
        input=texts
    )
    return [d.embedding for d in response.data]

