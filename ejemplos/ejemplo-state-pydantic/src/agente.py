"""
Ejemplo básico SIN LLMs: State con Pydantic en LangGraph.

Este ejemplo demuestra cómo LangGraph gestiona el State usando
un modelo Pydantic, incluyendo:
- Validación de tipos en tiempo de ejecución
- Coerción automática de tipos
- Actualización del estado a través de nodos
- Acceso al estado desde los nodos
"""

from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END


# =============================================================================
# DEFINICIÓN DEL STATE CON PYDANTIC
# =============================================================================

class MiState(BaseModel):
    """
    Estado del grafo definido como modelo Pydantic.

    Pydantic valida los tipos en tiempo de ejecución, lo que significa
    que si intentas pasar un valor con tipo incorrecto, obtendrás un error
    inmediatamente en lugar de un bug silencioso.
    """
    contador: int = Field(default=0, description="Contador de iteraciones")
    mensajes: list[str] = Field(
        default_factory=list, description="Lista de mensajes acumulados")
    nombre: str = Field(default="Usuario", description="Nombre del usuario")


# =============================================================================
# NODOS DEL GRAFO
# =============================================================================

def nodo_saludo(state: MiState) -> dict:
    """
    Primer nodo: genera un saludo personalizado.

    Recibe el estado completo y retorna un diccionario con los campos
    que desea actualizar. LangGraph hace el merge automáticamente.
    """
    saludo = f"¡Hola, {state.nombre}! Bienvenido al ejemplo de State con Pydantic."
    return {
        "mensajes": state.mensajes + [saludo],
        "contador": state.contador + 1,
    }


def nodo_procesar(state: MiState) -> dict:
    """
    Segundo nodo: procesa y agrega información al estado.

    Demuestra cómo los nodos pueden leer el estado actual
    (contador, mensajes) y actualizarlo incrementalmente.
    """
    mensaje = f"Iteración #{state.contador}: Procesando con {len(state.mensajes)} mensajes acumulados."
    return {
        "mensajes": state.mensajes + [mensaje],
        "contador": state.contador + 1,
    }


def nodo_despedida(state: MiState) -> dict:
    """
    Tercer nodo: genera una despedida.

    Lee el contador final y genera un resumen.
    """
    despedida = f"¡Adiós, {state.nombre}! Se procesaron {state.contador} pasos en total."
    return {
        "mensajes": state.mensajes + [despedida],
        "contador": state.contador + 1,
    }


# =============================================================================
# CONSTRUCCIÓN DEL GRAFO
# =============================================================================

def crear_grafo():
    """
    Construye y compila el grafo con el State Pydantic.

    El flujo es lineal: START → saludo → procesar → despedida → END
    """
    # Crear el grafo pasando el modelo Pydantic como state_schema
    workflow = StateGraph(MiState)

    # Añadir los nodos
    workflow.add_node("saludo", nodo_saludo)
    workflow.add_node("procesar", nodo_procesar)
    workflow.add_node("despedida", nodo_despedida)

    # Definir las conexiones (edges)
    workflow.add_edge(START, "saludo")
    workflow.add_edge("saludo", "procesar")
    workflow.add_edge("procesar", "despedida")
    workflow.add_edge("despedida", END)

    # Compilar el grafo
    return workflow.compile()


# =============================================================================
# EJECUCIÓN Y DEMOSTRACIÓN
# =============================================================================

def demo_validacion_pydantic():
    """
    Demuestra la validación de tipos de Pydantic.

    Pydantic coercionará ciertos tipos automáticamente:
    - "42" (string) → 42 (int) para campos int
    - Esto puede ser útil pero también inesperado
    """
    print("=" * 60)
    print("DEMOSTRACIÓN: Validación de Pydantic")
    print("=" * 60)

    # ✅ Estado válido
    estado_valido = MiState(contador=0, mensajes=[], nombre="Emi")
    print(f"\n✅ Estado válido: {estado_valido}")

    # ✅ Coerción automática: "5" se convierte en 5
    estado_coercion = MiState(contador="5", mensajes=[], nombre="Ana")
    print(f"✅ Coerción automática (contador='5'): {estado_coercion}")
    print(f"   Tipo de contador: {type(estado_coercion.contador)}")

    # ❌ Error de validación: "abc" no puede ser convertido a int
    try:
        estado_invalido = MiState(contador="abc", mensajes=[], nombre="Error")
    except Exception as e:
        print(f"\n❌ Error de validación esperado:")
        print(f"   {type(e).__name__}: {e}")


def demo_ejecucion_grafo():
    """
    Demuestra la ejecución del grafo con State Pydantic.
    """
    print("\n" + "=" * 60)
    print("DEMOSTRACIÓN: Ejecución del grafo")
    print("=" * 60)

    # Crear el grafo
    grafo = crear_grafo()

    # Estado inicial usando el modelo Pydantic
    estado_inicial = MiState(
        contador=0,
        mensajes=[],
        nombre="Emi"
    )

    print(f"\n📥 Estado inicial:")
    print(f"   contador: {estado_inicial.contador}")
    print(f"   mensajes: {estado_inicial.mensajes}")
    print(f"   nombre:   {estado_inicial.nombre}")

    # Invocar el grafo
    resultado = grafo.invoke(estado_inicial)

    print(f"\n📤 Estado final (resultado de invoke):")
    print(f"   tipo:     {type(resultado).__name__}")
    print(f"   contador: {resultado['contador']}")
    print(f"   nombre:   {resultado['nombre']}")
    print(f"\n   📝 Mensajes generados:")
    for i, msg in enumerate(resultado["mensajes"], 1):
        print(f"      {i}. {msg}")

    # Nota importante sobre el tipo de resultado
    print(f"\n⚠️  NOTA: El resultado de invoke() es un dict, NO un modelo Pydantic.")
    print(f"   Esto es una limitación conocida de LangGraph.")
    print(f"   Para convertirlo a Pydantic: MiState(**resultado)")


def demo_visualizacion_grafo():
    """
    Muestra la estructura del grafo en formato Mermaid.
    """
    print("\n" + "=" * 60)
    print("ESTRUCTURA DEL GRAFO (Mermaid)")
    print("=" * 60)

    grafo = crear_grafo()
    print(f"\n{grafo.get_graph().draw_mermaid()}")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    # 1. Demostrar validación de Pydantic
    demo_validacion_pydantic()

    # 2. Ejecutar el grafo
    demo_ejecucion_grafo()

    # 3. Mostrar estructura del grafo
    demo_visualizacion_grafo()
