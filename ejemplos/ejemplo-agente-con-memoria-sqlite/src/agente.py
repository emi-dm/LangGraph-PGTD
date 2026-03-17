"""
Ejemplo de agente LangGraph con memoria a largo plazo usando SQLite.

Este script demuestra cómo usar SqliteSaver para persistir el estado
del agente en una base de datos SQLite, permitiendo que la memoria
sobreviva entre ejecuciones del programa.

Ejecución:
    uv run ejemplos/ejemplo-agente-con-memoria-sqlite/src/agente.py

Conceptos demostrados:
- SqliteSaver para persistencia en SQLite
- Memoria a largo plazo (sobrevive entre ejecuciones)
- thread_id para mantener sesiones separadas
- Recuperación de conversaciones anteriores
"""

import sqlite3
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.graph import END, StateGraph, MessagesState
from langgraph.checkpoint.sqlite import SqliteSaver
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

def crear_graph(db_path: str = "memoria.db"):
    """Construye y compila el grafo con memoria SQLite persistente.

    Args:
        db_path: Ruta al archivo de base de datos SQLite.

    Returns:
        Grafo compilado con SqliteSaver.
    """
    workflow = StateGraph(state_schema=State)

    # Añadir nodo
    workflow.add_node("agente", agente)

    # Punto de entrada y salida
    workflow.set_entry_point("agente")
    workflow.add_edge("agente", END)

    # Compilar con SqliteSaver para memoria a largo plazo
    # La conexión se mantiene abierta durante la vida del grafo
    conn = sqlite3.connect(db_path, check_same_thread=False)
    memoria = SqliteSaver(conn)
    app = workflow.compile(checkpointer=memoria)

    return app


# =============================================================================
# UTILIDADES
# =============================================================================

def mostrar_historial(app, config: dict):
    """Muestra el historial de mensajes de la conversación actual."""
    estado = app.get_state(config)
    if estado and estado.values.get("messages"):
        print("\n📜 Historial de la conversación:")
        print("-" * 40)
        for msg in estado.values["messages"]:
            if isinstance(msg, HumanMessage):
                print(f"👤 Tú: {msg.content}")
            else:
                print(f"🤖 Agente: {msg.content}")
        print("-" * 40)


# =============================================================================
# EJECUCIÓN DESDE TERMINAL
# =============================================================================

def main():
    """Ejecuta el agente en modo interactivo con memoria SQLite."""

    # Ruta a la base de datos (en el directorio del ejemplo)
    script_dir = Path(__file__).parent.parent
    db_path = script_dir / "memoria.db"

    print("=" * 60)
    print("🧠 Agente LangGraph con Memoria SQLite (largo plazo)")
    print("=" * 60)
    print(f"📁 Base de datos: {db_path}")
    print()
    print("Escribe tu mensaje y presiona Enter.")
    print("Comandos especiales:")
    print("  - 'salir': Terminar la conversación")
    print("  - 'historial': Ver el historial completo")
    print("  - 'nueva': Iniciar una nueva sesión (nuevo thread_id)")
    print("=" * 60)
    print()

    # Crear el grafo con memoria SQLite
    app = crear_graph(str(db_path))

    # Configuración con thread_id para mantener la sesión
    thread_id = "sesion-principal"
    config = {"configurable": {"thread_id": thread_id}}

    print(f"🔑 Sesión actual: {thread_id}")
    print()

    while True:
        try:
            mensaje_usuario = input("👤 Tú: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 ¡Hasta luego!")
            break

        if not mensaje_usuario:
            continue

        # Comandos especiales
        if mensaje_usuario.lower() == "salir":
            print("👋 ¡Hasta luego! Tu conversación está guardada en SQLite.")
            break

        if mensaje_usuario.lower() == "historial":
            mostrar_historial(app, config)
            continue

        if mensaje_usuario.lower() == "nueva":
            import uuid
            thread_id = f"sesion-{uuid.uuid4().hex[:8]}"
            config = {"configurable": {"thread_id": thread_id}}
            print(f"🔑 Nueva sesión: {thread_id}")
            continue

        # Invocar al agente
        try:
            resultado = app.invoke(
                {"messages": [HumanMessage(content=mensaje_usuario)]},
                config=config
            )
            # Mostrar la respuesta del agente
            respuesta = resultado["messages"][-1]
            print(f"🤖 Agente: {respuesta.content}")
            print()
        except Exception as e:
            print(f"❌ Error: {e}")
            print()


if __name__ == "__main__":
    main()
