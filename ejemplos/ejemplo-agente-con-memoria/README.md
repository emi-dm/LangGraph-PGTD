# Ejemplo: Agente LangGraph con Memoria (InMemorySaver)

**Nivel:** Intermedio

Este ejemplo demuestra cómo usar **memoria a corto plazo** con `InMemorySaver` para que el agente recuerde información entre interacciones.

## 🎯 Conceptos Clave

| Concepto | Descripción |
|----------|-------------|
| **InMemorySaver** | Checkpointer que guarda el estado en memoria RAM |
| **thread_id** | Identificador único para cada sesión/conversación |
| **Memoria a corto plazo** | El agente recuerda el historial dentro de una misma sesión |

## 📁 Estructura del Proyecto

```
ejemplo-agente-con-memoria/
├── src/
│   └── agente.py          # Script ejecutable con demo de memoria
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
│ Agente  │◄──── Memoria (thread_id)
└────┬────┘
     │
     ▼
┌─────────┐
│   END   │
└─────────┘
```

## 📖 Siguiente Paso

Explora [ejemplo-agente-con-streaming](../ejemplo-agente-con-streaming/) para aprender sobre streaming de tokens.

## 🔑 Cómo Funciona la Memoria

### Con mismo `thread_id` (misma sesión)
```
Invocación 1 → Guarda estado → Invocación 2 → Lee estado previo → Recuerda
```

### Con diferente `thread_id` (sesión nueva)
```
Sesión 1 (thread_id="a") → Estado guardado
Sesión 2 (thread_id="b") → Estado vacío → No recuerda nada
```

## 📝 Notas

- `InMemorySaver` guarda datos en RAM, se pierden al cerrar el proceso
- Para producción, usa un checkpointer persistente (PostgreSQL, SQLite)
- Cada `thread_id` representa una conversación independiente
- El historial de mensajes se acumula automáticamente

## ➡️ Comparación con Otros Ejemplos

| Ejemplo | Herramientas | Interrupciones | Memoria |
|---------|--------------|----------------|---------|
| Básico | ❌ | ❌ | ❌ |
| Con Tools | ✅ | ❌ | ❌ |
| Con Interrupciones | ✅ | ✅ | ✅ |
| **Con Memoria** | ❌ | ❌ | ✅ |
