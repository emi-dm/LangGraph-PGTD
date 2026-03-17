"""
Ejemplo de agente LangGraph con memoria (InMemorySaver).

Este script demuestra cómo usar memoria a corto plazo para que el agente
recuerde información entre interacciones dentro de una misma conversación.

Ejecución:
    python src/agente.py

Conceptos demostrados:
- InMemorySaver para persistencia en memoria
- thread_id para mantener sesiones separadas
- Memoria entre múltiples invocaciones
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.graph import END, StateGraph, MessagesState
from langgraph.checkpoint.memory import InMemorySaver
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
    """Construye y compila el grafo con memoria."""
    workflow = StateGraph(state_schema=State)

    # Añadir nodo
    workflow.add_node("agente", agente)

    # Punto de entrada y salida
    workflow.set_entry_point("agente")
    workflow.add_edge("agente", END)

    # Compilar con InMemorySaver para memoria a corto plazo
    memoria = InMemorySaver()
    app = workflow.compile(checkpointer=memoria)

    return app


# =============================================================================
# EJECUCIÓN DESDE TERMINAL
# =============================================================================

def main():
    """Ejecuta el agente en modo interactivo con memoria."""

    print("=" * 60)
    print("🧠 Agente LangGraph con Memoria (modo interactivo)")
    print("=" * 60)
    print("Escribe tu mensaje y presiona Enter.")
    print("Escribe 'quit' para terminar la conversación.")
    print("=" * 60)
    print()

    # Crear el grafo con memoria
    app = crear_graph()

    # Configuración con thread_id para mantener la sesión
    config = {"configurable": {"thread_id": "sesion-interactiva"}}

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

        resultado = app.invoke(
            {"messages": [HumanMessage(content=mensaje_usuario)]},
            config
        )

        respuesta = resultado["messages"][-1].content
        print(f"🤖 Agente: {respuesta}")


if __name__ == "__main__":
    main()
