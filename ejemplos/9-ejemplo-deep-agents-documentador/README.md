# Ejemplo: Sistema Multiagente Documentador con Deep Agents

**Nivel:** Avanzado

Este ejemplo demuestra cómo crear un sistema de documentación multiagente usando **Deep Agents**, **Tavily**, **OpenRouter** y **Langfuse**, donde múltiples subagentes especializados colaboran para investigar, escribir y revisar documentación técnica en formato Markdown.

## 📖 ¿Qué es Deep Agents?

**Deep Agents** es un framework de agentes de código abierto construido sobre **LangGraph**, diseñado para tareas complejas y multi-paso que requieren planificación, uso de herramientas y delegación a sub-agentes.

### Concepto: "Agent Harness"

Deep Agents se define como un **"agent harness"** (arnés de agente). Esto significa que es el mismo bucle básico de llamadas a herramientas que otros frameworks de agentes, pero con **herramientas y capacidades integradas** que facilitan la construcción de agentes sofisticados.

```
┌─────────────────────────────────────────────────────────────────┐
│                     Deep Agents (Harness)                       │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  Planning   │  │ File System │  │  Subagents  │  ← Built-in │
│  │  (To-Do)    │  │  (Context)  │  │  (Delegate) │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   Memory    │  │ Human-in-   │  │    MCP      │  ← Built-in │
│  │ (Persist)   │  │  the-Loop   │  │   Tools     │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                 │
│  ┌─────────────────────────────────────────────────┐           │
│  │              LangGraph Runtime                  │  ← Base   │
│  │  (Durable execution, streaming, checkpointing)  │           │
│  └─────────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────────┘
```

### Arquitectura de Capas

| Capa | Componente | Función |
|------|------------|---------|
| **Harness** | Deep Agents SDK | Herramientas y capacidades integradas |
| **Runtime** | LangGraph | Ejecución durable, streaming, checkpointing |
| **Building Blocks** | LangChain | Modelos, herramientas, mensajes |

### Capacidades Integradas

| Capacidad | Descripción |
|-----------|-------------|
| **Planificación** | Sistema de to-do list para descomponer tareas complejas en pasos |
| **Sistema de archivos** | Lectura/escritura de archivos para gestión de contexto (memoria, disco, sandboxes) |
| **Subagentes** | Delegación de trabajo a agentes especializados con contexto aislado |
| **Memoria persistente** | Información que persiste entre conversaciones y threads |
| **Human-in-the-Loop** | Aprobación humana para operaciones sensibles |
| **MCP Tools** | Carga de herramientas externas vía Model Context Protocol |
| **Skills** | Capacidades personalizables almacenadas en directorios de skills |

### ¿Cuándo usar Deep Agents?

| ✅ Usar Deep Agents cuando... | ❌ No usar Deep Agents cuando... |
|-------------------------------|----------------------------------|
| Tareas complejas multi-paso | Agentes simples con pocas herramientas |
| Necesitas planificación y descomposición | Solo necesitas un loop básico de tool-calling |
| Gestión de contexto grande vía archivos | El contexto cabe fácilmente en memoria |
| Delegación a subagentes especializados | Un solo agente puede manejar todo |
| Ejecución de largo tiempo | Tareas rápidas y de una sola vez |

### Alternativas más simples

Para agentes más simples, considera:
- **LangChain `create_agent`** — Agente básico con tool-calling
- **LangGraph custom workflow** — Grafo personalizado con nodos específicos

## 🎯 Conceptos Clave del Ejemplo

| Concepto | Descripción |
|----------|-------------|
| **Deep Agents SDK** | Framework para crear agentes complejos con subagentes |
| **Sistema Multiagente** | Múltiples agentes especializados colaborando |
| **Tavily** | Búsqueda web para investigación técnica |
| **Langfuse** | Observabilidad y trazas detalladas de ejecuciones |

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

## 📁 Estructura del Proyecto

```
ejemplo-deep-agents-documentador/
├── src/
│   └── agente.py          # Sistema multiagente documentador
├── pyproject.toml          # Dependencias
└── README.md               # Este archivo
```

## 🛠️ Instalación

```bash
# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install -e .

# Configurar API keys (desde la raíz del repositorio)
cp ../../.env.example ../../.env
# Edita .env y añade tus API keys
```

## 🔑 Variables de Entorno

| Variable | Descripción | Requerida |
|----------|-------------|-----------|
| `OPENROUTER_API_KEY` | API key de OpenRouter | ✅ Sí |
| `OPENROUTER_MODEL` | Modelo a usar (default: openai/gpt-4.1-mini) | Opcional |
| `TAVILY_API_KEY` | API key de Tavily para búsqueda web | ✅ Sí |
| `LANGFUSE_SECRET_KEY` | Secret key de Langfuse | ✅ Sí |
| `LANGFUSE_PUBLIC_KEY` | Public key de Langfuse | ✅ Sí |
| `LANGFUSE_HOST` | URL de Langfuse (default: cloud) | Opcional |

## ▶️ Ejecución

**Modo estándar** (genera documentación de ejemplo):

```bash
python src/agente.py
```

**Modo interactivo** (genera documentación bajo demanda):

```bash
python src/agente.py --interactivo
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
