import axios from 'axios'
import { API_URL, API_ENDPOINTS } from '../config/constants'

/**
 * Cliente API configurado para comunicarse con el backend FastAPI
 */
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 120000, // 120 segundos (2 minutos) - el grafo puede tardar más
})

// Interceptor para manejar errores globalmente
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // El servidor respondió con un código de error
      console.error('API Error:', error.response.data)
      return Promise.reject({
        message: error.response.data?.detail || 'Error en la petición',
        status: error.response.status,
        data: error.response.data,
      })
    } else if (error.request) {
      // La petición se hizo pero no hubo respuesta
      console.error('Network Error:', error.request)
      console.error('Request URL:', error.config?.url)
      console.error('Base URL:', error.config?.baseURL)
      console.error('Full URL:', error.config?.baseURL + error.config?.url)
      return Promise.reject({
        message: `No se pudo conectar con el servidor en ${error.config?.baseURL || API_URL}. Verifica que el backend esté corriendo.`,
        status: 0,
        originalError: error,
      })
    } else {
      // Algo más causó el error
      console.error('Error:', error.message)
      return Promise.reject({
        message: error.message || 'Error desconocido',
        status: 0,
      })
    }
  }
)

/**
 * Servicio para interactuar con el agente
 */
export const agentService = {
  /**
   * Obtiene el historial de mensajes de una sesión
   * @param {string} sessionId - ID de sesión
   * @returns {Promise} - Historial de mensajes
   */
  async getSessionHistory(sessionId) {
    try {
      const response = await apiClient.get(`${API_ENDPOINTS.AGENT_SESSION}/${sessionId}`)
      return response.data
    } catch (error) {
      // Si la sesión no existe o hay error, retornar historial vacío
      if (error.status === 404) {
        return { session_id: sessionId, messages: [], context_length: 0 }
      }
      console.error('Error al obtener historial de sesión:', error)
      return { session_id: sessionId, messages: [], context_length: 0 }
    }
  },

  /**
   * Limpia el historial de mensajes de una sesión
   * @param {string} sessionId - ID de sesión
   * @returns {Promise} - Respuesta de limpieza
   */
  async clearSession(sessionId) {
    try {
      const response = await apiClient.delete(`${API_ENDPOINTS.AGENT_SESSION}/${sessionId}`)
      return response.data
    } catch (error) {
      console.error('Error al limpiar sesión:', error)
      throw error
    }
  },

  /**
   * Envía una consulta al agente
   * @param {Object} queryData - Datos de la consulta
   * @param {string} queryData.session_id - ID de sesión
   * @param {string} queryData.user_id - ID de usuario (opcional)
   * @param {Array} queryData.messages - Array de mensajes
   * @returns {Promise} - Respuesta del agente
   */
  async sendQuery({ session_id, user_id = null, messages }) {
    const response = await apiClient.post(API_ENDPOINTS.AGENT_QUERY, {
      session_id,
      user_id,
      messages: messages.map((msg) => ({
        role: msg.role,
        content: msg.content,
      })),
    })
    return response.data
  },
}

/**
 * Servicio para gestionar archivos
 */
export const filesService = {
  /**
   * Sube un archivo al servidor
   * @param {File} file - Archivo a subir
   * @returns {Promise} - Respuesta con información del archivo
   */
  async uploadFile(file) {
    const formData = new FormData()
    formData.append('file', file)

    // Crear un cliente temporal sin el header Content-Type para que axios lo configure automáticamente
    const uploadClient = axios.create({
      baseURL: API_URL,
      timeout: 60000, // 60 segundos para archivos grandes
    })

    const response = await uploadClient.post(API_ENDPOINTS.FILES_UPLOAD, formData, {
      headers: {
        // No establecer Content-Type, axios lo hará automáticamente con el boundary correcto
      },
    })
    return response.data
  },

  /**
   * Obtiene la lista de archivos subidos
   * @returns {Promise} - Lista de archivos
   */
  async getFiles() {
    try {
      const response = await apiClient.get(API_ENDPOINTS.FILES_LIST)
      return response.data || []
    } catch (error) {
      console.error('Error al obtener archivos:', error)
      // Si es un error 404 o la lista está vacía, retornar array vacío
      if (error.status === 404) {
        return []
      }
      throw error
    }
  },

  /**
   * Elimina un archivo
   * @param {string} documentId - ID del documento
   * @returns {Promise} - Respuesta de eliminación
   */
  async deleteFile(documentId) {
    const response = await apiClient.delete(
      `${API_ENDPOINTS.FILES_DELETE}/${documentId}`
    )
    return response.data
  },
}

export default apiClient

