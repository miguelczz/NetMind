import { createContext, useContext, useState } from 'react';

const NetworkContext = createContext();

export function useNetworkContext() {
  return useContext(NetworkContext);
}

export function NetworkProvider({ children }) {
  // Estado para Dashboard
  // Inicializamos con un array vacío para evitar datos falsos
  const [latencyHistory, setLatencyHistory] = useState([]);

  // Estado para Geo-Trace
  const [geoHost, setGeoHost] = useState('');
  const [geoResults, setGeoResults] = useState(null);
  const [isTracing, setIsTracing] = useState(false);

  // Estado persistente de incidentes
  const [incidentLog, setIncidentLog] = useState([]);
  const [networkStatus, setNetworkStatus] = useState('ok'); // 'ok' | 'issue'

  // Acciones
  const addLatencyPoint = (point) => {
    setLatencyHistory(prev => {
      // Mantener solo los últimos 20 puntos
      const newHistory = [...prev, point];
      if (newHistory.length > 20) {
        return newHistory.slice(newHistory.length - 20);
      }
      return newHistory;
    });

    // Análisis de incidentes persistente
    const isBad = point.latency > 100;
    const isOutage = point.latency >= 500;

    if (networkStatus === 'ok' && isBad) {
        // Registrar Incidente
        setIncidentLog(prev => [{
            type: 'issue',
            isOutage: isOutage,
            time: point.time,
            value: point.latency,
            id: Date.now()
        }, ...prev]);
        setNetworkStatus('issue');
    } else if (networkStatus === 'issue' && !isBad) {
        // Registrar Recuperación
        setIncidentLog(prev => [{
            type: 'recovery',
            time: point.time,
            value: point.latency,
            id: Date.now()
        }, ...prev]);
        setNetworkStatus('ok');
    }
  };

  const clearGeoTrace = () => {
    setGeoHost('');
    setGeoResults(null);
    setIsTracing(false);
  };

  const value = {
    latencyHistory,
    setLatencyHistory,
    addLatencyPoint,
    geoHost,
    setGeoHost,
    geoResults, 
    setGeoResults,
    isTracing,
    setIsTracing,
    clearGeoTrace,
    // Nuevos exportados
    incidentLog,
    clearIncidentLog: () => setIncidentLog([])
  };

  return (
    <NetworkContext.Provider value={value}>
      {children}
    </NetworkContext.Provider>
  );
}
