"""
API endpoints para gestión de archivos - Refactorizado para usar repositorios
"""
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List
from sqlalchemy.orm import Session as SQLSession
from ..models.schemas import FileUploadResponse, FileListResponse
from ..models.database import get_db
from ..repositories.document_repository import DocumentRepository
from ..repositories.qdrant_repository import QdrantRepository
from ..services.embeddings_service import process_and_store_pdf, delete_by_id
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/files", tags=["files"])

# Instancias de repositorios
document_repo = DocumentRepository()
qdrant_repo = QdrantRepository()

@router.post("/upload", status_code=201, response_model=FileUploadResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    db: SQLSession = Depends(get_db)
):
    """
    Sube y procesa un archivo PDF.
    Guarda el archivo, genera embeddings y almacena metadatos en BD.
    """
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    # Leer contenido del archivo
    content = await file.read()
    logger.info(f"Iniciando procesamiento de archivo: {file.filename}")
    
    # Guardar archivo usando el repositorio
    document_id, file_path = document_repo.save_file(content, file.filename)
    logger.info(f"Archivo guardado. Document ID: {document_id}, Path: {file_path}")
    
    # Procesar PDF (chunk + embeddings + store en Qdrant)
    try:
        processed_doc_id = await process_and_store_pdf(file_path, document_id=document_id)
        logger.info(f"PDF procesado exitosamente. Document ID: {processed_doc_id}")
    except Exception as e:
        logger.error(f"Error al procesar PDF: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Error al procesar el PDF: {str(e)}"
        )
    
    # Verificar que los datos se insertaron en Qdrant
    try:
        collection_info = qdrant_repo.get_collection_info()
        if "error" in collection_info:
            logger.warning(f"Error al verificar colección Qdrant: {collection_info['error']}")
        else:
            logger.info(f"Colección Qdrant verificada. Puntos totales: {collection_info.get('points_count', 0)}")
    except Exception as e:
        logger.warning(f"No se pudo verificar colección Qdrant: {str(e)}")
    
    # Obtener número de chunks (simplificado, podría mejorarse)
    # Por ahora, asumimos que se procesó correctamente
    chunk_count = 0  # Se podría calcular desde Qdrant si es necesario
    
    # Guardar metadatos en BD
    document_repo.create_document_metadata(
        db=db,
        document_id=document_id,
        filename=file.filename,
        file_path=file_path,
        chunk_count=chunk_count,
        source=file.filename
    )
    
    return FileUploadResponse(
        document_id=document_id,
        filename=file.filename,
        status="processed",
        uploaded_at=datetime.utcnow()
    )


@router.get("/", response_model=List[FileListResponse])
async def list_files(db: SQLSession = Depends(get_db)):
    """
    Lista todos los archivos con sus metadatos.
    """
    documents = document_repo.list_documents(db)
    return [
        FileListResponse(
            document_id=doc.document_id,
            filename=doc.filename,
            uploaded_at=doc.uploaded_at
        )
        for doc in documents
    ]


@router.delete("/{document_id}")
async def delete_file(
    document_id: str,
    db: SQLSession = Depends(get_db)
):
    """
    Elimina un archivo y todos sus vectores asociados.
    """
    # Verificar que el documento existe
    doc = document_repo.get_document_by_id(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Eliminar archivo del sistema de archivos
    document_repo.delete_file(document_id)
    
    # Eliminar vectores de Qdrant
    deleted = delete_by_id(document_id)
    if not deleted:
        raise HTTPException(
            status_code=500, 
            detail="Failed to delete vectors from Qdrant"
        )

    # Eliminar metadatos de BD
    document_repo.delete_document(db, document_id)
    
    return {
        "status": "deleted",
        "document_id": document_id,
        "filename": doc.filename
    }