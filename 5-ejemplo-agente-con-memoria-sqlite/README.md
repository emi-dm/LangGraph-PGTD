# Ejemplo: Agente LangGraph con Memoria Persistente (SQLite)

**Nivel:** Intermedio

Este ejemplo demuestra cómo usar **SqliteSaver** para implementar memoria a largo plazo en un agente LangGraph. A diferencia de `InMemorySaver`, la memoria SQLite persiste entre ejecuciones del programa.

## 🎯 Conceptos Clave

| Concepto | Descripción |
|----------|-------------|
| **SqliteSaver** | Checkpointer que almacena el estado en una base de datos SQLite |
| **Persistencia** | La memoria sobrevive entre ejecuciones del programa |
| **thread_id** | Identificador único para cada conversación/sesión |
| **Recuperación** | Puedes retomar conversaciones anteriores |

## 📁 Estructura del Proyecto

```
ejemplo-agente-con-memoria-sqlite/
├── src/
│   └── agente.py          # Agente con memoria SQLite
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

# Configurar API key (desde la raíz del repositorio)
cp ../../.env.example ../../.env
# Edita .env y añade tu OPENROUTER_API_KEY
```

## 🔑 Variables de Entorno

| Variable | Descripción | Requerida |
|----------|-------------|-----------|
| `OPENROUTER_API_KEY` | API key de OpenRouter | ✅ Sí |

## ▶️ Ejecución

```bash
python src/agente.py
```

## 📊 Flujo del Grafo

```
┌─────────┐
│  START  │
└────┬────┘
     │
     ▼
┌─────────┐
│ Agente  │◄──── Memoria SQLite (thread_id)
└────┬────┘
     │
     ▼
┌─────────┐
│   END   │
└─────────┘
```

## 📖 Uso

Una vez ejecutado, puedes:

1. **Conversar normalmente**: Escribe mensajes y el agente responderá
2. **Ver historial**: Escribe `historial` para ver toda la conversación
3. **Nueva sesión**: Escribe `nueva` para iniciar una nueva conversación
4. **Salir**: Escribe `quit` para terminar (la memoria se guarda automáticamente)

### Ejemplo de sesión

```
👤 Tú: Hola, me llamo María
🤖 Agente: ¡Hola María! ¿En qué puedo ayudarte hoy?

👤 Tú: ¿Cómo me llamo?
🤖 Agente: Te llamas María, como me mencionaste anteriormente.

👤 Tú: quit
👋 ¡Hasta luego! Tu conversación está guardada en SQLite.
```

Al ejecutar el programa nuevamente, el agente recordará la conversación anterior.

## Código Destacado

### Crear el checkpointer SQLite

```python
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver

# Conectar a la base de datos
conn = sqlite3.connect("memoria.db", check_same_thread=False)

# Crear el checkpointer
memoria = SqliteSaver(conn)

# Compilar el grafo con el checkpointer
app = workflow.compile(checkpointer=memoria)
```

### Invocar con thread_id

```python
config = {"configurable": {"thread_id": "mi-sesion"}}
resultado = app.invoke({"messages": [HumanMessage(content="Hola")]}, config=config)
```

## 📖 Siguiente Paso

Explora [ejemplo-agente-con-langfuse](../ejemplo-agente-con-langfuse/) para añadir observabilidad a tus agentes.

## 📚 Recursos

- [Documentación de LangGraph - Persistencia](https://docs.langchain.com/oss/python/langgraph/persistence)
- [LangGraph Checkpoint SQLite (PyPI)](https://pypi.org/project/langgraph-checkpoint-sqlite/)
- [Ejemplos oficiales de LangGraph](https://github.com/langchain-ai/langgraph/tree/main/examples)
