# LangGraph-PGTD

Repositorio de ejemplos progresivos para aprender a construir agentes con LangGraph, desde lo más básico hasta patrones avanzados.

## 📚 Ejemplos Disponibles (ordenados por complejidad)

| # | Ejemplo | Nivel | Descripción |
|---|---------|-------|-------------|
| 1 | [1-ejemplo-state-pydantic](./ejemplos/1-ejemplo-state-pydantic/) | Básico | State con Pydantic (sin LLMs) - Validación y concatenación |
| 2 | [2-ejemplo-agente-basico](./ejemplos/2-ejemplo-agente-basico/) | Principiante | Agente simple sin herramientas |
| 3 | [3-ejemplo-agente-con-tools](./ejemplos/3-ejemplo-agente-con-tools/) | Intermedio | Agente con herramientas de archivos |
| 4 | [4-ejemplo-agente-con-memoria](./ejemplos/4-ejemplo-agente-con-memoria/) | Intermedio | Memoria a corto plazo con InMemorySaver |
| 5 | [5-ejemplo-agente-con-memoria-sqlite](./ejemplos/5-ejemplo-agente-con-memoria-sqlite/) | Intermedio | Memoria persistente con SQLite |
| 6 | [6-ejemplo-agente-con-streaming](./ejemplos/6-ejemplo-agente-con-streaming/) | Intermedio | Streaming de tokens en tiempo real |
| 7 | [7-ejemplo-agente-con-interrupciones](./ejemplos/7-ejemplo-agente-con-interrupciones/) | Avanzado | Human-in-the-Loop con interrupciones |
| 8 | [8-ejemplo-agente-con-langfuse](./ejemplos/8-ejemplo-agente-con-langfuse/) | Intermedio | Observabilidad con Langfuse |
| 9 | [9-ejemplo-deep-agents-documentador](./ejemplos/9-ejemplo-deep-agents-documentador/) | Avanzado | Sistema multiagente documentador |

## 🚀 Inicio Rápido

### Prerrequisitos

- Python 3.11+
- API key de OpenRouter (u otro proveedor compatible)

### Configuración

1. **Clona el repositorio**:
   ```bash
   git clone <url-del-repositorio>
   cd LangGraph-PGTD
   ```

2. **Configura tu API key**:
   ```bash
   cp .env.example .env
   # Edita .env y añade tu OPENROUTER_API_KEY
   ```

3. **Elige un ejemplo y navega a su directorio**:
   ```bash
   cd ejemplos/2-ejemplo-agente-basico
   ```

4. **Crea un entorno virtual** (recomendado):
   ```bash
   uv sync
   ```
5. **Ejecuta el ejemplo**:
   ```bash
   langgraph dev  # Para ejemplos con langgraph.json
   # o
   uv run src/agente.py  # Para ejemplos sin langgraph.json
   ```

## 📁 Estructura del Repositorio

```
LangGraph-PGTD/
├── .env.example              # Plantilla de variables de entorno
├── .gitignore                # Archivos ignorados por Git
├── README.md                 # Este archivo
├── pyproject.toml            # Configuración común del proyecto
└── ejemplos/
    ├── 1-ejemplo-state-pydantic/          # State con Pydantic (sin LLMs)
    ├── 2-ejemplo-agente-basico/           # Agente simple
    ├── 3-ejemplo-agente-con-tools/        # Agente con herramientas
    ├── 4-ejemplo-agente-con-memoria/      # Memoria InMemory
    ├── 5-ejemplo-agente-con-memoria-sqlite/ # Memoria SQLite
    ├── 6-ejemplo-agente-con-streaming/    # Streaming
    ├── 7-ejemplo-agente-con-interrupciones/ # Human-in-the-Loop
    ├── 8-ejemplo-agente-con-langfuse/     # Observabilidad
    └── 9-ejemplo-deep-agents-documentador/ # Multiagente
```

## 🛠️ Dependencias Comunes

Todos los ejemplos comparten las siguientes dependencias:

- `langgraph` - Framework para construir agentes
- `langchain-openai` - Integración con OpenAI/OpenRouter
- `langchain-core` - Componentes core de LangChain
- `python-dotenv` - Gestión de variables de entorno
- `langgraph-cli[inmem]` - CLI de LangGraph (para ejemplos con langgraph.json)

## 📖 Recursos

- [Documentación de LangGraph](https://langchain-ai.github.io/langgraph/)
- [LangChain Documentation](https://python.langchain.com/)
- [OpenRouter API](https://openrouter.ai/)

## 🤝 Contribución

Las contribuciones son bienvenidas. Por favor abre un issue o pull request.

## 📄 Licencia

MIT