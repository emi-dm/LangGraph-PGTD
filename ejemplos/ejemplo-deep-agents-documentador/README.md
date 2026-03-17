# Sistema Multiagente Documentador con Deep Agents

Este ejemplo demuestra cómo crear un sistema de documentación multiagente usando **Deep Agents**, **Tavily**, **OpenRouter** y **Langfuse**, donde múltiples subagentes especializados colaboran para investigar, escribir y revisar documentación técnica en formato Markdown.

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                    Agente Orquestador                        │
│  (Coordina el flujo de trabajo de documentación)            │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│ Investigador  │ │   Escritor    │ │   Revisor     │
│  (Tavily)     │ │  (Markdown)   │ │  (Quality)    │
└───────────────┘ └───────────────┘ └───────────────┘
```

## 🎯 Conceptos Demostrados

- **Deep Agents SDK**: Uso de `create_deep_agent` para crear agentes complejos
- **Sistema Multiagente**: Subagentes especializados con roles definidos
- **Integración Tavily**: Búsqueda web para investigación técnica
- **OpenRouter**: Acceso unificado a múltiples modelos LLM (Claude, GPT-4, Llama, etc.)
- **Langfuse**: Observabilidad y trazas detalladas de ejecuciones
- **Sistema de Archivos**: Gestión de documentos generados
- **Planificación**: Descomposición automática de tareas complejas

## 🤖 Subagentes

### 1. Investigador
- Busca información técnica usando Tavily
- Recopila documentación oficial y ejemplos
- Organiza hallazgos en informes estructurados

### 2. Escritor
- Transforma información en documentación Markdown
- Sigue mejores prácticas de documentación técnica
- Incluye ejemplos de código con syntax highlighting

### 3. Revisor
- Verifica precisión técnica
- Mejora claridad y estructura
- Corrige errores y asegura consistencia

## 🚀 Inicio Rápido

### Prerrequisitos

- Python >= 3.10
- API key de [OpenRouter](https://openrouter.ai/) (acceso a Claude, GPT-4, Llama, etc.)
- API key de [Tavily](https://tavily.com/) (búsqueda web)
- API keys de [Langfuse](https://langfuse.com/) (observabilidad)

### Configuración

1. **Copia el archivo de ejemplo**:

```bash
cp .env.example .env
```

2. **Configura las variables de entorno** en `.env`:

```bash
# OpenRouter - Acceso unificado a múltiples modelos
OPENROUTER_API_KEY=sk-or-...
OPENROUTER_MODEL=anthropic/claude-sonnet-4

# Tavily - Búsqueda web
TAVILY_API_KEY=tvly-...

# Langfuse - Observabilidad
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com
```

2. **Instala las dependencias**:

```bash
uv sync
```

### Ejecución

**Modo estándar** (genera documentación de ejemplo):

```bash
uv run ejemplos/ejemplo-deep-agents-documentador/src/agente.py
```

**Modo interactivo** (genera documentación bajo demanda):

```bash
uv run ejemplos/ejemplo-deep-agents-documentador/src/agente.py --interactivo
```

## 📝 Ejemplo de Uso

```python
from agente import crear_agente_documentador

# Crear el agente
agent = crear_agente_documentador()

# Generar documentación
result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Genera documentación sobre FastAPI con ejemplos"
    }]
})
```

## 📁 Estructura de Salida

Los documentos generados se guardan en la carpeta `docs/`:

```
docs/
├── langgraph-guide.md
├── fastapi-tutorial.md
└── ...
```

## 🔧 Personalización

### Agregar nuevos subagentes

```python
nuevo_subagente = {
    "name": "traductor",
    "description": "Especialista en traducción técnica",
    "prompt": "Eres un traductor técnico...",
    "tools": ["leer_documento", "guardar_documento"],
}

subagents.append(nuevo_subagente)
```

### Modificar herramientas de búsqueda

```python
def buscar_en_web(query: str, max_results: int = 10) -> str:
    # Personaliza los parámetros de búsqueda
    results = tavily_client.search(
        query,
        max_results=max_results,
        search_depth="advanced",  # Búsqueda más profunda
        include_raw_content=True,
    )
    # ... procesamiento personalizado
```

## 📚 Recursos

- [Deep Agents Documentation](https://docs.langchain.com/oss/python/deepagents/overview)
- [OpenRouter Documentation](https://openrouter.ai/docs)
- [Tavily API Documentation](https://docs.tavily.com/)
- [Langfuse Documentation](https://langfuse.com/docs)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)

## 🤝 Flujo de Trabajo

1. **Usuario** solicita documentación sobre un tema
2. **Orquestador** analiza y planifica el flujo
3. **Investigador** busca información con Tavily
4. **Escritor** crea el documento Markdown
5. **Revisor** mejora y pule el documento
6. **Sistema** guarda el documento final en `docs/`

## ⚙️ Configuración Avanzada

### Cambiar el modelo LLM

```python
agent = create_deep_agent(
    model="gpt-4o",  # Usar GPT-4o en lugar de gpt-4o-mini
    # ...
)
```

### Ajustar límite de recursión

```python
result = agent.invoke(
    {"messages": [...]},
    config={"recursion_limit": 100},  # Aumentar para tareas complejas
)
```

## 📄 Licencia

Este ejemplo es parte del proyecto LangGraph-PGTD y sigue la misma licencia.
