"""
Ejemplo de agente LangGraph con streaming de tokens.

Demuestra cómo usar stream_mode="messages" para recibir los tokens
del LLM en tiempo real, en lugar de esperar la respuesta completa.

Ejecución:
    python src/agente.py

Conceptos demostrados:
- stream_mode="messages" para streaming token a token
- version="v2" para formato unificado de StreamPart
- Filtrado por langgraph_node en los metadatos
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.graph import END, StateGraph, MessagesState
import os

# Cargar variables de entorno
load_dotenv(override=True)


# =============================================================================
# ESTADO
# =============================================================================

class State(MessagesState):
    """Estado del grafo: mensajes."""
    pass


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

    respuesta = llm.invoke(state["messages"])
    return {"messages": [respuesta]}


# =============================================================================
# GRAFO
# =============================================================================

def crear_graph():
    """Construye y compila el grafo del agente."""
    workflow = StateGraph(state_schema=State)

    # Añadir nodo
    workflow.add_node("agente", agente)

    # Punto de entrada y salida
    workflow.set_entry_point("agente")
    workflow.add_edge("agente", END)

    return workflow.compile()


# =============================================================================
# EJECUCIÓN INTERACTIVA CON STREAMING
# =============================================================================

def main():
    """Ejecuta el agente en modo interactivo con streaming de tokens."""

    print("=" * 60)
    print("⚡ Agente LangGraph con Streaming")
    print("=" * 60)
    print("Escribe tu mensaje y presiona Enter.")
    print("Los tokens aparecerán en tiempo real.")
    print("Escribe 'salir' para terminar.")
    print("=" * 60)
    print()

    app = crear_graph()

    while True:
        try:
            mensaje_usuario = input("👤 Tú: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 ¡Hasta luego!")
            break

        if not mensaje_usuario:
            continue

        if mensaje_usuario.lower() in ("salir", "exit", "quit"):
            print("👋 ¡Hasta luego!")
            break

        print("🤖 Agente: ", end="", flush=True)

        # Stream de tokens en tiempo real
        for chunk in app.stream(
            {"messages": [HumanMessage(content=mensaje_usuario)]},
            stream_mode="messages",
            version="v2",
        ):
            # Solo procesar chunks de tipo "messages"
            if chunk["type"] == "messages":
                message_chunk, metadata = chunk["data"]

                # Filtrar solo tokens del nodo "agente"
                if metadata.get("langgraph_node") == "agente":
                    if message_chunk.content:
                        print(message_chunk.content, end="", flush=True)

        print()  # Nueva línea al final de la respuesta
        print()


if __name__ == "__main__":
    main()
