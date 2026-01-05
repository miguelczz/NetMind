"""
Servicio de embeddings - Refactorizado para usar repositorios y utilidades
"""
import os
import uuid
import logging
from typing import List
from ..repositories.qdrant_repository import get_qdrant_repository
from ..utils.text_processing import text_splitter, process_pdf_to_text
from ..utils.embeddings import embedding_for_text_batch
from ..settings import settings

logger = logging.getLogger(__name__)

# Instancia global del repositorio Qdrant (Lazy loaded via singleton)
# _qdrant_repo se puede reemplazar por llamadas directas a get_qdrant_repository() pero para minimizar cambios:
_qdrant_repo = get_qdrant_repository()


async def process_and_store_pdf(path: str, document_id: str = None) -> str:
    """
    Procesa un PDF, genera embeddings y los guarda en Qdrant.
    
    Args:
        path: Ruta al archivo PDF
        document_id: ID del documento (se genera si no se proporciona)
    
    Returns:
        document_id del documento procesado
    """
    if document_id is None:
        document_id = str(uuid.uuid4())

    logger.info(f"Procesando PDF: {path} (document_id: {document_id})")
    
    # Extraer texto del PDF
    try:
        text = process_pdf_to_text(path)
        if not text or not text.strip():
            raise ValueError(f"No se pudo extraer texto del PDF o el PDF está vacío: {path}")
        logger.info(f"Texto extraído: {len(text)} caracteres")
    except Exception as e:
        logger.error(f"Error al extraer texto del PDF: {str(e)}", exc_info=True)
        raise
    
    # Dividir en chunks
    try:
        chunks = text_splitter(
            text, 
            chunk_size=settings.chunk_size, 
            overlap=settings.chunk_overlap
        )
        if not chunks:
            raise ValueError("No se generaron chunks del texto")
        logger.info(f"Texto dividido en {len(chunks)} chunks")
    except Exception as e:
        logger.error(f"Error al dividir texto en chunks: {str(e)}", exc_info=True)
        raise
    
    # Generar embeddings
    try:
        logger.info(f"Generando embeddings para {len(chunks)} chunks...")
        embeddings = embedding_for_text_batch(chunks)
        if not embeddings or len(embeddings) != len(chunks):
            raise ValueError(f"Error al generar embeddings: se esperaban {len(chunks)}, se obtuvieron {len(embeddings) if embeddings else 0}")
        logger.info(f"Embeddings generados exitosamente")
    except Exception as e:
        logger.error(f"Error al generar embeddings: {str(e)}", exc_info=True)
        raise
    
    # Preparar puntos para Qdrant
    try:
        points = []
        for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
            points.append({
                "vector": emb,
                "payload": {
                    "text": chunk,
                    "source": os.path.basename(path),
                    "chunk_index": i,
                    "document_id": document_id
                }
            })
        logger.info(f"Preparados {len(points)} puntos para insertar en Qdrant")
    except Exception as e:
        logger.error(f"Error al preparar puntos: {str(e)}", exc_info=True)
        raise

    # Insertar en Qdrant usando el repositorio
    try:
        logger.info(f"Insertando {len(points)} puntos en Qdrant para document_id: {document_id}")
        success = _qdrant_repo.upsert_points(points)
        if not success:
            raise ValueError("upsert_points retornó False")
        
        # Verificar que se insertaron todos los puntos
        collection_info = _qdrant_repo.get_collection_info()
        if isinstance(collection_info, dict) and "error" not in collection_info:
            points_count = collection_info.get('points_count', 0)
            logger.info(f"✅ Verificación: Colección Qdrant tiene {points_count} puntos totales después de insertar {len(points)} puntos para document_id: {document_id}")
        else:
            logger.warning(f"⚠️ No se pudo verificar la inserción en Qdrant: {collection_info}")
        
        logger.info(f"✅ Puntos insertados exitosamente en Qdrant para document_id: {document_id} ({len(points)} chunks)")
    except Exception as e:
        logger.error(f"❌ Error al insertar puntos en Qdrant: {str(e)}", exc_info=True)
        logger.error(f"❌ Se intentaron insertar {len(points)} puntos pero falló")
        raise
    
    return document_id


def delete_by_id(document_id: str) -> bool:
    """
    Elimina todos los vectores en Qdrant asociados a un document_id.
    
    Args:
        document_id: ID del documento a eliminar
    
    Returns:
        True si la operación fue exitosa
    """
    return _qdrant_repo.delete_by_document_id(document_id)
