# Ejemplo: Agente con Memoria a Largo Plazo (SQLite)

Este ejemplo demuestra cómo usar **SqliteSaver** para implementar memoria a largo plazo en un agente LangGraph. A diferencia de `InMemorySaver`, la memoria SQLite persiste entre ejecuciones del programa.

## Conceptos Clave

- **SqliteSaver**: Checkpointer que almacena el estado en una base de datos SQLite
- **Persistencia**: La memoria sobrevive entre ejecuciones del programa
- **thread_id**: Identificador único para cada conversación/sesión
- **Recuperación**: Puedes retomar conversaciones anteriores

## Diferencias con InMemorySaver

| Característica | InMemorySaver | SqliteSaver |
|----------------|---------------|-------------|
| Persistencia | Solo en memoria RAM | Archivo SQLite en disco |
| Entre ejecuciones | ❌ Se pierde | ✅ Se conserva |
| Ideal para | Experimentación | Desarrollo local |
| Rendimiento | Más rápido | Ligeramente más lento |

## Instalación

```bash
# Instalar dependencias
uv sync

# O manualmente
uv add langgraph langgraph-checkpoint-sqlite langchain-openai langchain-core python-dotenv
```

## Configuración

Crea un archivo `.env` en la raíz del proyecto:

```env
OPENROUTER_API_KEY=tu_api_key_aqui
```

## Ejecución

```bash
uv run ejemplos/ejemplo-agente-con-memoria-sqlite/src/agente.py
```

## Uso

Una vez ejecutado, puedes:

1. **Conversar normalmente**: Escribe mensajes y el agente responderá
2. **Ver historial**: Escribe `historial` para ver toda la conversación
3. **Nueva sesión**: Escribe `nueva` para iniciar una nueva conversación
4. **Salir**: Escribe `salir` para terminar (la memoria se guarda automáticamente)

### Ejemplo de sesión

```
👤 Tú: Hola, me llamo María
🤖 Agente: ¡Hola María! ¿En qué puedo ayudarte hoy?

👤 Tú: ¿Cómo me llamo?
🤖 Agente: Te llamas María, como me mencionaste anteriormente.

👤 Tú: salir
👋 ¡Hasta luego! Tu conversación está guardada en SQLite.
```

Al ejecutar el programa nuevamente, el agente recordará la conversación anterior.

## Estructura del Proyecto

```
ejemplo-agente-con-memoria-sqlite/
├── README.md           # Este archivo
├── pyproject.toml      # Dependencias del proyecto
├── .env                # Variables de entorno (no incluido en git)
├── memoria.db          # Base de datos SQLite (se crea automáticamente)
└── src/
    └── agente.py       # Código del agente
```

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

## Referencias

- [Documentación de LangGraph - Persistencia](https://docs.langchain.com/oss/python/langgraph/persistence)
- [LangGraph Checkpoint SQLite (PyPI)](https://pypi.org/project/langgraph-checkpoint-sqlite/)
- [Ejemplos oficiales de LangGraph](https://github.com/langchain-ai/langgraph/tree/main/examples)
