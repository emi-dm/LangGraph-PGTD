"""
Ejemplo de agente LangGraph con observabilidad usando Langfuse.

Este script demuestra cómo integrar Langfuse con LangGraph para obtener
trazas detalladas de las ejecuciones del agente, incluyendo llamadas al LLM,
uso de herramientas, latencias y costos.

Ejecución:
    uv run ejemplos/8-ejemplo-agente-con-langfuse/src/agente.py

Conceptos demostrados:
- Integración de Langfuse con LangGraph
- CallbackHandler para trazas automáticas
- Observabilidad de llamadas al LLM
- Seguimiento de sesiones y usuarios
- InMemorySaver para memoria en conversación
- Tools: ejecución de código Python y fetch de URLs
- Streaming de tokens en tiempo real
"""

import os
import io
import uuid
import contextlib
import urllib.request

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import END, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import InMemorySaver
from langfuse import get_client
from langfuse.langchain import CallbackHandler

# Cargar variables de entorno
load_dotenv(override=True)


# =============================================================================
# ESTADO
# =============================================================================

class State(MessagesState):
    """Estado del grafo: mensajes."""
    pass


# =============================================================================
# TOOLS
# =============================================================================

@tool
def ejecutar_codigo_python(codigo: str) -> str:
    """Ejecuta código Python y retorna el resultado.

    Args:
        codigo: Código Python a ejecutar.

    Returns:
        Salida estándar del código ejecutado o mensaje de error.
    """
    stdout = io.StringIO()
    stderr = io.StringIO()

    try:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            exec(codigo)
        output = stdout.getvalue()
        error = stderr.getvalue()
        if error:
            return f"⚠️ Advertencias/Errores:\n{error}\n📤 Salida:\n{output}" if output else f"⚠️ Advertencias/Errores:\n{error}"
        return output if output else "✅ Código ejecutado sin salida."
    except Exception as e:
        return f"❌ Error al ejecutar código: {type(e).__name__}: {e}"


@tool
def fetch_url(url: str) -> str:
    """Obtiene el contenido de una URL y retorna una vista previa.

    Args:
        url: URL a la que hacer fetch.

    Returns:
        Contenido de la URL (primeros 2000 caracteres) o mensaje de error.
    """
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (LangGraph Agent)"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode("utf-8", errors="replace")
            # Limitar a 2000 caracteres para no saturar el contexto
            if len(content) > 2000:
                return content[:2000] + f"\n\n... (contenido truncado, total: {len(content)} caracteres)"
            return content
    except Exception as e:
        return f"❌ Error al hacer fetch de {url}: {type(e).__name__}: {e}"


# Lista de herramientas disponibles
tools = [ejecutar_codigo_python, fetch_url]


# =============================================================================
# NODO
# =============================================================================

def agente(state: State) -> dict:
    """Nodo principal del agente. Invoca al LLM y retorna la respuesta."""
    llm = ChatOpenAI(
        base_url="https://openrouter.ai/api/v1",
        model="openai/gpt-4.1-mini",
        api_key=os.getenv("OPENROUTER_API_KEY")
    )

    # Vincular tools al LLM
    llm_con_tools = llm.bind_tools(tools)

    respuesta = llm_con_tools.invoke(state["messages"])
    return {"messages": [respuesta]}


def debe_continuar(state: State) -> str:
    """Determina si el agente debe usar una tool o finalizar."""
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END


# =============================================================================
# GRAFO
# =============================================================================

def crear_graph():
    """Construye y compila el grafo del agente con memoria y tools.

    Returns:
        Grafo compilado con InMemorySaver.
    """
    workflow = StateGraph(state_schema=State)

    # Añadir nodos
    workflow.add_node("agente", agente)
    workflow.add_node("tools", ToolNode(tools))

    # Punto de entrada
    workflow.set_entry_point("agente")

    # Definir flujo: agente -> tools -> agente (hasta que no haya más tools)
    workflow.add_conditional_edges("agente", debe_continuar)
    workflow.add_edge("tools", "agente")

    # Compilar con InMemorySaver para memoria en la conversación
    memoria = InMemorySaver()
    app = workflow.compile(checkpointer=memoria)

    return app


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Función principal que ejecuta el agente con observabilidad Langfuse y streaming."""
    # Inicializar cliente Langfuse
    langfuse = get_client()

    # Inicializar CallbackHandler para LangGraph
    # Este handler captura automáticamente todas las trazas
    langfuse_handler = CallbackHandler()

    # Crear el grafo
    app = crear_graph()

    print("🤖 Agente LangGraph con Langfuse + Streaming")
    print("=" * 60)
    print("Escribe tu mensaje y presiona Enter.")
    print("Los tokens aparecerán en tiempo real.")
    print("Escribe 'salir' para terminar.")
    print("=" * 60)

    # Generar un nuevo session_id único para cada ejecución
    session_id = str(uuid.uuid4())
    thread_id = f"thread-{session_id}"

    print(f"📌 Sesión: {session_id}")

    # Configuración del thread para mantener contexto
    config = {
        "configurable": {"thread_id": thread_id},
        "callbacks": [langfuse_handler],  # Pasar el handler de Langfuse
        "metadata": {
            "langfuse_session_id": session_id,
            "langfuse_user_id": "demo-user",
            "langfuse_tags": ["demo", "langgraph", "langfuse", "streaming"]
        }
    }

    while True:
        # Obtener input del usuario
        try:
            user_input = input("\n👤 Tú: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 ¡Hasta luego!")
            break

        if user_input.lower() in ["salir", "exit", "quit"]:
            print("\n👋 ¡Hasta luego!")
            break

        if not user_input:
            continue

        print("\n🤖 Agente: ", end="", flush=True)

        # Stream de tokens en tiempo real con Langfuse tracing
        for chunk in app.stream(
            {"messages": [HumanMessage(content=user_input)]},
            config=config,
            stream_mode="messages",
            version="v2",
        ):
            # Solo procesar chunks de tipo "messages"
            if chunk["type"] == "messages":
                message_chunk, metadata = chunk["data"]

                # Filtrar solo tokens del nodo "agente" (no de tools)
                if metadata.get("langgraph_node") == "agente":
                    if message_chunk.content:
                        print(message_chunk.content, end="", flush=True)

        print()  # Nueva línea al final de la respuesta

    # Cerrar cliente Langfuse para asegurar que se envíen todas las trazas
    langfuse.shutdown()
    print("\n📊 Trazas enviadas a Langfuse. Visita https://cloud.langfuse.com para verlas.")


if __name__ == "__main__":
    main()
