# Solución de Problemas - Streaming y Contexto

## 🔧 Cambios Realizados

### 1. Streaming Visual Mejorado

**Archivo:** `backend/src/api/streaming.py`

**Cambios:**
- ✅ Reducido `chunk_size` de 15 a **5 caracteres** (más fluido)
- ✅ Aumentado delay de 20ms a **50ms** (más visible)
- ✅ Implementado pseudo-streaming dividiendo la respuesta final

**Resultado esperado:**
- Deberías ver el texto aparecer palabra por palabra (aproximadamente 20 caracteres por segundo)
- El efecto visual es similar a ChatGPT

---

## 🧪 Cómo Probar el Streaming

### Paso 1: Reiniciar el Backend

```bash
# Detener el backend actual (Ctrl+C)
# Luego reiniciar:
cd backend
python -m uvicorn main:app --reload
```

### Paso 2: Reiniciar el Frontend

```bash
# Detener el frontend actual (Ctrl+C)
# Luego reiniciar:
cd frontend
npm run dev
```

### Paso 3: Probar con una Pregunta Simple

```
¿Qué es TCP/IP?
```

**Resultado esperado:**
- Deberías ver una burbuja vacía aparecer inmediatamente
- El texto debería ir apareciendo palabra por palabra
- Velocidad: aproximadamente 20 caracteres por segundo

### Paso 4: Verificar en la Consola del Navegador

Abre las DevTools (F12) y ve a la pestaña "Console". Deberías ver logs como:

```
Recibiendo chunk SSE: {type: "token", data: {content: "El pr"}}
Recibiendo chunk SSE: {type: "token", data: {content: "otoco"}}
Recibiendo chunk SSE: {type: "token", data: {content: "lo TC"}}
...
```

---

## 🐛 Problema del Contexto Incorrecto

### Diagnóstico

El problema que reportaste:
- **Esperado:** Latencia promedio de 77.29 ms
- **Obtenido:** Latencia promedio de 30 ms

**Causa raíz:** El LLM está extrayendo incorrectamente los datos numéricos del contexto de conversación.

### Solución

El código ya tiene lógica para usar el contexto de conversación (líneas 588-605 en `tool_executors.py`), pero el prompt necesita ser más específico para extraer datos numéricos exactos.

**Archivo a modificar:** `backend/src/agent/tool_executors.py`

**Línea 588-605:** Modificar el prompt para ser más estricto con datos numéricos:

```python
followup_prompt = f"""
Basándote en la siguiente conversación previa, responde la pregunta del usuario de forma DIRECTA y PRECISA.

IMPORTANTE:
- Si la pregunta es sobre DATOS NUMÉRICOS (latencia, tiempo, porcentaje, etc.), extrae los valores EXACTOS del contexto
- NO inventes ni aproximes números - usa SOLO los valores que aparecen en el contexto
- Si hay múltiples valores, usa el más reciente o el más relevante según la pregunta
- Sé CONCISO: ve directo al punto

Conversación previa:
{context}

Pregunta del usuario: {user_prompt}

Respuesta (directa, precisa, con valores exactos del contexto):
"""
```

---

## 🔍 Debugging Paso a Paso

### Si el Streaming NO Funciona

1. **Verificar que el backend esté usando el endpoint correcto:**
   - Abre DevTools → Network
   - Envía un mensaje
   - Busca la petición a `/agent/query/stream`
   - Debería ser tipo "eventsource" o "fetch"

2. **Verificar que los chunks lleguen al frontend:**
   - Abre DevTools → Console
   - Deberías ver logs de chunks recibidos
   - Si no ves logs, el problema está en el frontend

3. **Verificar que el backend esté enviando chunks:**
   - Revisa los logs del backend
   - Deberías ver: `[Streaming] Respuesta guardada en contexto de ventana`

### Si el Contexto Está Mal

1. **Verificar que el contexto se esté guardando:**
   - Envía un mensaje
   - Revisa los logs del backend
   - Deberías ver: `[Streaming] Respuesta guardada en contexto de ventana para sesión XXX`

2. **Verificar que el contexto se esté usando:**
   - Envía una pregunta de seguimiento
   - Revisa los logs del backend
   - Deberías ver: `[RAG] Detectado seguimiento de conversación - usando contexto de conversación`

3. **Verificar el contenido del contexto:**
   - Agrega un log temporal en `tool_executors.py` línea 599:
   ```python
   logger.info(f"[DEBUG] Contexto usado: {context[:500]}")  # Primeros 500 chars
   ```
   - Verifica que el contexto contenga los datos correctos del ping anterior

---

## 🎯 Solución Rápida para el Contexto

Si quieres una solución inmediata para el problema del contexto, puedes hacer lo siguiente:

### Opción 1: Mejorar el Prompt (Recomendado)

Modifica el prompt en `tool_executors.py` línea 588 como se indicó arriba.

### Opción 2: Aumentar el Contexto

Aumenta el número de mensajes en el contexto:

```python
# Línea 582
context_text = get_conversation_context(messages, max_messages=15)  # Era 10
```

### Opción 3: Agregar Validación de Datos Numéricos

Agrega validación para asegurar que los datos numéricos se extraigan correctamente:

```python
# Después de generar la respuesta (línea 605)
answer = generate_from_context(context_text, prompt)

# Validar que los números en la respuesta coincidan con los del contexto
import re
numbers_in_context = re.findall(r'\d+\.?\d*\s*ms', context_text)
numbers_in_answer = re.findall(r'\d+\.?\d*\s*ms', answer)

if numbers_in_context and not numbers_in_answer:
    logger.warning(f"[RAG] Respuesta no contiene datos numéricos del contexto")
    # Regenerar con prompt más específico
```

---

## 📊 Métricas de Éxito

### Streaming Funcionando Correctamente
- ✅ Texto aparece palabra por palabra
- ✅ Velocidad visible pero no molesta (~20 chars/seg)
- ✅ Solo UNA burbuja de respuesta
- ✅ No hay duplicados

### Contexto Funcionando Correctamente
- ✅ Pregunta de seguimiento usa datos del mensaje anterior
- ✅ Datos numéricos son exactos (no aproximados)
- ✅ El agente "recuerda" acciones previas (pings, consultas DNS, etc.)

---

## 🚀 Próximos Pasos

1. **Probar el streaming** con los nuevos parámetros (chunk_size=5, delay=50ms)
2. **Verificar el contexto** con una pregunta de seguimiento
3. **Si el contexto sigue mal**, aplicar la solución del prompt mejorado
4. **Reportar resultados** para ajustar si es necesario

---

## 💡 Notas Importantes

- El streaming es **pseudo-streaming** (divide la respuesta final), no streaming real token por token del LLM
- Esto es suficiente para la experiencia de usuario y mucho más simple de implementar
- El streaming real requeriría refactorizar todo el código para usar LangChain LLMs en lugar de llamadas directas a OpenAI
- El contexto ya está implementado, solo necesita ajustes en el prompt para extraer datos numéricos correctamente
