# Lista de Construcción del Proyecto NetMind

Esta guía describe paso a paso cómo construir el proyecto NetMind desde cero. Cada paso incluye una descripción breve de qué hacer.

---

## 📋 Fase 1: Configuración Inicial del Entorno

### 1.1 Crear Estructura de Directorios
**Descripción**: Crear la estructura básica de carpetas del proyecto (backend/, frontend/, etc.)

### 1.2 Configurar Entorno Virtual Python
**Descripción**: Crear y activar un entorno virtual de Python para aislar dependencias

### 1.3 Instalar Dependencias Backend
**Descripción**: Instalar todas las librerías necesarias desde `requirements.txt` (FastAPI, LangChain, OpenAI, etc.)

### 1.4 Crear Docker Compose
**Descripción**: Crear `docker-compose.dev.yml` en la raíz del proyecto con servicios: PostgreSQL, Qdrant, Redis

### 1.5 Configurar Variables de Entorno
**Descripción**: Crear archivo `.env` con API keys, URLs de bases de datos, configuraciones

---

## 📋 Fase 2: Configuración de Bases de Datos

### 2.1 Iniciar Servicios Docker
**Descripción**: Ejecutar `docker-compose -f docker-compose.dev.yml up -d` para levantar PostgreSQL, Qdrant y Redis

### 2.2 Configurar PostgreSQL
**Descripción**: Crear esquema de base de datos mediante un archivo models el cual hace migración de tablas para documentos y sesiones.

### 2.3 Configurar Qdrant
**Descripción**: Crear colección vectorial en Qdrant para almacenar embeddings de documentos

### 2.4 Verificar Conexiones
**Descripción**: Probar conexiones a las tres bases de datos desde Python

---

## 📋 Fase 3: Configuración Core (Settings y Modelos)

### 3.1 Crear Settings
**Descripción**: Implementar `settings.py` con Pydantic Settings para cargar variables de entorno

### 3.2 Definir Schemas Pydantic
**Descripción**: Crear modelos de datos en `schemas.py`: AgentState, Message, AgentQuery, etc.

### 3.3 Definir Modelos de Base de Datos
**Descripción**: Crear modelos SQLAlchemy en `database.py` para tablas de documentos y sesiones

### 3.4 Configurar GraphState
**Descripción**: Implementar `GraphState` en `graph_state.py` con anotaciones de LangGraph (add_messages, LastValue)

---

## 📋 Fase 4: Repositorios y Servicios Base

### 4.1 Implementar QdrantRepository
**Descripción**: Crear clase para interactuar con Qdrant: insertar vectores, buscar por similitud, eliminar

### 4.2 Implementar DocumentRepository
**Descripción**: Crear clase para gestionar documentos en PostgreSQL: crear, leer, eliminar, listar

### 4.3 Implementar SessionRepository
**Descripción**: Crear clase para gestionar sesiones en PostgreSQL/Redis: crear, actualizar, obtener

### 4.4 Implementar EmbeddingsService
**Descripción**: Crear servicio para generar embeddings usando OpenAI API (text-embedding-3-large)

### 4.5 Implementar Utilidades de Texto
**Descripción**: Crear funciones en `text_processing.py`: chunking de documentos, limpieza de texto

---

## 📋 Fase 5: Sistema de Caché

### 5.1 Implementar CacheManager
**Descripción**: Crear clase en `cache.py` para gestionar caché con Redis: get, set, delete, clear

### 5.2 Crear Decorador de Caché
**Descripción**: Implementar decorador `@cache_result` para cachear automáticamente resultados de funciones

### 5.3 Integrar Caché en Herramientas
**Descripción**: Aplicar decorador de caché a RAG tool, IP tool con TTLs apropiados

---

## 📋 Fase 6: Herramientas Especializadas

### 6.1 Implementar RAG Tool
**Descripción**: Crear `rag_tool.py` con búsqueda semántica, búsqueda híbrida, generación de respuestas con contexto

### 6.2 Implementar IP Tool
**Descripción**: Crear `ip_tool.py` con funciones: ping, traceroute, comparación de IPs, validación

### 6.3 Implementar DNS Tool
**Descripción**: Crear `dns_tool.py` con consultas DNS: A, AAAA, MX, TXT, NS, CNAME, PTR, SPF, DMARC

### 6.4 Implementar Formateo de Resultados
**Descripción**: Crear métodos `format_result()` en cada herramienta para presentar resultados de forma legible

---

## 📋 Fase 7: Cliente LLM y Router

### 7.1 Implementar LLMClient
**Descripción**: Crear clase en `llm_client.py` para interactuar con OpenAI API: generate, chat, embeddings

### 7.2 Implementar NetMindAgent (Router)
**Descripción**: Crear clase en `router.py` que decide qué herramienta usar basándose en la pregunta del usuario

### 7.3 Implementar Validación Temática
**Descripción**: Agregar validación en router para rechazar preguntas fuera del tema de redes/telecomunicaciones

### 7.4 Implementar Generación de Planes
**Descripción**: Crear lógica para generar `plan_steps` específicos y ejecutables basados en la consulta

---

## 📋 Fase 8: Ejecutores de Herramientas

### 8.1 Implementar determine_tool_from_step
**Descripción**: Crear función que identifica qué herramienta usar basándose en un paso del plan

### 8.2 Implementar execute_rag_tool
**Descripción**: Crear función que ejecuta RAG tool con contexto de conversación y formatea resultado

### 8.3 Implementar execute_ip_tool
**Descripción**: Crear función que ejecuta IP tool (ping/traceroute/comparación) y formatea resultado

### 8.4 Implementar execute_dns_tool
**Descripción**: Crear función que ejecuta DNS tool según tipo de consulta y formatea resultado

---

## 📋 Fase 9: Grafo LangGraph

### 9.1 Crear Estructura del Grafo
**Descripción**: Inicializar `StateGraph` en `agent_graph.py` con START y END

### 9.2 Implementar Nodo Planner
**Descripción**: Crear función `planner_node` que analiza pregunta y genera plan usando NetMindAgent

### 9.3 Implementar Nodo Orchestrator
**Descripción**: Crear función `orchestrator_node` que decide siguiente componente (Executor o Synthesizer)

### 9.4 Implementar Nodo Executor
**Descripción**: Crear función `ejecutor_agent_node` que ejecuta herramientas según plan_steps

### 9.5 Implementar Nodo Synthesizer
**Descripción**: Crear función `synthesizer_node` que combina resultados de múltiples herramientas

### 9.6 Implementar Nodo Supervisor
**Descripción**: Crear función `supervisor_node` que valida calidad, mejora respuesta y captura para evaluación

### 9.7 Configurar Ruteo Condicional
**Descripción**: Agregar edges condicionales entre nodos basados en estado (plan_steps, results, etc.)

### 9.8 Compilar Grafo
**Descripción**: Compilar grafo con `graph.compile()` y exportar para LangGraph Studio

---

## 📋 Fase 10: Gestión de Estado y Sesiones

### 10.1 Implementar StateManager
**Descripción**: Crear clase en `state_manager.py` para gestionar sesiones en memoria con thread-safety

### 10.2 Implementar RedisSessionManager (Opcional)
**Descripción**: Crear alternativa en `redis_session_manager.py` para persistir sesiones en Redis

### 10.3 Implementar Helpers de Conversión
**Descripción**: Crear funciones para convertir entre AgentState y GraphState, mensajes LangChain

---

## 📋 Fase 11: API REST con FastAPI

### 11.1 Configurar FastAPI App
**Descripción**: Crear `main.py` con FastAPI app, middleware, CORS, routers

### 11.2 Implementar Endpoint de Archivos
**Descripción**: Crear endpoints en `files.py`: upload PDF, listar documentos, eliminar documento

### 11.3 Implementar Procesamiento de PDFs
**Descripción**: Crear lógica para extraer texto de PDFs, chunking, generar embeddings, indexar en Qdrant

### 11.4 Implementar Endpoint de Consultas
**Descripción**: Crear endpoint `/agent/query` en `agent.py` que ejecuta el grafo y retorna respuesta

### 11.5 Implementar Endpoint de Streaming
**Descripción**: Crear endpoint `/agent/query/stream` en `streaming.py` con Server-Sent Events (SSE)

### 11.6 Implementar Manejo de Errores
**Descripción**: Agregar exception handlers, validación de inputs, mensajes de error claros

---

## 📋 Fase 12: Evaluación y Utilidades

### 12.1 Implementar RAGAS Evaluator
**Descripción**: Crear clase en `ragas_evaluator.py` para evaluar calidad de respuestas RAG

### 12.2 Implementar RAGAS Callback
**Descripción**: Crear callback en `ragas_callback.py` para capturar datos durante ejecución del grafo

### 12.3 Integrar Evaluación en Supervisor
**Descripción**: Agregar captura de datos para evaluación RAGAS en supervisor_node

---

## 📋 Fase 13: Frontend (Opcional)

### 13.1 Configurar React + Vite
**Descripción**: Inicializar proyecto React con Vite, instalar dependencias (React Router, Axios, Tailwind)

### 13.2 Crear Componentes de UI
**Descripción**: Crear componentes: ChatContainer, Message, ChatInput, Loading, Button, etc.

### 13.3 Implementar Servicio API
**Descripción**: Crear cliente HTTP en `api.js` para comunicarse con backend FastAPI

### 13.4 Implementar Gestión de Estado
**Descripción**: Crear contextos/hooks para gestionar estado de chat, sesiones, mensajes

### 13.5 Implementar Página de Chat
**Descripción**: Crear página principal con interfaz de chat, streaming de respuestas, historial

### 13.6 Implementar Página de Archivos
**Descripción**: Crear página para subir, listar y eliminar documentos PDF

---

## 📋 Fase 14: Testing y Optimización

### 14.1 Crear Tests Unitarios
**Descripción**: Escribir tests para herramientas, repositorios, utilidades con pytest

### 14.2 Crear Tests de Integración
**Descripción**: Escribir tests para endpoints API, flujo completo del agente

### 14.3 Optimizar Búsqueda RAG
**Descripción**: Implementar búsqueda híbrida paralela, ajustar chunk_size, mejorar prompts

### 14.4 Optimizar Rendimiento
**Descripción**: Profiling, optimizar queries a bases de datos, reducir llamadas a LLM

---

## 📋 Fase 15: Documentación y Deployment

### 15.1 Documentar Código
**Descripción**: Agregar docstrings a todas las funciones y clases

### 15.2 Crear README
**Descripción**: Escribir README.md con descripción, instalación, uso, ejemplos

### 15.3 Crear Documentación Técnica
**Descripción**: Crear docs/ con: Flujo.md, Arquitectura.md, API.md, etc.

### 15.4 Configurar Docker para Producción
**Descripción**: Crear Dockerfile para backend, optimizar imágenes, multi-stage builds

### 15.5 Configurar CI/CD (Opcional)
**Descripción**: Configurar GitHub Actions para tests automáticos, deployment

---

## 🔧 Orden Recomendado de Construcción

### Semana 1: Fundamentos
- Fase 1: Configuración inicial
- Fase 2: Bases de datos
- Fase 3: Core (settings, modelos)

### Semana 2: Infraestructura
- Fase 4: Repositorios y servicios
- Fase 5: Sistema de caché
- Fase 6: Herramientas (RAG, IP, DNS)

### Semana 3: Agente
- Fase 7: Cliente LLM y router
- Fase 8: Ejecutores de herramientas
- Fase 9: Grafo LangGraph

### Semana 4: API y Frontend
- Fase 10: Gestión de estado
- Fase 11: API REST
- Fase 13: Frontend (opcional)

### Semana 5: Pulido
- Fase 12: Evaluación
- Fase 14: Testing y optimización
- Fase 15: Documentación

---

## 📝 Notas Importantes

1. **Dependencias**: Algunas fases dependen de otras (ej: herramientas necesitan repositorios)
2. **Testing incremental**: Probar cada componente después de implementarlo
3. **Configuración**: Asegurar que todas las variables de entorno estén configuradas
4. **Documentación**: Documentar mientras construyes, no al final
5. **Versionado**: Usar Git, hacer commits frecuentes con mensajes claros

---

## 🚀 Comandos Útiles Durante Construcción

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload

# Docker
docker-compose -f docker-compose.dev.yml up -d
docker-compose -f docker-compose.dev.yml logs -f
docker-compose -f docker-compose.dev.yml down

# Testing
pytest tests/ -v
pytest tests/ -v --cov=src

# Frontend
cd frontend
npm install
npm run dev
```

---

¡Buena suerte construyendo NetMind! 🚀

