# LangGraph-PGTD

Repositorio de ejemplos progresivos para aprender a construir agentes con LangGraph, desde lo más básico hasta patrones avanzados.

## 📚 Ejemplos Disponibles

| Ejemplo | Nivel | Descripción |
|---------|-------|-------------|
| [ejemplo-agente-basico](./ejemplos/ejemplo-agente-basico/) | Principiante | Agente simple sin herramientas |
| [ejemplo-agente-con-tools](./ejemplos/ejemplo-agente-con-tools/) | Intermedio | Agente con herramientas de archivos |
| [ejemplo-agente-con-interrupciones](./ejemplos/ejemplo-agente-con-interrupciones/) | Avanzado | Human-in-the-Loop con interrupciones |
| [ejemplo-agente-con-memoria](./ejemplos/ejemplo-agente-con-memoria/) | Intermedio | Memoria a corto plazo con InMemorySaver |
| [ejemplo-agente-con-memoria-sqlite](./ejemplos/ejemplo-agente-con-memoria-sqlite/) | Intermedio | Memoria persistente con SQLite |
| [ejemplo-agente-con-streaming](./ejemplos/ejemplo-agente-con-streaming/) | Intermedio | Streaming de tokens en tiempo real |
| [ejemplo-agente-con-langfuse](./ejemplos/ejemplo-agente-con-langfuse/) | Intermedio | Observabilidad con Langfuse |
| [ejemplo-deep-agents-documentador](./ejemplos/ejemplo-deep-agents-documentador/) | Avanzado | Sistema multiagente documentador |

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
   cd ejemplos/ejemplo-agente-basico
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
    ├── ejemplo-agente-basico/
    ├── ejemplo-agente-con-tools/
    ├── ejemplo-agente-con-interrupciones/
    ├── ejemplo-agente-con-memoria/
    ├── ejemplo-agente-con-memoria-sqlite/
    ├── ejemplo-agente-con-streaming/
    ├── ejemplo-agente-con-langfuse/
    └── ejemplo-deep-agents-documentador/
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