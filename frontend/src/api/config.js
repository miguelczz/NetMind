import axios from 'axios';

// Determinar la URL base dinámicamente
const getBaseUrl = () => {
  // 1. Si hay una variable de entorno explícita (Producción real), usarla.
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }

  // 2. Si estamos en desarrollo/local y accedemos por IP (ej: 192.168.x.x),
  // construir la URL del backend usando el mismo hostname pero puerto 8000.
  const hostname = window.location.hostname;
  return `http://${hostname}:8000`;
};

const api = axios.create({
  baseURL: getBaseUrl(),
});

export default api;
