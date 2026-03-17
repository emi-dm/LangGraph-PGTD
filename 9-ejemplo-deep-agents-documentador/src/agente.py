"""
Sistema multiagente documentador con Deep Agents, Tavily y Langfuse.

Este script demuestra cómo crear un sistema de documentación multiagente
usando Deep Agents, donde múltiples subagentes especializados colaboran
para investigar, escribir y revisar documentación técnica en formato Markdown.

Ejecución:
    uv run ejemplos/9-ejemplo-deep-agents-documentador/src/agente.py

Conceptos demostrados:
- Deep Agents SDK con create_deep_agent
- Sistema multiagente con subagentes especializados
- Integración con Tavily para búsqueda web
- Integración con Langfuse para observabilidad
- Uso de OpenRouter como proveedor de modelos
- Sistema de archivos virtual para gestión de contexto
- Planificación de tareas complejas
- Generación de documentación en Markdown

Arquitectura del sistema:
┌─────────────────────────────────────────────────────────────┐
│                    Agente Orquestador                        │
│  (Coordina el flujo de trabajo de documentación)            │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│   Investigador │ │    Escritor   │ │   Revisor     │
│  (Tavily)     │ │  (Markdown)   │ │  (Quality)    │
└───────────────┘ └───────────────┘ └───────────────┘

Flujo de trabajo:
1. Usuario solicita documentación sobre un tema
2. Orquestador analiza y planifica el flujo
3. Investigador busca información con Tavily
4. Escritor crea el documento Markdown
5. Revisor mejora y pule el documento
6. Sistema guarda el documento final en docs/
"""

import os
from typing import Literal

from dotenv import load_dotenv
from tavily import TavilyClient
from deepagents import create_deep_agent
from langchain_openai import ChatOpenAI
from langfuse import get_client
from langfuse.langchain import CallbackHandler

# Cargar variables de entorno
load_dotenv(override=True)


# =============================================================================
# TOOLS PERSONALIZADAS
# =============================================================================

# Cliente Tavily para búsqueda web
tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])


def buscar_en_web(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = True,
) -> str:
    """Busca información en la web usando Tavily.

    Esta herramienta permite a los agentes investigar temas técnicos,
    encontrar documentación oficial, ejemplos de código y mejores prácticas.

    Args:
        query: Consulta de búsqueda.
        max_results: Número máximo de resultados (default: 5).
        topic: Tipo de búsqueda - general, news, o finance.
        include_raw_content: Incluir contenido completo de las páginas.

    Returns:
        Resultados de la búsqueda con títulos, URLs y contenido.
    """
    try:
        results = tavily_client.search(
            query,
            max_results=max_results,
            include_raw_content=include_raw_content,
            topic=topic,
        )

        # Formatear resultados para mejor legibilidad
        formatted_results = []
        for i, result in enumerate(results.get("results", []), 1):
            formatted = f"""
## Resultado {i}: {result.get('title', 'Sin título')}

**URL:** {result.get('url', 'N/A')}

**Resumen:** {result.get('content', 'Sin contenido')[:500]}...

**Relevancia:** {result.get('score', 'N/A')}
"""
            if result.get("raw_content"):
                formatted += f"\n**Contenido completo:**\n{result['raw_content'][:2000]}...\n"

            formatted_results.append(formatted)

        return "\n---\n".join(formatted_results) if formatted_results else "No se encontraron resultados."

    except Exception as e:
        return f"❌ Error en búsqueda: {type(e).__name__}: {e}"


def guardar_documento(filename: str, content: str) -> str:
    """Guarda un documento Markdown en el sistema de archivos.

    Args:
        filename: Nombre del archivo (debe terminar en .md).
        content: Contenido del documento en formato Markdown.

    Returns:
        Confirmación de guardado o mensaje de error.
    """
    try:
        # Asegurar que el directorio docs existe
        os.makedirs("docs", exist_ok=True)

        # Asegurar extensión .md
        if not filename.endswith(".md"):
            filename += ".md"

        filepath = os.path.join("docs", filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        return f"✅ Documento guardado exitosamente en: {filepath}"

    except Exception as e:
        return f"❌ Error al guardar documento: {type(e).__name__}: {e}"


def leer_documento(filename: str) -> str:
    """Lee un documento Markdown del sistema de archivos.

    Args:
        filename: Nombre del archivo a leer.

    Returns:
        Contenido del documento o mensaje de error.
    """
    try:
        if not filename.endswith(".md"):
            filename += ".md"

        filepath = os.path.join("docs", filename)

        if not os.path.exists(filepath):
            return f"❌ Archivo no encontrado: {filepath}"

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        return f"📄 Contenido de {filepath}:\n\n{content}"

    except Exception as e:
        return f"❌ Error al leer documento: {type(e).__name__}: {e}"


# =============================================================================
# PROMPTS DE SISTEMA PARA SUBAGENTES
# =============================================================================

INVESTIGADOR_PROMPT = """\
Eres un investigador técnico especializado en encontrar información precisa y actualizada.

Tu rol es:
1. Buscar información relevante sobre el tema solicitado usando la herramienta buscar_en_web
2. Encontrar documentación oficial, ejemplos de código y mejores prácticas
3. Recopilar información de múltiples fuentes para obtener una visión completa
4. Organizar la información encontrada de manera estructurada
5. Citar las fuentes de información encontradas

Directrices:
- Realiza múltiples búsquedas con diferentes términos para obtener cobertura completa
- Prioriza fuentes oficiales y documentación técnica
- Incluye ejemplos de código cuando estén disponibles
- Identifica las mejores prácticas y patrones comunes
- Estructura tu informe final con secciones claras

Cuando termines tu investigación, proporciona un informe estructurado con:
- Resumen ejecutivo del tema
- Puntos clave encontrados
- Ejemplos relevantes
- Fuentes consultadas
"""


ESCRITOR_PROMPT = """\
Eres un escritor técnico especializado en crear documentación clara y profesional en Markdown.

Tu rol es:
1. Transformar información técnica en documentación bien estructurada
2. Crear documentos Markdown siguiendo las mejores prácticas
3. Incluir ejemplos de código con sintaxis highlighting
4. Usar tablas, listas y otros elementos de Markdown para mejorar la legibilidad
5. Guardar los documentos usando la herramienta guardar_documento

Estructura estándar de documentación:
```markdown
# Título Principal

## Introducción
Breve descripción del tema y su importancia.

## Conceptos Clave
Explicación de los conceptos fundamentales.

## Guía de Inicio Rápido
Pasos para comenzar rápidamente.

## Ejemplos Prácticos
Ejemplos de código con explicaciones.

## Mejores Prácticas
Recomendaciones y patrones recomendados.

## Referencias
Enlaces a recursos adicionales.
```

Directrices:
- Usa encabezados jerárquicos (H1, H2, H3) apropiadamente
- Incluye bloques de código con el lenguaje especificado
- Usa tablas para comparar información
- Añade notas y advertencias cuando sea relevante
- Mantén un tono profesional pero accesible
"""


REVISOR_PROMPT = """\
Eres un revisor técnico especializado en mejorar la calidad de documentación.

Tu rol es:
1. Revisar documentos Markdown creados por el escritor
2. Verificar la precisión técnica de la información
3. Mejorar la claridad y estructura del documento
4. Corregir errores gramaticales y de formato
5. Asegurar consistencia en el estilo de documentación

Criterios de revisión:
- **Precisión técnica**: ¿La información es correcta y actualizada?
- **Claridad**: ¿El contenido es fácil de entender?
- **Estructura**: ¿La organización del documento es lógica?
- **Completitud**: ¿Se cubren todos los aspectos importantes?
- **Ejemplos**: ¿Los ejemplos de código son correctos y útiles?
- **Formato**: ¿Se siguen las convenciones de Markdown?

Proceso de revisión:
1. Lee el documento usando leer_documento
2. Identifica áreas de mejora
3. Realiza las correcciones necesarias
4. Guarda la versión revisada con guardar_documento
5. Proporciona un resumen de los cambios realizados
"""


ORQUESTADOR_PROMPT = """\
Eres el agente orquestador de un sistema de documentación multiagente.

Tu rol es coordinar el flujo de trabajo de documentación, delegando tareas
a subagentes especializados según sea necesario.

Flujo de trabajo típico:
1. **Investigación**: Delega al investigador para recopilar información sobre el tema
2. **Escritura**: Delega al escritor para crear el documento Markdown
3. **Revisión**: Delega al revisor para mejorar y pulir el documento

Instrucciones:
- Analiza la solicitud del usuario para determinar el tipo de documentación necesaria
- Planifica el flujo de trabajo apropiado
- Delega tareas a los subagentes especializados
- Coordina la entrega del documento final
- Informa al usuario sobre el progreso y resultado

Tipos de documentación que puedes generar:
- Guías de inicio rápido (quickstart)
- Tutoriales paso a paso
- Referencias de API
- Documentación de arquitectura
- Mejores prácticas
- Resolución de problemas (troubleshooting)
"""


# =============================================================================
# DEFINICIÓN DE SUBAGENTES
# =============================================================================

subagents = [
    {
        "name": "investigador",
        "description": "Especialista en investigación técnica. Usa esta herramienta para buscar información, documentación y ejemplos sobre un tema específico.",
        "system_prompt": INVESTIGADOR_PROMPT,
        "tools": [buscar_en_web],
    },
    {
        "name": "escritor",
        "description": "Especialista en escritura técnica. Usa esta herramienta para crear documentos Markdown bien estructurados y profesionales.",
        "system_prompt": ESCRITOR_PROMPT,
        "tools": [guardar_documento, leer_documento],
    },
    {
        "name": "revisor",
        "description": "Especialista en revisión técnica. Usa esta herramienta para revisar, mejorar y pulir documentos existentes.",
        "system_prompt": REVISOR_PROMPT,
        "tools": [guardar_documento, leer_documento],
    },
]


# =============================================================================
# CONFIGURACIÓN DE MODELO CON OPENROUTER
# =============================================================================

def crear_modelo():
    """Crea el modelo LLM usando OpenRouter.

    OpenRouter permite acceder a múltiples modelos (GPT-4, Claude, Llama, etc.)
    a través de una API unificada.

    Returns:
        Instancia de ChatOpenAI configurada para OpenRouter.
    """
    return ChatOpenAI(
        model=os.environ.get("OPENROUTER_MODEL", "openrouter/hunter-alpha"),
        api_key=os.environ["OPENROUTER_API_KEY"],
        base_url="https://openrouter.ai/api/v1",
        temperature=0.7
    )


# =============================================================================
# CREACIÓN DEL AGENTE PRINCIPAL
# =============================================================================

def crear_agente_documentador():
    """Crea y retorna el agente documentador multiagente.

    Returns:
        Agente Deep Agent configurado para documentación con Langfuse.
    """
    # Crear modelo con OpenRouter
    model = crear_modelo()

    # Crear agente con Deep Agents
    agent = create_deep_agent(
        name="documentador-multiagente",
        model=model,
        tools=[buscar_en_web, guardar_documento, leer_documento],
        system_prompt=ORQUESTADOR_PROMPT,
        subagents=subagents,
    )

    return agent


def obtener_callbacks_langfuse():
    """Crea callbacks de Langfuse para observabilidad.

    Returns:
        Lista con el CallbackHandler de Langfuse.
    """
    langfuse_handler = CallbackHandler()
    return [langfuse_handler]


# =============================================================================
# EJECUCIÓN PRINCIPAL
# =============================================================================

def main():
    """Función principal que ejecuta el sistema de documentación."""
    print("=" * 70)
    print("📚 SISTEMA MULTIAGENTE DOCUMENTADOR CON DEEP AGENTS")
    print("=" * 70)
    print()

    # Verificar variables de entorno
    if not os.environ.get("TAVILY_API_KEY"):
        print("❌ Error: TAVILY_API_KEY no encontrada en variables de entorno")
        print("   Configura tu API key de Tavily en el archivo .env")
        return

    if not os.environ.get("OPENROUTER_API_KEY"):
        print("❌ Error: OPENROUTER_API_KEY no encontrada en variables de entorno")
        print("   Configura tu API key de OpenRouter en el archivo .env")
        return

    # Crear el agente
    print("🔧 Inicializando sistema multiagente...")
    agent = crear_agente_documentador()
    print("✅ Sistema inicializado correctamente")

    # Configurar callbacks de Langfuse
    callbacks = obtener_callbacks_langfuse()
    print("📊 Langfuse observabilidad activada")
    print()

    # Ejemplo de uso: Documentar un tema
    tema = "LangGraph: Framework para construir agentes con LLMs"

    print(f"📝 Generando documentación sobre: {tema}")
    print("-" * 70)
    print()

    solicitud = f"""\
Por favor, genera documentación completa sobre "{tema}".

La documentación debe incluir:
1. Una introducción clara al tema
2. Conceptos clave y arquitectura
3. Guía de inicio rápido con ejemplos de código
4. Mejores prácticas
5. Casos de uso comunes

Usa el flujo de trabajo completo:
- Primero investiga el tema usando el subagente investigador
- Luego crea el documento Markdown con el subagente escritor
- Finalmente revisa y mejora el documento con el subagente revisor

Guarda el documento final como "langgraph-guide.md"
"""

    # Ejecutar el agente con Langfuse callbacks
    print("🚀 Iniciando generación de documentación...")
    print()

    result = agent.invoke(
        {"messages": [{"role": "user", "content": solicitud}]},
        config={
            "recursion_limit": 50,
            "callbacks": callbacks,
        },
    )

    # Mostrar resultado
    print()
    print("=" * 70)
    print("📊 RESULTADO DE LA GENERACIÓN")
    print("=" * 70)
    print()

    for message in result.get("messages", []):
        if hasattr(message, "content") and message.content:
            print(message.content)
            print()

    print()
    print("✅ Documentación generada exitosamente")
    print("📁 Revisa la carpeta 'docs/' para ver los documentos generados")


def modo_interactivo():
    """Modo interactivo para generar documentación bajo demanda."""
    print("=" * 70)
    print("📚 SISTEMA MULTIAGENTE DOCUMENTADOR - MODO INTERACTIVO")
    print("=" * 70)
    print()
    print("Comandos disponibles:")
    print("  - Escribe un tema para generar documentación")
    print("  - 'quit' para terminar")
    print()

    # Verificar variables de entorno
    if not os.environ.get("TAVILY_API_KEY") or not os.environ.get("OPENROUTER_API_KEY"):
        print("❌ Error: Configura TAVILY_API_KEY y OPENROUTER_API_KEY en .env")
        return

    # Crear el agente
    agent = crear_agente_documentador()

    # Configurar callbacks de Langfuse
    callbacks = obtener_callbacks_langfuse()

    while True:
        print("-" * 70)
        tema = input("\n🔍 ¿Sobre qué tema quieres documentación? > ").strip()

        if tema.lower() in ["salir", "exit", "quit"]:
            print("\n👋 ¡Hasta luego!")
            break

        if not tema:
            print("⚠️ Por favor, ingresa un tema válido")
            continue

        solicitud = f"""\
Genera documentación técnica completa sobre "{tema}".

Sigue este flujo:
1. Investiga el tema (búsquedas web con Tavily)
2. Escribe un documento Markdown completo
3. Revisa y mejora el documento
4. Guarda como "{tema.lower().replace(' ', '-')}.md"

La documentación debe ser profesional, con ejemplos de código y mejores prácticas.
"""

        print(f"\n🚀 Generando documentación sobre: {tema}")
        print()

        try:
            result = agent.invoke(
                {"messages": [{"role": "user", "content": solicitud}]},
                config={
                    "recursion_limit": 50,
                    "callbacks": callbacks,
                },
            )

            # Mostrar último mensaje del asistente
            messages = result.get("messages", [])
            for msg in reversed(messages):
                if hasattr(msg, "content") and msg.content:
                    print("\n" + "=" * 70)
                    print("📄 RESUMEN:")
                    print("=" * 70)
                    print(msg.content)
                    break

        except Exception as e:
            print(f"\n❌ Error: {type(e).__name__}: {e}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--interactivo":
        modo_interactivo()
    else:
        main()
