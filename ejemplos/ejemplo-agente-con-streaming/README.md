# Ejemplo: Agente LangGraph con Streaming

**Nivel:** Intermedio

Demuestra cómo usar `stream_mode="messages"` para recibir los tokens del LLM en tiempo real, en lugar de esperar la respuesta completa.

## 🎯 Conceptos Clave

| Concepto | Descripción |
|----------|-------------|
| **stream_mode="messages"** | Streaming token a token del LLM |
| **version="v2"** | Formato unificado de StreamPart |
| **Filtrado por nodo** | Filtrar mensajes por `langgraph_node` en metadatos |
| **Respuesta progresiva** | Mostrar tokens conforme llegan |

## 📁 Estructura del Proyecto

```
ejemplo-agente-con-streaming/
├── src/
│   ├── __init__.py
│   └── agente.py          # Agente con streaming de tokens
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
│ Agente  │ ──► Stream de tokens
└────┬────┘
     │
     ▼
┌─────────┐
│   END   │
└─────────┘
```

## 📖 Explora Más

Revisa [ejemplo-agente-con-memoria](../ejemplo-agente-con-memoria/) para aprender sobre memoria a corto plazo, o [ejemplo-agente-con-interrupciones](../ejemplo-agente-con-interrupciones/) para Human-in-the-Loop.
