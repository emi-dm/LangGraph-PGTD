# Ejemplo: Agente LangGraph Básico (Sin Herramientas)

**Nivel:** Principiante

Este es el ejemplo más simple de un agente LangGraph. Un agente que recibe mensajes y responde usando un LLM, sin herramientas adicionales.

## 🎯 Conceptos Clave

| Concepto | Descripción |
|----------|-------------|
| **MessagesState** | Estado del grafo basado en mensajes |
| **Nodo único** | Un solo nodo con el LLM |
| **Grafo lineal** | Flujo simple: START → Agente → END |

## 📁 Estructura del Proyecto

```
ejemplo-agente-basico/
├── src/
│   └── agente.py          # Código del agente básico
├── pyproject.toml          # Dependencias del proyecto
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
│ Agente  │
└────┬────┘
     │
     ▼
┌─────────┐
│   END   │
└─────────┘
```

## 📖 Siguiente Paso

Una vez entendido este ejemplo básico, continúa con [ejemplo-agente-con-tools](../ejemplo-agente-con-tools/) para aprender a añadir herramientas al agente.
