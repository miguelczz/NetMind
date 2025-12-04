"""
Módulo para streaming de respuestas usando Server-Sent Events (SSE)
"""
import json
import logging
from typing import AsyncIterator, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage, AIMessage
from ..models.schemas import Message, AgentQuery
from ..core.state_manager import SessionManager, get_session_manager
from ..core.graph_state import GraphState
from ..agent.agent_graph import graph
from ..settings import settings

router = APIRouter(prefix="/agent", tags=["agent"])
logger = logging.getLogger(__name__)


async def stream_graph_execution(
    initial_state: GraphState,
    session_id: str
) -> AsyncIterator[str]:
    """
    Ejecuta el grafo y stream los resultados usando SSE.
    OPTIMIZACIÓN: Usa astream_events para capturar tokens del LLM en tiempo real.
    
    Args:
        initial_state: Estado inicial del grafo
        session_id: ID de sesión para logging
    
    Yields:
        Chunks de datos en formato SSE
    """
    try:
        final_state = None
        last_node = None
        
        # OPTIMIZACIÓN: Usar astream_events para capturar eventos en tiempo real
        # Esto permite capturar tokens del LLM mientras se generan
        async for event in graph.astream_events(initial_state, version="v2"):
            event_type = event.get("event")
            event_name = event.get("name", "")
            
            # Capturar actualizaciones de nodos
            if event_type == "on_chain_start" or event_type == "on_chain_end":
                node_name = event_name.split(".")[-1] if "." in event_name else event_name
                if node_name != last_node:
                    last_node = node_name
                    chunk_data = {
                        "type": "node_update",
                        "data": {
                            "node": node_name,
                            "status": "started" if event_type == "on_chain_start" else "completed"
                        }
                    }
                    yield f"data: {json.dumps(chunk_data)}\n\n"
            
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
            
            # Capturar actualizaciones de estado
            if event_type == "on_chain_end" and "data" in event:
                state_updates = event.get("data", {}).get("output", {})
                if state_updates:
                    chunk_data = {
                        "type": "state_update",
                        "data": {
                            "plan_steps": state_updates.get("plan_steps", []),
                            "executed_tools": state_updates.get("executed_tools", []),
                            "executed_steps": state_updates.get("executed_steps", []),
                        }
                    }
                    yield f"data: {json.dumps(chunk_data)}\n\n"
        
        # Obtener estado final después del streaming
        final_state = await graph.ainvoke(initial_state)
        
        # Enviar respuesta final completa (por si acaso no se capturaron todos los tokens)
        supervised_output = final_state.get('supervised_output')
        final_output = final_state.get('final_output')
        assistant_response = supervised_output or final_output or "No se pudo generar una respuesta."
        
        # Solo enviar respuesta final si no se envió completamente por streaming
        response_data = {
            "type": "final_response",
            "data": {
                "content": assistant_response,
                "executed_tools": final_state.get('executed_tools', []),
                "executed_steps": final_state.get('executed_steps', []),
                "thought_chain": final_state.get('thought_chain', []) if settings.show_thought_chain else None,
            }
        }
        yield f"data: {json.dumps(response_data)}\n\n"
        
        # Señal de finalización
        yield f"data: {json.dumps({'type': 'done'})}\n\n"
        
    except Exception as e:
        logger.error(f"Error en streaming para sesión {session_id}: {str(e)}", exc_info=True)
        error_data = {
            "type": "error",
            "data": {
                "message": str(e),
                "type": type(e).__name__,
            }
        }
        if settings.debug:
            import traceback
            error_data["data"]["traceback"] = traceback.format_exc()
        
        yield f"data: {json.dumps(error_data)}\n\n"


@router.post("/query/stream")
async def agent_query_stream(
    query: AgentQuery,
    session_manager: SessionManager = Depends(get_session_manager)
):
    """
    Endpoint para consultas con streaming de respuestas usando Server-Sent Events.
    
    La respuesta se envía en tiempo real a medida que el agente procesa la consulta.
    """
    try:
        # Validación: verificar que haya mensajes
        if not query.messages:
            raise HTTPException(status_code=400, detail="La lista de mensajes no puede estar vacía")
        
        # Validación: verificar que haya al menos un mensaje del usuario
        user_messages = [m for m in query.messages if m.role == "user"]
        if not user_messages:
            raise HTTPException(status_code=400, detail="Debe haber al menos un mensaje con role='user'")
        
        # Obtener o crear sesión (persistencia de estado)
        session_state = session_manager.get_session(query.session_id, query.user_id)
        
        # Extraer último mensaje del usuario
        user_message = user_messages[-1].content
        if not user_message or not user_message.strip():
            raise HTTPException(status_code=400, detail="El último mensaje del usuario no puede estar vacío")

        # Agregar el nuevo mensaje del usuario al contexto de la sesión
        last_user_msg_in_state = None
        if session_state.context_window:
            for msg in reversed(session_state.context_window):
                if msg.role == "user":
                    last_user_msg_in_state = msg.content
                    break
        
        # Solo agregar si es un mensaje nuevo
        if last_user_msg_in_state != user_message:
            session_state.add_message("user", user_message)
        
        # Actualizar user_id si se proporciona
        if query.user_id:
            session_state.user_id = query.user_id

        # Convertir mensajes de AgentState a mensajes de LangChain para el grafo
        graph_messages = []
        for msg in session_state.context_window:
            if msg.role == "user":
                graph_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                graph_messages.append(AIMessage(content=msg.content))

        # Crear estado inicial del grafo
        initial_state = GraphState(
            messages=graph_messages
        )

        # Crear respuesta de streaming
        return StreamingResponse(
            stream_graph_execution(initial_state, query.session_id),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # Deshabilitar buffering en nginx
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en agent_query_stream: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

