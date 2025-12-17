# Registro de Correcciones de Formato

## Problema Reportado
Las listas con viñetas se mostraban descoordinadas (viñeta en una línea, texto en la siguiente) y con indentación incorrecta.

## Solución Implementada
Se han actualizado los prompts de generación de texto y el formateo de herramientas para imponer reglas estrictas de estructura de listas.

### Archivos Modificados

1.  **`backend/src/tools/ip_tool.py`**
    *   Estandarización de viñetas en comparaciones de IP.
    *   Formato unificado: `• **Host**: Descripción`.

2.  **`backend/src/agent/agent_graph.py`**
    *   Actualización del `synthesis_prompt`.
    *   Regla explícita: "LISTAS LIMPIAS: Cuando uses listas, la viñeta (• o -) debe estar en la MISMA LÍNEA que el texto."

3.  **`backend/src/agent/tool_executors.py`**
    *   Actualización del prompt de seguimiento RAG (`generate_from_context`).
    *   Regla explícita sobre formato de listas.

4.  **`backend/src/tools/rag_tool.py`**
    *   Actualización del `BASE_PROMPT_TEMPLATE`.
    *   Instrucciones visuales sobre lo que es correcto e incorrecto en el uso de viñetas.

## Resultado Esperado
*   Todas las respuestas generadas (RAG, análisis, comparaciones) tendrán viñetas alineadas con el texto.
*   No habrá saltos de línea incorrectos después de un marcador de lista.
*   La lectura será más fluida y profesional.
