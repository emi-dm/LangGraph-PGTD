# Ejemplo: Sistema de Investigación Académica con Deep Agents

**Nivel:** Avanzado

Este ejemplo demuestra cómo crear un sistema de investigación académica multiagente usando **Deep Agents**, **Semantic Scholar**, **arXiv** y **Langfuse**, donde múltiples subagentes especializados colaboran para buscar, analizar y sintetizar papers académicos en informes de literatura estructurados.

## 🎯 Conceptos Clave del Ejemplo

| Concepto | Descripción |
|----------|-------------|
| **Deep Agents SDK** | Framework para crear agentes complejos con subagentes |
| **Sistema Multiagente** | Múltiples agentes especializados colaborando |
| **Gestión de Contexto** | Offloading, summarización y recuperación automática |
| **Semantic Scholar API** | Búsqueda académica gratuita (200M+ papers) |
| **arXiv API** | Repositorio de preprints académicos |
| **MarkItDown** | Conversión de PDFs a Markdown optimizado para LLMs |
| **Langfuse** | Observabilidad y trazas detalladas de ejecuciones |

## 🧠 Gestión de Contexto

Deep Agents implementa gestión automática de contexto para tareas largas:

| Técnica | Cuándo se activa | Qué hace |
|---------|------------------|-----------|
| **Offloading de resultados** | Resultado > 20k tokens | Guarda en filesystem, reemplaza con referencia |
| **Offloading de inputs** | Contexto > 85% | Trunca writes/antiguos, mantiene referencia a archivo |
| **Summarización** | Sin más offloading posible | Resume historial, guarda original en filesystem |

### Ejemplo práctico

```
Turno 1-10:  Búsqueda de papers (resultados grandes → offload automático)
Turno 11-20: Análisis de papers (contexto crece → offload de inputs antiguos)
Turno 21+:   Síntesis (contexto > 85% → summarización automática)

El agente puede recuperar info previa con read_file cuando la necesita.
```

Más info: [Context Management for Deep Agents](https://blog.langchain.com/context-management-for-deepagents/)

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                    Agente Orquestador                        │
│  (Coordina el flujo de investigación académica)             │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┬───────────────┐
        │               │               │               │
        ▼               ▼               ▼               ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│  Refinador    │ │   Buscador    │ │  Analizador   │ │ Sintetizador  │
│  (Pregunta    │ │ (Semantic     │ │  (Extract     │ │  (Literature  │
│   al usuario) │ │  Scholar +    │ │   Key Info)   │ │   Review)     │
│               │ │  arXiv)       │ │               │ │               │
└───────────────┘ └───────────────┘ └───────────────┘ └───────────────┘
```

### Flujo de trabajo

```
1. Usuario pide investigación
         │
         ▼
2. Refinador analiza tema ──► Pregunta al usuario ──► Confirma términos
         │
         ▼
3. Buscador busca papers con términos refinados
         │
         ▼
4. Analizador extrae información clave
         │
         ▼
5. Sintetizador crea informe final
```

## 🤖 Subagentes

### 1. Refinador (NUEVO)
- Analiza la consulta inicial del usuario
- Identifica si el tema es muy amplio o vago
- Propone términos de búsqueda específicos y alternativas
- Sugiere categorías de arXiv relevantes (cs.SE, cs.AI, cs.CL, etc.)
- **Pregunta al usuario** si quiere refinar antes de proceder

### 2. Buscador
- Busca papers en Semantic Scholar y arXiv con términos refinados
- Descarga PDFs de papers con acceso abierto
- Procesa PDFs con MarkItDown para extraer contenido completo
- Organiza resultados por relevancia

### 3. Analizador
- Analiza metadatos y abstracts de papers
- Procesa PDFs descargados con MarkItDown para análisis profundo
- Extrae métodos, resultados y contribuciones
- Compara enfoques entre papers

### 4. Sintetizador
- Crea informes de literatura estructurados
- Identifica tendencias y gaps de investigación
- Genera referencias formateadas

## 📄 Procesamiento de PDFs con MarkItDown

Este ejemplo utiliza [MarkItDown](https://github.com/microsoft/markitdown) de Microsoft para convertir papers PDF a Markdown optimizado para LLMs.

### Flujo de procesamiento

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Buscar     │ -> │  Descargar  │ -> │  Procesar   │
│  Papers     │    │  PDF        │    │  con MarkItDown │
└─────────────┘    └─────────────┘    └─────────────┘
                                              │
                                              ▼
                                    ┌─────────────┐
                                    │  Markdown   │
                                    │  optimizado │
                                    │  para LLMs  │
                                    └─────────────┘
```

### Ventajas de MarkItDown

- **Preserva estructura**: Mantiene encabezados, listas, tablas y enlaces
- **Token-efficient**: Markdown es altamente eficiente en tokens para LLMs
- **Multi-formato**: Soporta PDF, Word, PowerPoint, Excel, imágenes, etc.
- **Sin dependencias pesadas**: Ligero y fácil de instalar

## 📁 Estructura del Proyecto

```
10-ejemplo-deep-agents-investigador/
├── src/
│   └── agente.py          # Sistema multiagente investigador
├── papers/                 # PDFs descargados (creado automáticamente)
├── informes/               # Informes generados (creado automáticamente)
├── pyproject.toml          # Dependencias
└── README.md               # Este archivo
```

## 🛠️ Instalación

```bash
# Desde la raíz del repositorio
cd ejemplos/10-ejemplo-deep-agents-investigador

# Instalar dependencias (usando uv desde la raíz)
cd ../..
uv sync
```

## 🔑 Variables de Entorno

| Variable | Descripción | Requerida |
|----------|-------------|-----------|
| `OPENROUTER_API_KEY` | API key de OpenRouter | ✅ Sí |
| `OPENROUTER_MODEL` | Modelo a usar (default: openai/gpt-4.1-mini) | Opcional |
| `LANGFUSE_SECRET_KEY` | Secret key de Langfuse | ✅ Sí |
| `LANGFUSE_PUBLIC_KEY` | Public key de Langfuse | ✅ Sí |
| `LANGFUSE_HOST` | URL de Langfuse (default: cloud) | Opcional |

> **Nota:** Semantic Scholar y arXiv son APIs gratuitas que no requieren API key.

## ▶️ Ejecución

**Modo estándar** (genera un informe de ejemplo):

```bash
uv run 10-ejemplo-deep-agents-investigador/src/agente.py
```

**Modo interactivo** (consultas bajo demanda con loading animado):

```bash
uv run 10-ejemplo-deep-agents-investigador/src/agente.py --interactivo
```

### Modo Interactivo

En modo interactivo puedes:
- Escribir consultas de investigación libremente
- El agente **refinará tu consulta** antes de buscar (te preguntará)
- Confirmar con "Si" para proceder con la búsqueda
- Continuar la conversación (mantiene contexto entre turnos)
- Usar comandos especiales:
  - `salir` / `exit` — Terminar la sesión
  - `limpiar` — Borrar papers descargados
  - `listar` — Ver informes generados
  - `nueva` — Empezar una nueva investigación (limpia historial)

```
🔍 Tu consulta: Specification-Driven Development in Software Engineering

🤖 EL AGENTE TIENE UNA PREGUNTA:
══════════════════════════════════════════════════════════════════════
He analizado tu consulta. Propongo buscar con estos términos:
- "Specification-Driven Development"
- "Formal Specification in Software Engineering"
- "Requirements-Driven Development"
- Categorías: cs.SE (Software Engineering)

¿Procedo con estas búsquedas?
──────────────────────────────────────────────────────────────────────
👤 Tu respuesta: Si

⠋ 🔍 Buscando papers académicos...
⠙ 📄 Descargando PDFs...
⠹ 🔬 Analizando contenido...
✅ Investigación completada
```

## 📝 Ejemplo de Uso

```python
from agente import crear_agente_investigador

# Crear el agente
agent = crear_agente_investigador()

# Generar informe de literatura
result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Genera un informe de literatura sobre LangGraph y agentes multiagente"
    }]
})
```

## 📁 Estructura de Salida

Los informes generados se guardan en la carpeta `informes/` con estructura académica formal:

```
informes/
├── langgraph-literature-review.md
├── llm-agents-survey.md
└── ...
```

### Estructura del Informe

Cada informe generado sigue esta estructura académica formal:

```markdown
# Informe de Literatura: [Tema]

**Fecha:** [fecha]
**Fuentes consultadas:** Semantic Scholar, arXiv
**Número de papers analizados:** [número]

---

## Resumen Ejecutivo
## 1. Introducción
   1.1 Contexto y Motivación
   1.2 Objetivos del Informe
   1.3 Alcance y Limitaciones
## 2. Metodología de Búsqueda
   2.1 Fuentes de Datos
   2.2 Criterios de Búsqueda
   2.3 Proceso de Selección
## 3. Marco Teórico
   3.1 Definiciones y Conceptos Clave
   3.2 Evolución Histórica
   3.3 Estado del Arte Actual
## 4. Resultados
   4.1 Tendencia 1
   4.2 Tendencia 2
   4.3 Tabla Comparativa
## 5. Discusión
   5.1 Análisis Comparativo
   5.2 Consensos en la Literatura
   5.3 Disensos y Debates
## 6. Gaps y Oportunidades de Investigación
## 7. Conclusiones
## Referencias (formato APA, numeradas [1], [2], etc.)
## Apéndices
```

### Citas en el texto

Las referencias se citan usando numeración secuencial:
- "Según Vaswani et al. [1], el mecanismo de atención es fundamental..."
- "Estudios recientes [2, 3] demuestran que..."
- "Como señalan Smith et al. [4]..."

## 🔧 Personalización

### Cambiar el modelo LLM

```python
model = ChatOpenAI(
    model="anthropic/claude-3.5-sonnet",  # Usar Claude en lugar de GPT-4
    # ...
)
```

### Agregar nuevas fuentes académicas

```python
def buscar_en_dblp(query: str, max_results: int = 5) -> str:
    """Busca papers en DBLP (ciencias de la computación)."""
    url = f"https://dblp.org/search/publ/api?q={query}&format=json&h={max_results}"
    # ... implementación
```

## 📚 Recursos

- [Deep Agents Documentation](https://docs.langchain.com/oss/python/deepagents/overview)
- [Semantic Scholar API](https://api.semanticscholar.org/)
- [arXiv API](https://info.arxiv.org/help/api/index.html)
- [Langfuse Documentation](https://langfuse.com/docs)
- [OpenRouter Documentation](https://openrouter.ai/docs)

## 🤝 Flujo de Trabajo

1. **Usuario** solicita un informe de literatura sobre un tema
2. **Orquestador** analiza y planifica el flujo de investigación
3. **Buscador** encuentra papers relevantes en Semantic Scholar y arXiv
4. **Analizador** extrae información clave de los papers
5. **Sintetizador** crea el informe de literatura estructurado
6. **Sistema** guarda el informe final en `informes/`

## ⚙️ Diferencias con el Ejemplo 9 (Documentador)

| Aspecto | Ejemplo 9 (Documentador) | Ejemplo 10 (Investigador) |
|---------|--------------------------|---------------------------|
| **Dominio** | Documentación técnica | Investigación académica |
| **Fuentes** | Tavily (web general) | Semantic Scholar + arXiv |
| **Salida** | Documentación Markdown | Informes de literatura |
| **Subagentes** | Investigador, Escritor, Revisor | Buscador, Analizador, Sintetizador |
| **APIs** | Requiere Tavily API key | Gratuitas (sin API key) |
