"""
Ejemplo de agente LangGraph con herramientas e interrupciones (Human-in-the-Loop).

Este agente puede leer y crear archivos, pero pide confirmación al usuario
antes de ejecutar cualquier acción. Implementa el patrón human-in-the-loop.

Características:
- Herramientas de archivos (leer/crear)
- Interrupciones antes de ejecutar herramientas
- Aprobar/rechazar/modificar acciones
- Estado persistente con checkpointer
"""

from typing import Annotated, Literal
from typing_extensions import TypedDict
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage, AIMessage
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.graph import END, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command, interrupt
import os
import json

# Cargar variables de entorno
load_dotenv(override=True)


# =============================================================================
# HERRAMIENTAS
# =============================================================================

@tool
def leer_archivo(ruta: str) -> str:
    """Lee el contenido de un archivo dado su ruta absoluta o relativa.

    Args:
        ruta: La ruta del archivo a leer (ej: './datos.txt' o '/home/user/archivo.py')

    Returns:
        El contenido del archivo como string, o un mensaje de error.
    """
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            contenido = f.read()
        return contenido
    except FileNotFoundError:
        return f"Error: El archivo '{ruta}' no fue encontrado."
    except PermissionError:
        return f"Error: No tienes permisos para leer '{ruta}'."
    except Exception as e:
        return f"Error al leer el archivo: {str(e)}"


@tool
def crear_archivo(ruta: str, contenido: str) -> str:
    """Crea un archivo nuevo con el contenido especificado.

    Si el archivo ya existe, lo sobrescribe. Crea directorios padre si no existen.

    Args:
        ruta: La ruta donde crear el archivo (ej: './nuevo.txt' o 'output/datos.csv')
        contenido: El contenido a escribir en el archivo

    Returns:
        Mensaje de confirmación o error.
    """
    try:
        # Crear directorios padre si no existen
        directorio = os.path.dirname(ruta)
        if directorio:
            os.makedirs(directorio, exist_ok=True)

        with open(ruta, "w", encoding="utf-8") as f:
            f.write(contenido)
        return f"✅ Archivo '{ruta}' creado exitosamente."
    except PermissionError:
        return f"Error: No tienes permisos para escribir en '{ruta}'."
    except Exception as e:
        return f"Error al crear el archivo: {str(e)}"


# Herramienta especial que solicita aprobación humana antes de ejecutar
@tool
def crear_archivo_con_aprobacion(
    ruta: str,
    contenido: str,
    tool_call_id: Annotated[str, InjectedToolCallId]
) -> str:
    """Crea un archivo nuevo, pero solicita aprobación humana antes de ejecutar.

    Esta herramienta pausa la ejecución y pide confirmación al usuario
    antes de crear el archivo.

    Args:
        ruta: La ruta donde crear el archivo
        contenido: El contenido a escribir en el archivo
        tool_call_id: ID interno de la llamada a herramienta

    Returns:
        Mensaje de confirmación o rechazo.
    """
    # Interrumpir y pedir aprobación humana
    aprobacion = interrupt(
        {
            "tipo": "solicitud_aprobacion",
            "accion": "crear_archivo",
            "ruta": ruta,
            "contenido_preview": contenido[:200] + "..." if len(contenido) > 200 else contenido,
            "pregunta": f"¿Aprobar la creación del archivo '{ruta}'?"
        }
    )
    print("-" * 40)
    print(aprobacion)
    print("-" * 40)
    # Verificar respuesta del usuario
    # aprobacion será "OK" para aprobar, cualquier otro valor rechaza
    if aprobacion == "OK":
        # Ejecutar la acción aprobada
        try:
            directorio = os.path.dirname(ruta)
            if directorio:
                os.makedirs(directorio, exist_ok=True)

            with open(ruta, "w", encoding="utf-8") as f:
                f.write(contenido)
            return f"✅ Archivo '{ruta}' creado exitosamente (aprobado por usuario)."
        except Exception as e:
            return f"Error al crear el archivo: {str(e)}"
    else:
        return f"❌ Creación de archivo '{ruta}' rechazada por el usuario."


# Lista de herramientas disponibles
herramientas = [leer_archivo, crear_archivo_con_aprobacion]


# =============================================================================
# ESTADO
# =============================================================================

class State(MessagesState):
    """Estado del grafo: mensajes."""
    pass


# =============================================================================
# NODOS
# =============================================================================

def agente(state: State) -> dict:
    """Nodo principal del agente. Invoca al LLM con las herramientas disponibles."""
    llm = ChatOpenAI(
        base_url="https://openrouter.ai/api/v1",
        model="openai/gpt-4.1-mini",
        api_key=os.getenv("OPENROUTER_API_KEY")
    )

    # Vincular herramientas al LLM
    llm_con_herramientas = llm.bind_tools(herramientas)

    # Invocar y retornar respuesta
    respuesta = llm_con_herramientas.invoke(state["messages"])
    return {"messages": [respuesta]}


# Nodo de herramientas con manejo de interrupciones
def nodo_herramientas(state: State) -> dict:
    """Ejecuta las herramientas solicitadas por el LLM.

    Maneja las interrupciones para herramientas que requieren aprobación.
    """
    resultado = ToolNode(herramientas).invoke(state)
    return resultado


# =============================================================================
# GRAFO
# =============================================================================

def crear_graph():
    """Construye y compila el grafo del agente con interrupciones."""
    workflow = StateGraph(state_schema=State)

    # Añadir nodos
    workflow.add_node("agente", agente)
    # Nombre 'tools' requerido por tools_condition
    workflow.add_node("tools", nodo_herramientas)

    # Punto de entrada
    workflow.set_entry_point("agente")

    # Aristas condicionales usando tools_condition predefinido
    workflow.add_conditional_edges(
        "agente",
        tools_condition,  # Detecta automáticamente si hay tool calls y busca nodo 'tools'
    )

    # Después de ejecutar herramientas, volver al agente
    workflow.add_edge("tools", "agente")

    app = workflow.compile()

    return app


# =============================================================================
# EXPORT PARA LANGGRAPH CLI
# =============================================================================

graph = crear_graph()
