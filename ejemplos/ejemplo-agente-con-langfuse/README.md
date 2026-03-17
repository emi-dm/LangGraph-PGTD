# Ejemplo: Agente LangGraph con Langfuse

**Nivel:** Intermedio

Este ejemplo demuestra cómo integrar [Langfuse](https://langfuse.com/) con LangGraph para obtener observabilidad completa de tu agente, incluyendo memoria conversacional, herramientas y streaming.

## 🎯 Conceptos Clave

| Concepto | Descripción |
|----------|-------------|
| **Langfuse** | Plataforma de observabilidad para aplicaciones LLM |
| **CallbackHandler** | Integración automática con LangChain/LangGraph |
| **Trazas** | Registro detallado de cada ejecución del agente |
| **Metadata** | Etiquetas y sesiones para organizar trazas |

## 🚀 Características

- 🔍 **Observabilidad con Langfuse**: Trazas detalladas de cada ejecución
- 🧠 **Memoria conversacional**: `InMemorySaver` para mantener contexto dentro de la sesión
- 🛠️ **Tools integradas**:
  - `ejecutar_codigo_python`: Ejecuta código Python y retorna el resultado
  - `fetch_url`: Obtiene contenido de una URL
- ⚡ **Streaming**: Tokens del LLM aparecen en tiempo real

## 📁 Estructura del Proyecto

```
ejemplo-agente-con-langfuse/
├── src/
│   ├── __init__.py
│   └── agente.py          # Agente con observabilidad Langfuse
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
| `LANGFUSE_SECRET_KEY` | Secret key de Langfuse | ✅ Sí |
| `LANGFUSE_PUBLIC_KEY` | Public key de Langfuse | ✅ Sí |
| `LANGFUSE_BASE_URL` | URL de Langfuse (default: cloud) | Opcional |

Puedes obtener las claves de Langfuse registrándote gratis en [cloud.langfuse.com](https://cloud.langfuse.com/).

## ▶️ Ejecución

```bash
python src/agente.py
```

## Conceptos clave

### CallbackHandler

El `CallbackHandler` de Langfuse se integra con LangChain/LangGraph para capturar automáticamente:

```python
from langfuse import get_client
from langfuse.langchain import CallbackHandler

# Inicializar cliente Langfuse
langfuse = get_client()

# Crear handler para capturar trazas
langfuse_handler = CallbackHandler()

# Pasar el handler al invocar el agente
resultado = app.invoke(
    {"messages": [HumanMessage(content="Hola")]},
    config={"callbacks": [langfuse_handler]}
)
```

### Metadata de trazas

Puedes añadir metadata a tus trazas para mejor organización:

```python
config = {
    "callbacks": [langfuse_handler],
    "metadata": {
        "langfuse_session_id": "session-123",
        "langfuse_user_id": "user-456",
        "langfuse_tags": ["production", "support"]
    }
}
```

### Cierre del cliente

Siempre cierra el cliente Langfuse al finalizar para asegurar que se envíen todas las trazas:

```python
langfuse.shutdown()
```

### InMemorySaver (Memoria conversacional)

El `InMemorySaver` permite que el agente recuerde el contexto de la conversación actual:

```python
from langgraph.checkpoint.memory import MemorySaver

memoria = MemorySaver()
app = workflow.compile(checkpointer=memoria)
```

### Tools (Herramientas)

El agente tiene dos herramientas disponibles:

#### 1. `ejecutar_codigo_python`
Ejecuta código Python y retorna el resultado:
```
👤 Tú: Ejecuta print("Hola mundo")
🤖 Agente: [usa la tool ejecutar_codigo_python]
📤 Salida: Hola mundo
```

#### 2. `fetch_url`
Obtiene el contenido de una URL:
```
👤 Tú: ¿Qué hay en https://ejemplo.com?
🤖 Agente: [usa la tool fetch_url]
📤 Contenido de la página...
```

## Ver trazas

Después de ejecutar el agente, visita [cloud.langfuse.com](https://cloud.langfuse.com/) para ver:

- **Traces**: Vista completa de cada ejecución del agente
- **Generations**: Detalles de cada llamada al LLM (input, output, tokens, costo)
- **Scores**: Métricas y evaluaciones

## 📖 Siguiente Paso

Explora [ejemplo-deep-agents-documentador](../ejemplo-deep-agents-documentador/) para aprender sobre sistemas multiagentes avanzados.

## 📚 Recursos

- [Documentación de Langfuse](https://langfuse.com/docs)
- [Integración con LangChain/LangGraph](https://langfuse.com/integrations/frameworks/langchain)
- [Ejemplos en el cookbook](https://langfuse.com/guides/cookbook/integration_langgraph)
