# Ejemplo: Agente LangGraph con Herramientas e Interrupciones (Human-in-the-Loop)

**Nivel:** Avanzado

Este ejemplo evoluciona el agente con herramientas añadiendo **interrupciones** que permiten al usuario aprobar o rechazar acciones antes de que se ejecuten.

## 🎯 Conceptos Clave

| Concepto | Descripción |
|----------|-------------|
| **Human-in-the-Loop** | El usuario aprueba/rechaza acciones antes de ejecutarlas |
| **Interrupciones** | `interrupt()` pausa la ejecución y espera input del usuario |
| **MemorySaver** | Checkpointer en memoria para mantener historial y reanudar ejecución |
| **thread_id** | Identificador único para cada sesión/conversación |
| **Command** | Continúa la ejecución con la respuesta del usuario |

## 📁 Estructura del Proyecto

```
ejemplo-agente-con-interrupciones/
├── src/
│   └── agente.py          # Agente con tools e interrupciones
├── pyproject.toml          # Dependencias
├── langgraph.json          # Configuración LangGraph CLI
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

## ▶️ Uso

```bash
langgraph dev
```

## 📊 Flujo del Grafo

```
┌─────────┐
│  START  │
└────┬────┘
     │
     ▼
┌─────────┐
│ Agente  │◄────────────────┐
└────┬────┘                 │
     │                      │
     ▼                      │
┌─────────┐                 │
│Herramientas│              │
└────┬────┘                 │
     │                      │
     ▼                      │
┌─────────┐                 │
│ INTERRUPT│                │
└────┬────┘                 │
     │                      │
     ▼                      │
┌─────────┐                 │
│Aprobación├────────────────┘
└────┬────┘
     │
     ▼
┌─────────┐
│   END   │
└─────────┘
```

## 📖 Siguiente Paso

Explora [ejemplo-agente-con-memoria](../ejemplo-agente-con-memoria/) para aprender sobre memoria a corto plazo.

## 🔧 Herramientas Disponibles

### `leer_archivo(ruta: str)`
Lee el contenido de un archivo. **Sin interrupción** (lectura segura).

### `crear_archivo_con_aprobacion(ruta: str, contenido: str)`
Crea un archivo, pero **solicita aprobación** antes de ejecutar.

## 🔑 Diferencias con `ejemplo-agente-con-tools`

| Característica | Con Tools | Con Interrupciones |
|----------------|-----------|-------------------|
| Leer archivos | ✅ | ✅ |
| Crear archivos | ✅ Automático | ⚠️ Con aprobación |
| Memoria | ❌ | ✅ `MemorySaver` |
| Interrupciones | ❌ | ✅ `interrupt()` |
| Human-in-the-Loop | ❌ | ✅ |
| Historial entre mensajes | ❌ | ✅ |
| Recuperar estado | ❌ | ✅ `get_state()` |

## 💻 Ejemplo de Uso Programático

```python
from src.agente import graph

# Configuración con thread_id para persistencia
config = {"configurable": {"thread_id": "mi-sesion-1"}}

# Primera invocación: el agente decide crear un archivo
resultado = graph.invoke(
    {"messages": [("user", "Crea un archivo notas.txt con 'Hola mundo'")]},
    config
)

# El grafo se pausa en la interrupción
# Ver estado actual
estado = graph.get_state(config)
print(estado.next)  # ('herramientas',) - esperando aprobación

# Aprobar la acción (enviar "OK")
from langgraph.types import Command
resultado = graph.invoke(
    Command(resume="OK"),
    config
)

# O rechazar la acción (enviar cualquier otro valor)
resultado = graph.invoke(
    Command(resume="NO"),
    config
)
```

## 🔄 Flujo de Interrupción

1. **Usuario**: "Crea un archivo notas.txt con 'Hola mundo'"
2. **Agente**: Decide usar `crear_archivo_con_aprobacion`
3. **Grafo**: Se pausa con `interrupt()`
4. **Sistema**: Muestra solicitud de aprobación
5. **Usuario**: Aprueba o rechaza
6. **Grafo**: Reanuda con `Command(resume={...})`
7. **Herramienta**: Ejecuta o cancela según aprobación
8. **Agente**: Reporta resultado al usuario

## 🧠 Memoria (MemorySaver)

Este ejemplo usa `MemorySaver` como checkpointer para mantener memoria a corto plazo:

```python
from langgraph.checkpoint.memory import InMemorySaver

memoria = InMemorySaver()
app = workflow.compile(checkpointer=memoria)
```

### ¿Qué permite?

| Funcionalidad | Descripción |
|---------------|-------------|
| **Historial de conversación** | El agente recuerda mensajes anteriores usando el mismo `thread_id` |
| **Reanudar interrupciones** | Después de una interrupción, el estado se guarda y puede reanudarse |
| **Recuperar estado** | Puedes consultar el estado actual con `graph.get_state(config)` |

### Ejemplo de memoria entre conversaciones

```python
config = {"configurable": {"thread_id": "usuario-123"}}

# Primera conversación
graph.invoke({"messages": [("user", "Mi nombre es Emilio")]}, config)

# Segunda conversación - el agente recuerda el nombre
resultado = graph.invoke({"messages": [("user", "¿Cómo me llamo?")]}, config)
# El agente responderá: "Te llamas Emilio"
```

### Diferentes thread_id = diferentes memorias

```python
# Sesión 1 - memoria independiente
config1 = {"configurable": {"thread_id": "sesion-1"}}

# Sesión 2 - memoria independiente
config2 = {"configurable": {"thread_id": "sesion-2"}}
```

### En producción

Para producción, reemplaza `MemorySaver` con un checkpointer persistente:
- **PostgreSQL**: `from langgraph.checkpoint.postgres import PostgresSaver`
- **Redis**: `from langgraph.checkpoint.redis import RedisSaver`

## 📝 Notas

- El **checkpointer** (`MemorySaver`) es esencial para interrupciones y memoria
- Cada sesión necesita un `thread_id` único para mantener el estado
- En producción, usa un checkpointer persistente (PostgreSQL, Redis, etc.)
- Las interrupciones permiten workflows de aprobación, corrección de errores, etc.