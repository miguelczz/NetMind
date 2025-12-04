# 🚀 Optimizaciones de Tiempo de Respuesta - NetMind

Este documento detalla todas las técnicas de optimización implementadas en el proyecto NetMind para reducir los tiempos de respuesta y mejorar la experiencia del usuario.

---

## 📋 Tabla de Contenidos

1. [Streaming de Respuestas (SSE)](#1-streaming-de-respuestas-sse)
2. [Pool de Conexiones de Base de Datos](#2-pool-de-conexiones-de-base-de-datos)
3. [Procesamiento Asíncrono](#3-procesamiento-asíncrono)
4. [Búsqueda Híbrida Paralela](#4-búsqueda-híbrida-paralela)
5. [Caché con Redis](#5-caché-con-redis)
6. [Pre-compilación de Prompts](#6-pre-compilación-de-prompts)
7. [Validación y Análisis en Paralelo](#7-validación-y-análisis-en-paralelo)
8. [Optimizaciones de Configuración](#8-optimizaciones-de-configuración)

---

## 1. Streaming de Respuestas (SSE)

### 📍 Ubicación
- **Archivo**: `backend/src/api/streaming.py`

### 🎯 Objetivo
Enviar tokens de respuesta al usuario de forma incremental mientras se generan, en lugar de esperar a que se complete toda la respuesta.

### 💡 Implementación

```20:122:backend/src/api/streaming.py
async def stream_graph_execution(
    initial_state: GraphState,
    session_id: str
) -> AsyncIterator[str]:
    """
    Ejecuta el grafo y stream los resultados usando SSE.
    OPTIMIZACIÓN: Usa astream_events para capturar tokens del LLM en tiempo real.
    """
    try:
        # OPTIMIZACIÓN: Usar astream_events para capturar eventos en tiempo real
        # Esto permite capturar tokens del LLM mientras se generan
        async for event in graph.astream_events(initial_state, version="v2"):
            event_type = event.get("event")
            event_name = event.get("name", "")
            
            # Capturar tokens del LLM en tiempo real (OPTIMIZACIÓN CRÍTICA)
            if event_type == "on_chat_model_stream":
                chunk = event.get("data", {}).get("chunk")
                if chunk and hasattr(chunk, "content") and chunk.content:
                    token_data = {
                        "type": "token",
                        "data": {
                            "content": chunk.content
                        }
                    }
                    yield f"data: {json.dumps(token_data)}\n\n"
```

### 🔑 Características Clave

1. **Server-Sent Events (SSE)**: Formato estándar para streaming de datos
2. **Captura de tokens en tiempo real**: Usa `astream_events` de LangGraph para capturar tokens mientras se generan
3. **Headers optimizados**:
   - `Cache-Control: no-cache`: Evita que proxies cacheen la respuesta
   - `Connection: keep-alive`: Mantiene la conexión abierta
   - `X-Accel-Buffering: no`: Desactiva buffering en nginx para envío inmediato
4. **Actualizaciones de estado**: Envía actualizaciones sobre el progreso del grafo (nodos ejecutados, herramientas usadas)

### 📊 Beneficios

- **Time to First Token (TTFT)**: El usuario ve la respuesta casi inmediatamente
- **Percepción de velocidad**: La respuesta se siente más rápida aunque el tiempo total sea el mismo
- **Mejor UX**: El usuario no ve una pantalla en blanco esperando
- **Transparencia**: El usuario puede ver qué nodos del grafo se están ejecutando

### 🔧 Uso

```bash
curl -X POST "http://localhost:8000/agent/query/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "mi-sesion",
    "messages": [{
      "role": "user",
      "content": "¿Qué es un ping?"
    }]
  }'
```

---

## 2. Pool de Conexiones de Base de Datos

### 📍 Ubicación
- **Archivo**: `backend/src/models/database.py` (líneas 64-73)

### 🎯 Objetivo
Reutilizar conexiones de base de datos en lugar de crear nuevas para cada solicitud, reduciendo la sobrecarga de establecer conexiones.

### 💡 Implementación

```64:73:backend/src/models/database.py
# Crear engine de SQLAlchemy con pool optimizado
# OPTIMIZACIÓN: Configurar pool de conexiones para mejor rendimiento
engine = create_engine(
    settings.sqlalchemy_url,
    pool_pre_ping=True,  # Verifica conexiones antes de usarlas
    pool_size=10,  # Número de conexiones a mantener en el pool
    max_overflow=20,  # Máximo de conexiones adicionales que se pueden crear
    pool_recycle=3600,  # Reciclar conexiones después de 1 hora
    echo=False  # Cambiar a True para ver queries SQL en desarrollo
)
```

### 🔑 Características Clave

1. **Pool de conexiones**: SQLAlchemy mantiene un conjunto de conexiones reutilizables
2. **Configuración**:
   - `pool_size=10`: Número de conexiones a mantener en el pool
   - `max_overflow=20`: Máximo de conexiones adicionales que se pueden crear bajo carga
   - `pool_pre_ping=True`: Verifica conexiones antes de usarlas (detecta conexiones cerradas)
   - `pool_recycle=3600`: Recicla conexiones después de 1 hora para evitar timeouts
3. **Gestión automática**: Las conexiones se adquieren y liberan automáticamente mediante el dependency `get_db()`

### 📊 Beneficios

- **Reducción de latencia**: Evita el tiempo de establecer nuevas conexiones (típicamente 50-200ms)
- **Mejor escalabilidad**: Maneja múltiples solicitudes concurrentes eficientemente
- **Menor carga en BD**: Reutiliza conexiones existentes
- **Detección de conexiones muertas**: `pool_pre_ping` detecta y reemplaza conexiones cerradas automáticamente

### 🔧 Configuración

El pool se configura automáticamente al importar el módulo. Para ajustar los valores:

```python
# En backend/src/models/database.py
engine = create_engine(
    settings.sqlalchemy_url,
    pool_size=15,      # Aumentar para más concurrencia
    max_overflow=30,   # Aumentar para picos de carga
    pool_recycle=3600  # Ajustar según timeout de BD
)
```

---

## 3. Procesamiento Asíncrono

### 📍 Ubicación
- Todo el proyecto usa `async/await` consistentemente
- Endpoints FastAPI son asíncronos
- Operaciones de I/O usan `asyncio`

### 🎯 Objetivo
Permitir que múltiples operaciones I/O (base de datos, APIs externas, etc.) se ejecuten concurrentemente en lugar de secuencialmente.

### 💡 Ejemplo de Implementación

```python
# backend/src/api/agent.py
@router.post("/query")
async def agent_query(
    query: AgentQuery,
    session_manager: SessionManager = Depends(get_session_manager)
):
    """
    Endpoint asíncrono que procesa consultas del agente.
    """
    # Operaciones asíncronas no bloquean el event loop
    session_state = session_manager.get_session(query.session_id, query.user_id)
    initial_state = GraphState(messages=graph_messages)
    final_state = await graph.ainvoke(initial_state)  # No bloquea otras solicitudes
    return response
```

### 📊 Beneficios

- **Concurrencia**: Múltiples solicitudes pueden procesarse simultáneamente
- **No bloquea**: Mientras espera I/O, puede procesar otras solicitudes
- **Mejor utilización de recursos**: Aprovecha mejor el CPU y la red
- **Escalabilidad**: Puede manejar miles de solicitudes concurrentes

### 🔧 Principios Aplicados

```python
# ❌ Evitar (síncrono)
def process_data():
    result1 = db.query()  # Bloquea
    result2 = api.call()   # Bloquea
    return combine(result1, result2)

# ✅ Preferir (asíncrono)
async def process_data():
    result1 = await db.query()  # No bloquea, permite otras operaciones
    result2 = await api.call()  # No bloquea
    return combine(result1, result2)
```

---

## 4. Búsqueda Híbrida Paralela

### 📍 Ubicación
- **Archivo**: `backend/src/tools/rag_tool.py` (líneas 320-368)

### 🎯 Objetivo
Ejecutar búsquedas densas (vectoriales) y dispersas (por palabras clave) simultáneamente en lugar de secuencialmente.

### 💡 Implementación

```320:368:backend/src/tools/rag_tool.py
    async def _execute_query(self, query_text: str, top_k: int = 8, conversation_context: Optional[str] = None):
        """
        Método interno que ejecuta la consulta RAG real.
        OPTIMIZACIÓN: Búsqueda híbrida paralela (densa + dispersa) usando asyncio.gather().
        """
        # OPTIMIZACIÓN: Extraer keywords antes de las búsquedas
        keywords = self._extract_keywords(query_text)
        
        # OPTIMIZACIÓN: Ejecutar búsqueda densa y dispersa en paralelo usando asyncio.gather()
        # Esto es más eficiente que ThreadPoolExecutor para operaciones I/O
        tasks = [self._dense_search(query_text, top_k)]
        
        # Agregar búsqueda dispersa solo si hay keywords
        if keywords:
            tasks.append(self._sparse_search(keywords))
        
        # Ejecutar ambas búsquedas en paralelo
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Procesar resultados
        hits = results[0] if not isinstance(results[0], Exception) else []
        keyword_hits = results[1] if len(results) > 1 and not isinstance(results[1], Exception) else []
```

### 🔑 Características Clave

1. **`asyncio.gather()`**: Ejecuta ambas búsquedas en paralelo
2. **Independencia**: Las búsquedas densa y dispersa no dependen una de otra
3. **Reducción de tiempo**: El tiempo total es el máximo de ambas, no la suma
4. **Manejo de errores**: `return_exceptions=True` permite que una búsqueda falle sin afectar la otra

### 📊 Beneficios

- **Reducción de latencia**: Si cada búsqueda toma 100ms, en paralelo toma ~100ms en lugar de 200ms
- **Mejor rendimiento**: Aprovecha mejor los recursos del servidor de búsqueda (Qdrant)
- **Resiliencia**: Si una búsqueda falla, la otra puede seguir funcionando

### 🔧 Cómo Funciona

```python
import asyncio

# ❌ Evitar (secuencial)
async def search_sequential():
    dense_results = await dense_search(query)    # 100ms
    sparse_results = await sparse_search(query)   # 100ms
    # Total: 200ms

# ✅ Preferir (paralelo)
async def search_parallel():
    dense_results, sparse_results = await asyncio.gather(
        dense_search(query),   # 100ms
        sparse_search(query)   # 100ms
    )
    # Total: ~100ms (el máximo de ambas)
```

---

## 5. Caché con Redis

### 📍 Ubicación
- **Archivo**: `backend/src/core/cache.py`
- **Uso**: Decorador `@cache_result` en múltiples herramientas

### 🎯 Objetivo
Almacenar datos frecuentemente accedidos (resultados RAG, operaciones de red, etc.) en memoria para acceso rápido.

### 💡 Implementación

```215:263:backend/src/core/cache.py
def cache_result(prefix: str, ttl: int = 3600):
    """
    Decorador para cachear resultados de funciones.
    
    Args:
        prefix: Prefijo para las claves de cache
        ttl: Tiempo de vida en segundos
    
    Ejemplo:
        @cache_result("rag", ttl=3600)
        def query(text: str):
            # ... lógica ...
            return result
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_manager = get_cache_manager()
            
            # Si el cache está deshabilitado, ejecutar función directamente
            if not cache_manager.enabled:
                return func(*args, **kwargs)
            
            # Generar clave de cache única basada en argumentos
            cache_key = cache_manager.get_cache_key(prefix, *cache_args, **kwargs)
            
            # Intentar obtener del cache
            cached = cache_manager.get(cache_key)
            if cached is not None:
                logger.info(f"Cache HIT: {prefix}")
                return cached
            
            # Cache miss: ejecutar función y almacenar resultado
            result = func(*args, **kwargs)
            
            # Almacenar en cache (solo si no hay error)
            if result and not (isinstance(result, dict) and result.get("error")):
                cache_manager.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator
```

### 🔑 Características Clave

1. **Almacenamiento en memoria**: Acceso ultra-rápido (< 1ms)
2. **Serialización JSON**: Maneja objetos complejos automáticamente
3. **Manejo de errores robusto**: Fallback graceful si Redis no está disponible
4. **TTL configurable**: Cada función puede tener su propio tiempo de vida
5. **Claves únicas**: Hash MD5 de argumentos para evitar colisiones

### 📊 Uso en el Proyecto

```python
# RAG Tool - Cache por 1 hora
@cache_result("rag", ttl=3600)
def query(self, query_text: str, ...):
    # ...

# IP Tool - Cache por 5 minutos (operaciones de red cambian frecuentemente)
@cache_result("ip_ping", ttl=300)
def ping(self, host: str, ...):
    # ...

# IP Tool - Cache por 10 minutos (traceroute)
@cache_result("ip_traceroute", ttl=600)
def tracert(self, host: str, ...):
    # ...
```

### 📊 Beneficios

- **Acceso rápido**: Redis típicamente responde en < 1ms vs 10-50ms de BD
- **Reducción de carga**: Menos consultas a Qdrant y menos llamadas a APIs externas
- **Mejor escalabilidad**: Puede manejar miles de lecturas por segundo
- **Ahorro de costos**: Reduce llamadas a OpenAI API para consultas repetidas

---

## 6. Pre-compilación de Prompts

### 📍 Ubicación
- **Archivo**: `backend/src/tools/rag_tool.py` (líneas 34-100)

### 🎯 Objetivo
Definir prompts como constantes de clase en lugar de construirlos en cada llamada, reduciendo overhead de procesamiento.

### 💡 Implementación

```34:100:backend/src/tools/rag_tool.py
class RAGTool:
    """
    Herramienta RAG optimizada con búsqueda híbrida paralela usando asyncio.gather().
    """
    
    # OPTIMIZACIÓN: Pre-compilar prompts estáticos para evitar reconstruirlos en cada llamada
    RELEVANCE_CHECK_PROMPT_TEMPLATE = """
Analiza si la siguiente pregunta está relacionada EXCLUSIVAMENTE con la temática de redes, telecomunicaciones, protocolos de red, tecnologías de red, o temas técnicos de TI relacionados con redes.

Pregunta del usuario: "{query_text}"

INSTRUCCIONES CRÍTICAS:
- Sé MUY ESTRICTO: solo marca como relevante si la pregunta está CLARAMENTE y DIRECTAMENTE relacionada con redes, protocolos de red, telecomunicaciones o tecnologías de red
...
"""
    
    COMPLEXITY_PROMPT_TEMPLATE = """
Analiza la siguiente pregunta y determina su complejidad:
...
"""
    
    BASE_PROMPT_TEMPLATE = """
Eres un asistente experto en redes y telecomunicaciones. Responde la pregunta del usuario de manera clara, natural y adaptada a su complejidad.
...
"""
```

### 🔑 Características Clave

1. **Constantes de clase**: Los prompts se definen una vez como atributos de clase
2. **Formateo simple**: Solo se reemplazan variables específicas cuando se necesitan
3. **Sin overhead**: No se reconstruyen strings en cada llamada

### 📊 Beneficios

- **Reducción de latencia**: Evita el tiempo de construir strings largos (~5-10ms)
- **Menor uso de CPU**: No necesita procesar templates repetidamente
- **Menor uso de memoria**: Los prompts se comparten entre todas las instancias

### 🔧 Comparación

```python
# ❌ Evitar (construcción en cada uso)
def process_query(query):
    prompt = f"""
    Eres un asistente experto...
    Pregunta: {query}
    ...
    """  # Construye el string cada vez
    return llm.generate(prompt)

# ✅ Preferir (pre-compilación)
class QueryProcessor:
    PROMPT_TEMPLATE = """
    Eres un asistente experto...
    Pregunta: {query}
    ...
    """  # Definido una vez
    
    def process_query(self, query):
        prompt = self.PROMPT_TEMPLATE.format(query=query)  # Solo formatea
        return llm.generate(prompt)
```

---

## 7. Validación y Análisis en Paralelo

### 📍 Ubicación
- **Archivo**: `backend/src/tools/rag_tool.py` (líneas 395-479)

### 🎯 Objetivo
Ejecutar validación de relevancia temática y análisis de complejidad simultáneamente en lugar de secuencialmente.

### 💡 Implementación

```395:479:backend/src/tools/rag_tool.py
        # OPTIMIZACIÓN: Validar relevancia y analizar complejidad en paralelo usando asyncio.gather()
        # IMPORTANTE: La validación de relevancia debe considerar el contexto de conversación
        async def check_relevance():
            """Verifica si la pregunta es relevante para la temática."""
            # ... lógica de validación ...
        
        async def analyze_complexity():
            """Analiza la complejidad de la pregunta."""
            # ... lógica de análisis ...
        
        # OPTIMIZACIÓN: Ejecutar validación de relevancia y complejidad en paralelo usando asyncio.gather()
        is_relevant, complexity = await asyncio.gather(
            check_relevance(),
            analyze_complexity(),
            return_exceptions=True
        )
```

### 🔑 Características Clave

1. **Ejecución paralela**: Ambas operaciones se ejecutan simultáneamente
2. **Independencia**: La validación y el análisis no dependen una de otra
3. **Manejo de errores**: `return_exceptions=True` permite que una falle sin afectar la otra

### 📊 Beneficios

- **Reducción de latencia**: Si cada operación toma 200ms, en paralelo toma ~200ms en lugar de 400ms
- **Mejor utilización de recursos**: Aprovecha mejor las llamadas a la API de OpenAI
- **Respuestas más rápidas**: El usuario recibe la respuesta más rápido

---

## 8. Optimizaciones de Configuración

### 📍 Ubicación
- **Archivo**: `backend/src/models/database.py` (pool de conexiones)
- **Archivo**: `backend/src/core/cache.py` (configuración Redis)
- **Archivo**: `backend/src/tools/rag_tool.py` (configuración OpenAI client)

### 🎯 Objetivo
Ajustar configuraciones del sistema para mejor rendimiento.

### 💡 Implementaciones

#### Pool de Conexiones PostgreSQL

```64:73:backend/src/models/database.py
engine = create_engine(
    settings.sqlalchemy_url,
    pool_pre_ping=True,  # Verifica conexiones antes de usarlas
    pool_size=10,  # Número de conexiones a mantener en el pool
    max_overflow=20,  # Máximo de conexiones adicionales que se pueden crear
    pool_recycle=3600,  # Reciclar conexiones después de 1 hora
    echo=False
)
```

#### Cliente OpenAI con Retries Limitados

```19:22:backend/src/tools/rag_tool.py
client = OpenAI(
    api_key=settings.openai_api_key,
    max_retries=2  # Limitar retries para reducir tiempo de bloqueo
)
```

#### Configuración Redis

```58:63:backend/src/core/cache.py
_redis_client = redis.from_url(
    settings.redis_url,
    decode_responses=True,
    socket_connect_timeout=2,  # Timeout corto para conexión
    socket_timeout=2  # Timeout corto para operaciones
)
```

### 🔑 Consideraciones

1. **Balance**: Más conexiones permiten más concurrencia pero consumen más recursos
2. **Ajuste según carga**: Monitorear y ajustar según el uso real
3. **Timeouts**: Configurar timeouts apropiados para evitar bloqueos
4. **Retries**: Limitar retries para evitar latencia excesiva

### 📊 Beneficios

- **Mejor manejo de carga**: Más conexiones permiten más solicitudes concurrentes
- **Prevención de cuellos de botella**: Evita que las solicitudes esperen por conexiones
- **Resiliencia**: Timeouts y retries limitados previenen bloqueos prolongados

---

## 📊 Resumen de Impacto

| Optimización | Reducción de Latencia Estimada | Complejidad de Implementación | Estado |
|-------------|--------------------------------|-------------------------------|--------|
| Streaming (SSE) | 50-90% (percepción) | Media | ✅ Implementado |
| Pool de Conexiones | 50-200ms por request | Baja | ✅ Implementado |
| Procesamiento Asíncrono | 30-70% en operaciones I/O | Media | ✅ Implementado |
| Búsqueda Híbrida Paralela | 50% (de 200ms a 100ms) | Baja | ✅ Implementado |
| Caché Redis | 90-95% (de 50ms a <1ms) | Media | ✅ Implementado |
| Pre-compilación de Prompts | 5-10ms por request | Baja | ✅ Implementado |
| Validación y Análisis Paralelo | 50% (de 400ms a 200ms) | Baja | ✅ Implementado |
| Optimizaciones de Configuración | Variable | Baja | ✅ Implementado |

---

## 🎯 Optimizaciones Implementadas

### ✅ Todas las Optimizaciones Principales

1. ✅ **Streaming (SSE)**: Implementado en `backend/src/api/streaming.py`
2. ✅ **Pool de Conexiones**: Implementado en `backend/src/models/database.py`
3. ✅ **Procesamiento Asíncrono**: Todo el proyecto usa `async/await`
4. ✅ **Búsqueda Híbrida Paralela**: Implementado en `backend/src/tools/rag_tool.py`
5. ✅ **Caché Redis**: Implementado en `backend/src/core/cache.py` con decorador `@cache_result`
6. ✅ **Pre-compilación de Prompts**: Implementado en `backend/src/tools/rag_tool.py`
7. ✅ **Validación y Análisis Paralelo**: Implementado en `backend/src/tools/rag_tool.py`
8. ✅ **Optimizaciones de Configuración**: Pool de conexiones, timeouts, retries limitados

---

## 🔍 Métricas para Monitorear

Para validar las optimizaciones en el proyecto:

1. **Time to First Token (TTFT)**: Tiempo hasta el primer token en streaming
2. **Time to Last Token (TTLT)**: Tiempo total de generación
3. **Latencia de BD**: Tiempo promedio de queries a PostgreSQL
4. **Hit Rate de Caché**: Porcentaje de hits en Redis
5. **Concurrencia**: Número de solicitudes simultáneas manejadas
6. **Throughput**: Solicitudes por segundo
7. **Latencia de Búsqueda**: Tiempo promedio de búsquedas en Qdrant

---

## 📚 Referencias en el Código

- **Streaming**: `backend/src/api/streaming.py`
- **Pool de Conexiones**: `backend/src/models/database.py:64-73`
- **Búsqueda Híbrida**: `backend/src/tools/rag_tool.py:320-368`
- **Caché Redis**: `backend/src/core/cache.py`
- **Pre-compilación de Prompts**: `backend/src/tools/rag_tool.py:34-100`
- **Validación Paralela**: `backend/src/tools/rag_tool.py:395-479`

---

## 🔧 Configuración de TTLs de Caché

Los TTLs (Time To Live) configurados en el proyecto:

- **RAG queries**: 3600 segundos (1 hora) - Consultas conceptuales cambian poco
- **Conversation context**: 1800 segundos (30 minutos) - Contexto de conversación
- **IP ping**: 300 segundos (5 minutos) - Operaciones de red cambian frecuentemente
- **IP traceroute**: 600 segundos (10 minutos) - Rutas de red son más estables
- **IP comparison**: 600 segundos (10 minutos) - Comparaciones de IPs

Estos valores pueden ajustarse según las necesidades del proyecto.

---

**Última actualización**: Basado en análisis del proyecto NetMind v1.0.0
