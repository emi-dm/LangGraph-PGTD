# Ejemplo: Agente LangGraph con Herramientas de Archivos

**Nivel:** Intermedio

Este es un ejemplo completo de un agente LangGraph que puede **leer** y **crear** archivos en el sistema.

## 🎯 Conceptos Clave

| Concepto | Descripción |
|----------|-------------|
| **@tool** | Decorador para definir herramientas |
| **ToolNode** | Nodo preconstruido para ejecutar herramientas |
| **bind_tools()** | Vincula herramientas al LLM |
| **Aristas condicionales** | El LLM decide cuándo usar herramientas |

## 🚀 Características

- **Leer archivos**: El agente puede leer cualquier archivo del sistema
- **Crear archivos**: Puede crear archivos nuevos con contenido personalizado
- **Decisión autónoma**: El LLM decide cuándo usar herramientas basándose en la consulta del usuario

## 📁 Estructura del Proyecto

```
ejemplo-agente-con-tools/
├── src/
│   └── agente.py          # Código del agente con herramientas
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
│ Agente  │◄────────┐
└────┬────┘         │
     │              │
     ▼              │
┌─────────┐         │
│Herramientas├──────┘
└────┬────┘
     │
     ▼
┌─────────┐
│   END   │
└─────────┘
```

## 📖 Siguiente Paso

Continúa con [ejemplo-agente-con-interrupciones](../ejemplo-agente-con-interrupciones/) para aprender a añadir aprobación humana (Human-in-the-Loop).

Esto iniciará el servidor de desarrollo de LangGraph en `http://localhost:2024`.

### Ejemplos de consultas

Una vez iniciado, puedes probar con estas consultas:

```
"Lee el archivo README.md y hazme un resumen"
```

```
"Crea un archivo llamado notas.txt con el contenido: 'Mi primera nota del agente'"
```

```
"Crea un archivo en output/resultados.txt con una lista de 5 ideas creativas"
```

## 🔧 Herramientas Disponibles

### `leer_archivo(ruta: str)`
Lee el contenido de un archivo dado su ruta.

**Parámetros:**
- `ruta`: Ruta del archivo (absoluta o relativa)

**Ejemplo de uso por el agente:**
```python
leer_archivo("./datos.csv")
```

### `crear_archivo(ruta: str, contenido: str)`
Crea un archivo nuevo con el contenido especificado.

**Parámetros:**
- `ruta`: Ruta donde crear el archivo
- `contenido`: Texto a escribir en el archivo

**Ejemplo de uso por el agente:**
```python
crear_archivo("./output/informe.txt", "Este es el contenido del informe...")
```

## 📊 Flujo del Grafo

```
┌─────────┐
│  START  │
└────┬────┘
     │
     ▼
┌─────────┐     ¿Necesita      ┌─────────────┐
│ Agente  │────herramientas?───▶│ Herramientas│
└────┬────┘                    └──────┬──────┘
     │                                │
     │◀───────────────────────────────┘
     │
     ▼
┌─────────┐
│   END   │
└─────────┘
```

1. El usuario envía un mensaje
2. El **Agente** (LLM) analiza la consulta
3. Si necesita leer/crear archivos → va a **Herramientas**
4. Después de ejecutar herramientas → vuelve al **Agente**
5. El agente responde al usuario con los resultados

## 🔑 Variables de Entorno

| Variable | Descripción | Requerida |
|----------|-------------|-----------|
| `OPENROUTER_API_KEY` | API key de OpenRouter | ✅ Sí |

## 📝 Notas

- Este ejemplo usa OpenRouter como proveedor, pero puedes cambiarlo por cualquier proveedor compatible con LangChain
- Las herramientas trabajan con rutas relativas al directorio donde se ejecuta el agente
- El agente crea directorios automáticamente si no existen al crear archivos

## 🤝 Personalización

Para añadir más herramientas, simplemente:

1. Crea una función decorada con `@tool`
2. Añádela a la lista `herramientas`
3. El agente automáticamente podrá usarla

```python
@tool
def mi_nueva_herramienta(parametro: str) -> str:
    """Descripción de lo que hace la herramienta."""
    # Tu lógica aquí
    return "resultado"

herramientas = [leer_archivo, crear_archivo, mi_nueva_herramienta]
```
