"""
Ejemplo básico de agente LangGraph (sin herramientas).

Este es el ejemplo más simple: un agente que recibe mensajes
y responde usando un LLM, sin herramientas adicionales.
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph, MessagesState
import os

# Cargar variables de entorno
load_dotenv(override=True)


# =============================================================================
# ESTADO
# =============================================================================

class State(MessagesState):
    """Estado del grafo: solo mensajes."""
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

    # Añadir único nodo
    workflow.add_node("agente", agente)

    # Punto de entrada y salida
    workflow.set_entry_point("agente")
    workflow.add_edge("agente", END)

    # Compilar y retornar
    app = workflow.compile()
    return app

# =============================================================================
# EXPORT PARA LANGGRAPH CLI
# =============================================================================

graph = crear_graph()
