import { useState, useRef } from 'react'
import { useQuery } from '@tanstack/react-query'
import { filesService } from '../services/api'
import { Button } from '../components/ui/Button'
import { Loading } from '../components/ui/Loading'
import { Upload, Trash2, FileText, Calendar } from 'lucide-react'

/**
 * Página para gestionar archivos subidos
 */
export function FilesPage() {
  const [uploading, setUploading] = useState(false)
  const fileInputRef = useRef(null)

  const {
    data: files = [],
    isLoading,
    error: filesError,
    refetch,
  } = useQuery({
    queryKey: ['files'],
    queryFn: filesService.getFiles,
    retry: 1,
    refetchOnWindowFocus: false,
  })

  const handleFileSelect = () => {
    fileInputRef.current?.click()
  }

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return

    if (file.type !== 'application/pdf') {
      alert('Solo se permiten archivos PDF')
      e.target.value = '' // Reset input
      return
    }

    setUploading(true)
    try {
      await filesService.uploadFile(file)
      await refetch()
      alert('Archivo subido correctamente')
      e.target.value = '' // Reset input
    } catch (error) {
      console.error('Error al subir archivo:', error)
      alert(`Error al subir archivo: ${error.message || 'Error desconocido'}`)
      e.target.value = '' // Reset input
    } finally {
      setUploading(false)
    }
  }

  const handleDelete = async (documentId) => {
    if (!confirm('¿Estás seguro de eliminar este archivo?')) return

    try {
      await filesService.deleteFile(documentId)
      await refetch()
    } catch (error) {
      alert(`Error al eliminar archivo: ${error.message}`)
    }
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    const date = new Date(dateString)
    return date.toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return (
    <div className="container-app py-4 sm:py-6 px-3 sm:px-4">
      <div className="max-w-4xl mx-auto">
        <div className="flex flex-col gap-4 sm:gap-6 mb-6 sm:mb-8">
          {/* Título y descripción */}
          <div className="flex-1 min-w-0">
            <h1 className="text-lg sm:text-2xl font-medium text-dark-text-primary mb-1 sm:mb-2 tracking-tight">
              Gestión de Archivos
            </h1>
            <p className="text-dark-text-secondary text-xs sm:text-[15px] leading-relaxed">
              Sube y gestiona los documentos PDF que el agente utilizará para responder consultas
            </p>
          </div>

          {/* Botón de subir */}
          <div className="flex-shrink-0">
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf"
              onChange={handleFileUpload}
              disabled={uploading}
              className="hidden"
            />
            <Button
              type="button"
              onClick={handleFileSelect}
              disabled={uploading}
              className="w-full sm:w-auto"
            >
              {uploading ? (
                <>
                  <Loading size="sm" className="sm:mr-2" />
                  <span>Subiendo...</span>
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4 sm:mr-2" />
                  <span>Subir PDF</span>
                </>
              )}
            </Button>
          </div>
        </div>

        {isLoading ? (
          <div className="flex justify-center py-16">
            <Loading size="lg" />
          </div>
        ) : filesError ? (
          <div className="card-gemini p-12 text-center">
            <FileText className="w-16 h-16 mx-auto mb-4 text-dark-text-muted opacity-50" />
            <p className="text-dark-text-secondary mb-6 text-[15px] leading-relaxed">
              Error al cargar archivos: {filesError.message || 'Error desconocido'}
            </p>
            <Button onClick={() => refetch()} variant="secondary" size="sm">
              Reintentar
            </Button>
          </div>
        ) : files.length === 0 ? (
          <div className="card-gemini p-12 text-center">
            <FileText className="w-16 h-16 mx-auto mb-4 text-dark-text-muted opacity-50" />
            <p className="text-dark-text-secondary text-[15px] leading-relaxed">
              No hay archivos subidos. Sube un PDF para comenzar.
            </p>
          </div>
        ) : (
          <div className="space-y-2 sm:space-y-3">
            {files.map((file) => (
              <div
                key={file.document_id}
                className="card-gemini p-3 sm:p-4 flex items-center justify-between group gap-2 sm:gap-4"
              >
                <div className="flex items-center gap-2 sm:gap-4 flex-1 min-w-0">
                  <div className="flex-shrink-0 w-9 h-9 sm:w-11 sm:h-11 rounded-xl bg-dark-accent-primary/15 flex items-center justify-center border border-dark-accent-primary/20">
                    <FileText className="w-4 h-4 sm:w-5 sm:h-5 text-dark-accent-primary" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-medium text-dark-text-primary truncate text-xs sm:text-[15px] leading-tight">
                      {file.filename}
                    </h3>
                    <div className="flex flex-col sm:flex-row sm:items-center gap-0.5 sm:gap-4 mt-1 sm:mt-1.5 text-[10px] sm:text-sm text-dark-text-muted">
                      <span className="flex items-center gap-1">
                        <Calendar className="w-2.5 h-2.5 sm:w-3.5 sm:h-3.5" />
                        {formatDate(file.uploaded_at)}
                      </span>
                      {file.chunk_count && (
                        <span className="hidden sm:inline text-xs">{file.chunk_count} fragmentos</span>
                      )}
                    </div>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleDelete(file.document_id)}
                  className="text-dark-status-error hover:bg-dark-status-error/10 ml-1 sm:ml-4 opacity-100 sm:opacity-0 sm:group-hover:opacity-100 transition-opacity rounded-xl flex-shrink-0 p-1.5 sm:p-2"
                  aria-label="Eliminar archivo"
                >
                  <Trash2 className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                </Button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default FilesPage

