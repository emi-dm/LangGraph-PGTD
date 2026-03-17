"""
Ejemplo de agente LangGraph con herramientas de archivos.

Este agente puede:
- Leer archivos del sistema
- Crear archivos nuevos
- Responder preguntas y decidir cuándo usar herramientas
"""

from typing import Annotated, Sequence
from typing_extensions import TypedDict
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import END, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode
import os

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


# Lista de herramientas disponibles
herramientas = [leer_archivo, crear_archivo]


# =============================================================================
# ESTADO
# =============================================================================

class State(MessagesState):
    """Estado del grafo: solo mensajes."""
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


# Nodo de herramientas (ejecuta las herramientas solicitadas por el LLM)
nodo_herramientas = ToolNode(herramientas)


# =============================================================================
# ARISTAS CONDICIONALES
# =============================================================================

def debe_continuar(state: State) -> str:
    """Determina si el agente debe usar herramientas o terminar.
    
    Returns:
        "herramientas" si hay tool calls pendientes, END si no.
    """
    mensajes = state["messages"]
    ultimo_mensaje = mensajes[-1]
    
    # Si el último mensaje tiene llamadas a herramientas, ir al nodo de herramientas
    if hasattr(ultimo_mensaje, "tool_calls") and ultimo_mensaje.tool_calls:
        return "herramientas"
    
    # Si no, terminar
    return END


# =============================================================================
# GRAFO
# =============================================================================

def crear_graph():
    """Construye y compila el grafo del agente."""
    workflow = StateGraph(state_schema=State)
    
    # Añadir nodos
    workflow.add_node("agente", agente)
    workflow.add_node("herramientas", nodo_herramientas)
    
    # Punto de entrada
    workflow.set_entry_point("agente")
    
    # Aristas condicionales: agente decide si usar herramientas o terminar
    workflow.add_conditional_edges(
        "agente",
        debe_continuar,
        {
            "herramientas": "herramientas",
            END: END
        }
    )
    
    # Después de ejecutar herramientas, volver al agente
    workflow.add_edge("herramientas", "agente")
    
    # Compilar y retornar
    app = workflow.compile()
    return app


# =============================================================================
# EXPORT PARA LANGGRAPH CLI
# =============================================================================

graph = crear_graph()
