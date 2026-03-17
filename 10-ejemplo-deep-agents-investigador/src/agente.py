"""
Sistema multiagente de investigación académica con Deep Agents.

Este script demuestra cómo crear un sistema de investigación académica
usando Deep Agents, donde múltiples subagentes especializados colaboran
para buscar, analizar y sintetizar papers académicos.

Ejecución:
    uv run 10-ejemplo-deep-agents-investigador/src/agente.py

Modo interactivo:
    uv run 10-ejemplo-deep-agents-investigador/src/agente.py --interactivo

Conceptos demostrados:
- Deep Agents SDK con create_deep_agent
- Sistema multiagente con subagentes especializados
- Gestión automática de contexto (offloading, summarización)
- Filesystem integrado para persistencia de datos grandes
- Integración con Semantic Scholar API (gratuita)
- Integración con arXiv API (gratuita)
- Integración con Langfuse para observabilidad
- Uso de OpenRouter como proveedor de modelos
- Generación de informes de literatura académica
- Procesamiento de PDFs con MarkItDown
- Modo interactivo para consultas bajo demanda

Gestión de contexto (Deep Agents):
- Offloading automático: Resultados de tools > 20k tokens se guardan en filesystem
- Summarización: Cuando el contexto supera el 85%, se resume automáticamente
- Recuperación: El agente puede leer archivos previos con read_file cuando necesita info

Arquitectura del sistema:
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

Flujo de trabajo:
1. Refinador analiza la consulta y propone términos específicos
2. Usuario confirma los términos de búsqueda
3. Buscador encuentra papers relevantes en Semantic Scholar y arXiv
4. Analizador extrae información clave de los papers
5. Sintetizador crea el informe de literatura estructurado
6. Sistema guarda el informe final en informes/
"""

import itertools
import os
import sys
import threading
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv
from deepagents import create_deep_agent
from langchain_openai import ChatOpenAI
from langfuse.langchain import CallbackHandler
from markitdown import MarkItDown

# Cargar variables de entorno
load_dotenv(override=True)

# Configuración de directorios
PAPERS_DIR = Path("papers")
INFORMES_DIR = Path("informes")

# Crear directorios si no existen
PAPERS_DIR.mkdir(exist_ok=True)
INFORMES_DIR.mkdir(exist_ok=True)

# Inicializar MarkItDown para conversión de PDFs a Markdown
md_converter = MarkItDown(enable_plugins=False)


# =============================================================================
# SPINNER PARA ANIMACIÓN EN CLI
# =============================================================================

class Spinner:
    """Animación de spinner para indicar progreso en la terminal."""

    FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    MESSAGES = [
        "🔍 Buscando papers academicos...",
        "📄 Descargando PDFs...",
        "🔬 Analizando contenido...",
        "📊 Procesando datos...",
        "✍️ Generando informe...",
        "🔎 Investigando fuentes...",
        "📚 Compilando referencias...",
        "🧠 Pensando...",
    ]

    def __init__(self, message: str = "Procesando"):
        self.message = message
        self._running = False
        self._thread = None
        self._current_message = message

    def _animate(self):
        """Función interna que ejecuta la animación."""
        i = 0
        msg_idx = 0
        msg_counter = 0
        while self._running:
            frame = self.FRAMES[i % len(self.FRAMES)]
            sys.stdout.write(f"\r  {frame} {self._current_message}")
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1
            msg_counter += 1
            # Cambiar mensaje cada 3 segundos (30 iteraciones * 0.1s)
            if msg_counter >= 30:
                msg_counter = 0
                msg_idx = (msg_idx + 1) % len(self.MESSAGES)
                self._current_message = self.MESSAGES[msg_idx]

    def start(self, message: str = None):
        """Inicia la animación del spinner."""
        if message:
            self._current_message = message
        self._running = True
        self._thread = threading.Thread(target=self._animate, daemon=True)
        self._thread.start()

    def stop(self, final_message: str = None):
        """Detiene la animación del spinner."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=0.5)
        # Limpiar la línea del spinner
        sys.stdout.write("\r" + " " * 80 + "\r")
        sys.stdout.flush()
        if final_message:
            print(f"  ✅ {final_message}")

    def update(self, message: str):
        """Actualiza el mensaje del spinner."""
        self._current_message = message


# Context manager para usar el spinner fácilmente
class SpinnerContext:
    """Context manager para el spinner."""

    def __init__(self, message: str = "Procesando"):
        self.spinner = Spinner(message)

    def __enter__(self):
        self.spinner.start()
        return self.spinner

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.spinner.stop("Error durante el procesamiento")
        else:
            self.spinner.stop("Proceso completado")
        return False


# =============================================================================
# HELPER: REQUESTS CON RETRY Y BACKOFF EXPONENCIAL
# =============================================================================

def request_with_retry(
    url: str,
    params: dict = None,
    max_retries: int = 3,
    initial_delay: float = 2.0,
    timeout: int = 30,
) -> requests.Response:
    """Realiza una petición HTTP con retry y backoff exponencial.

    Maneja el rate limiting (429) y errores temporales de red.

    Args:
        url: URL a la que hacer la petición.
        params: Parámetros de la query string.
        max_retries: Número máximo de reintentos (default: 3).
        initial_delay: Delay inicial en segundos (default: 2.0).
        timeout: Timeout de la petición en segundos (default: 30).

    Returns:
        Response de la petición.

    Raises:
        requests.HTTPError: Si la petición falla después de todos los reintentos.
    """
    delay = initial_delay
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            response = requests.get(url, params=params, timeout=timeout)

            # Si es rate limit (429), esperar y reintentar
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", delay))
                print(
                    f"  ⏳ Rate limit alcanzado. Esperando {retry_after}s... (intento {attempt + 1}/{max_retries + 1})")
                time.sleep(retry_after)
                delay *= 2  # Backoff exponencial
                continue

            response.raise_for_status()
            return response

        except requests.exceptions.RequestException as e:
            last_exception = e
            if attempt < max_retries:
                print(
                    f"  ⚠️  Error de conexión. Reintentando en {delay}s... (intento {attempt + 1}/{max_retries + 1})")
                time.sleep(delay)
                delay *= 2  # Backoff exponencial
            else:
                raise

    # Si llegamos aquí, todos los reintentos fallaron
    raise last_exception


# =============================================================================
# TOOLS PERSONALIZADAS - BÚSQUEDA ACADÉMICA
# =============================================================================

def buscar_papers_semantic_scholar(
    query: str,
    max_results: int = 5,
    year_range: Optional[str] = None,
) -> str:
    """Busca papers académicos en Semantic Scholar.

    Semantic Scholar es un motor de búsqueda académico gratuito con API
    que indexa más de 200 millones de papers.

    Args:
        query: Consulta de búsqueda (tema, concepto, tecnología).
        max_results: Número máximo de resultados (default: 5).
        year_range: Rango de años opcional (ej: "2020-2024").

    Returns:
        Lista de papers encontrados con título, autores, abstract y citas.
    """
    try:
        url = "https://api.semanticscholar.org/graph/v1/paper/search"
        params = {
            "query": query,
            "limit": max_results,
            "fields": "title,authors,abstract,citationCount,year,url,openAccessPdf",
        }

        if year_range:
            params["year"] = year_range

        response = request_with_retry(
            url, params=params, max_retries=3, initial_delay=2.0)
        data = response.json()

        papers = data.get("data", [])
        if not papers:
            return "No se encontraron papers para la consulta."

        formatted = []
        for i, paper in enumerate(papers, 1):
            authors = ", ".join([a.get("name", "")
                                for a in paper.get("authors", [])[:3]])
            if len(paper.get("authors", [])) > 3:
                authors += " et al."

            formatted.append(f"""
## Paper {i}: {paper.get('title', 'Sin título')}

**Autores:** {authors}
**Año:** {paper.get('year', 'N/A')}
**Citas:** {paper.get('citationCount', 0)}
**URL:** {paper.get('url', 'N/A')}

**Abstract:**
{paper.get('abstract', 'No disponible')[:500]}...
""")

        return "\n---\n".join(formatted)

    except Exception as e:
        return f"❌ Error en búsqueda: {type(e).__name__}: {e}"


def buscar_papers_arxiv(
    query: str,
    max_results: int = 5,
    sort_by: str = "relevance",
) -> str:
    """Busca papers en arXiv.

    arXiv es un repositorio de preprints en física, matemáticas, ciencias
    de la computación y más.

    Args:
        query: Consulta de búsqueda.
        max_results: Número máximo de resultados (default: 5).
        sort_by: Ordenar por "relevance" o "lastUpdatedDate".

    Returns:
        Lista de papers de arXiv encontrados.
    """
    try:
        url = "http://export.arxiv.org/api/query"
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max_results,
            "sortBy": sort_by,
            "sortOrder": "descending",
        }

        response = request_with_retry(
            url, params=params, max_retries=2, initial_delay=1.0)

        # Parsear XML de arXiv
        root = ET.fromstring(response.text)

        ns = {"atom": "http://www.w3.org/2005/Atom"}
        entries = root.findall("atom:entry", ns)

        if not entries:
            return "No se encontraron papers en arXiv."

        formatted = []
        for i, entry in enumerate(entries, 1):
            title = entry.find(
                "atom:title", ns).text.strip().replace("\n", " ")
            summary = entry.find("atom:summary", ns).text.strip()[:500]
            published = entry.find("atom:published", ns).text[:10]
            link = entry.find("atom:id", ns).text

            authors = [a.find("atom:name", ns).text for a in entry.findall(
                "atom:author", ns)]
            authors_str = ", ".join(authors[:3])
            if len(authors) > 3:
                authors_str += " et al."

            formatted.append(f"""
## Paper {i}: {title}

**Autores:** {authors_str}
**Publicado:** {published}
**URL:** {link}

**Abstract:**
{summary}...
""")

        return "\n---\n".join(formatted)

    except Exception as e:
        return f"❌ Error en búsqueda arXiv: {type(e).__name__}: {e}"


def analizar_paper(paper_url: str) -> str:
    """Analiza un paper académico y extrae información clave.

    Args:
        paper_url: URL del paper (Semantic Scholar o arXiv).

    Returns:
        Análisis estructurado del paper.
    """
    try:
        # Intentar obtener información de Semantic Scholar
        if "semanticscholar.org" in paper_url or "arxiv.org" in paper_url:
            # Extraer ID del paper
            if "arxiv.org" in paper_url:
                paper_id = paper_url.split("/abs/")[-1]
                api_url = f"https://api.semanticscholar.org/graph/v1/paper/ArXiv:{paper_id}"
            else:
                paper_id = paper_url.split("/paper/")[-1]
                api_url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}"

            response = request_with_retry(
                api_url,
                params={
                    "fields": "title,authors,abstract,citationCount,year,references,tldr"},
                max_retries=2,
                initial_delay=1.5,
            )
            paper = response.json()

            tldr_text = "No disponible"
            if paper.get("tldr") and isinstance(paper["tldr"], dict):
                tldr_text = paper["tldr"].get("text", "No disponible")

            return f"""
## Análisis del Paper

**Título:** {paper.get('title', 'N/A')}
**Año:** {paper.get('year', 'N/A')}
**Citas:** {paper.get('citationCount', 0)}

### Abstract
{paper.get('abstract', 'No disponible')}

### TL;DR
{tldr_text}

### Referencias principales
{len(paper.get('references', []))} referencias encontradas.
"""
        else:
            return "❌ URL no soportada. Use URLs de Semantic Scholar o arXiv."

    except Exception as e:
        return f"❌ Error al analizar paper: {type(e).__name__}: {e}"


def descargar_paper(pdf_url: str, filename: Optional[str] = None) -> str:
    """Descarga un paper en formato PDF desde una URL.

    Args:
        pdf_url: URL directa al PDF del paper.
        filename: Nombre del archivo (opcional). Si no se proporciona,
                  se extrae de la URL.

    Returns:
        Ruta al archivo descargado o mensaje de error.
    """
    try:
        if not filename:
            # Extraer nombre de archivo de la URL
            filename = pdf_url.split("/")[-1]
            if not filename.endswith(".pdf"):
                filename += ".pdf"

        filepath = PAPERS_DIR / filename

        # Descargar el PDF
        response = requests.get(pdf_url, timeout=60, stream=True)
        response.raise_for_status()

        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return f"✅ Paper descargado exitosamente en: {filepath}"

    except Exception as e:
        return f"❌ Error al descargar paper: {type(e).__name__}: {e}"


def procesar_paper_con_markitdown(filename: str) -> str:
    """Procesa un paper PDF y lo convierte a Markdown usando MarkItDown.

    MarkItDown es una utilidad de Microsoft para convertir archivos
    (PDF, Word, PowerPoint, etc.) a Markdown optimizado para LLMs.

    Args:
        filename: Nombre del archivo PDF en la carpeta papers/.

    Returns:
        Contenido del paper convertido a Markdown.
    """
    try:
        if not filename.endswith(".pdf"):
            filename += ".md"

        filepath = PAPERS_DIR / filename

        if not filepath.exists():
            return f"❌ Archivo no encontrado: {filepath}"

        # Convertir PDF a Markdown usando MarkItDown
        result = md_converter.convert(str(filepath))

        return f"📄 Contenido de {filename} (convertido a Markdown):\n\n{result.text_content}"

    except Exception as e:
        return f"❌ Error al procesar paper: {type(e).__name__}: {e}"


def listar_papers_descargados() -> str:
    """Lista todos los papers descargados en la carpeta papers/.

    Returns:
        Lista de archivos PDF disponibles.
    """
    try:
        pdf_files = list(PAPERS_DIR.glob("*.pdf"))

        if not pdf_files:
            return "📁 No hay papers descargados en la carpeta papers/"

        formatted = ["📁 Papers descargados:\n"]
        for i, pdf_file in enumerate(pdf_files, 1):
            size_mb = pdf_file.stat().st_size / (1024 * 1024)
            formatted.append(f"{i}. {pdf_file.name} ({size_mb:.2f} MB)")

        return "\n".join(formatted)

    except Exception as e:
        return f"❌ Error al listar papers: {type(e).__name__}: {e}"


def preguntar_al_usuario(pregunta: str) -> str:
    """Hace una pregunta al usuario y espera su respuesta.

    Esta herramienta permite al agente interactuar con el usuario
    para refinar consultas o pedir aclaraciones antes de proceder.

    Args:
        pregunta: La pregunta a hacer al usuario.

    Returns:
        La respuesta del usuario.
    """
    print("\n" + "=" * 70)
    print("🤖 EL AGENTE TIENE UNA PREGUNTA:")
    print("=" * 70)
    print()
    print(pregunta)
    print()
    print("-" * 70)

    respuesta = input("👤 Tu respuesta: ").strip()

    if not respuesta:
        return "El usuario no proporcionó respuesta. Procede con tu mejor criterio."

    return f"Respuesta del usuario: {respuesta}"


def guardar_informe(filename: str, content: str) -> str:
    """Guarda un informe de investigación en el sistema de archivos.

    Args:
        filename: Nombre del archivo (debe terminar en .md).
        content: Contenido del informe en formato Markdown.

    Returns:
        Confirmación de guardado o mensaje de error.
    """
    try:
        os.makedirs("informes", exist_ok=True)

        if not filename.endswith(".md"):
            filename += ".md"

        filepath = os.path.join("informes", filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        return f"✅ Informe guardado exitosamente en: {filepath}"

    except Exception as e:
        return f"❌ Error al guardar informe: {type(e).__name__}: {e}"


def leer_informe(filename: str) -> str:
    """Lee un informe de investigación del sistema de archivos.

    Args:
        filename: Nombre del archivo a leer.

    Returns:
        Contenido del informe o mensaje de error.
    """
    try:
        if not filename.endswith(".md"):
            filename += ".md"

        filepath = os.path.join("informes", filename)

        if not os.path.exists(filepath):
            return f"❌ Archivo no encontrado: {filepath}"

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        return f"📄 Contenido de {filepath}:\n\n{content}"

    except Exception as e:
        return f"❌ Error al leer informe: {type(e).__name__}: {e}"


# =============================================================================
# PROMPTS DE SISTEMA PARA SUBAGENTES
# =============================================================================

BUSCADOR_PROMPT = """\
Eres un investigador académico especializado en encontrar papers relevantes.

Tu rol es:
1. Buscar papers académicos usando buscar_papers_semantic_scholar y buscar_papers_arxiv
2. Encontrar los papers más relevantes y citados sobre el tema
3. Descargar papers PDF cuando estén disponibles usando descargar_paper
4. Procesar papers descargados usando procesar_paper_con_markitdown
5. Organizar los resultados por relevancia y fecha

Directrices:
- Realiza búsquedas en ambas fuentes (Semantic Scholar y arXiv)
- Prioriza papers con alto número de citas
- Incluye papers recientes (últimos 3-5 años) cuando sea relevante
- Descarga los PDFs de los papers más relevantes cuando tengan acceso abierto
- Procesa los PDFs con MarkItDown para extraer el contenido completo
- Estructura tu informe con los papers más relevantes primero
- Incluye abstracts para ayudar a evaluar relevancia
- Usa diferentes queries para obtener cobertura completa del tema

Cuando termines tu búsqueda, proporciona un informe estructurado con:
- Lista de papers encontrados ordenados por relevancia
- Resumen de cada paper con abstract
- Métricas clave (año, citas)
- URLs para acceso directo
- Estado de descarga y procesamiento de PDFs
"""


REFINADOR_PROMPT = """\
Eres un especialista en refinar consultas de investigación académica.

Tu rol es ayudar al usuario a definir mejor su tema de investigación ANTES de buscar papers.

Cuando recibas una consulta de investigación:
1. Analiza el tema propuesto por el usuario
2. Identifica si el tema es muy amplio o vago
3. Propón términos de búsqueda más específicos y alternativas
4. Sugiere categorías de arXiv relevantes (ej: cs.SE para Software Engineering, cs.AI para Inteligencia Artificial, cs.CL para Procesamiento de Lenguaje Natural)
5. Pregunta al usuario si quiere refinar la búsqueda antes de proceder

Categorías de arXiv comunes:
- cs.AI: Inteligencia Artificial
- cs.CL: Procesamiento de Lenguaje Natural (Computation and Language)
- cs.SE: Ingeniería de Software
- cs.LG: Aprendizaje Automático (Machine Learning)
- cs.CV: Visión por Computador
- cs.RO: Robótica
- cs.IR: Recuperación de Información
- cs.HCI: Interacción Humano-Computadora

Formato de respuesta:
1. **Análisis del tema**: Explica brevemente el tema
2. **Problemas identificados**: ¿Es muy amplio? ¿Es ambiguo?
3. **Propuesta de refinamiento**:
   - Términos de búsqueda sugeridos (3-5 alternativas)
   - Categorías de arXiv relevantes
   - Filtros temporales sugeridos
4. **Pregunta al usuario**: ¿Quieres proceder con estos términos o prefieres ajustar algo?

Ejemplo:
Usuario: "Quiero investigar sobre Specification-Driven Development"
Respuesta: El término "Specification-Driven Development" es específico pero puede no capturar todos los papers relevantes. Sugiero buscar también:
- "specification-based development"
- "requirements-driven development" 
- "formal specification software"
- Categorías: cs.SE (Software Engineering), cs.AI (AI)
- ¿Procedo con estas búsquedas?
"""


ANALIZADOR_PROMPT = """\
Eres un analizador académico especializado en extraer información clave de papers.

Tu rol es:
1. Analizar papers individuales usando analizar_paper
2. Procesar PDFs descargados usando procesar_paper_con_markitdown para obtener contenido completo
3. Extraer métodos, resultados y contribuciones principales
4. Identificar fortalezas y limitaciones
5. Comparar enfoques entre diferentes papers

Criterios de análisis:
- **Problema**: ¿Qué problema aborda el paper?
- **Método**: ¿Qué enfoque o metodología propone?
- **Resultados**: ¿Qué resultados obtiene?
- **Contribución**: ¿Cuál es la contribución principal?
- **Limitaciones**: ¿Cuáles son las limitaciones reconocidas?

Directrices:
- Primero usa analizar_paper para obtener metadatos y abstract
- Luego usa procesar_paper_con_markitdown para leer el contenido completo del PDF
- Usa listar_papers_descargados para ver qué papers están disponibles
- Extrae secciones clave: introducción, metodología, resultados, conclusiones
- Identifica tablas y figuras importantes mencionadas en el texto

Cuando termines tu análisis, proporciona:
- Resumen ejecutivo de cada paper
- Tabla comparativa de métodos
- Identificación de patrones comunes
- Evaluación de calidad y relevancia
"""


SINTETIZADOR_PROMPT = """\
Eres un escritor académico especializado en crear informes de literatura formales y detallados.

Tu rol es:
1. Sintetizar información de múltiples papers en un informe coherente y formal
2. Crear informes de literatura bien estructurados en Markdown académico
3. Identificar tendencias, gaps y direcciones futuras
4. Citar correctamente todas las fuentes usando numeración [1], [2], etc.
5. Incluir una sección de referencias completa al final
6. Guardar los informes usando guardar_informe

ESTRUCTURA OBLIGATORIA DEL INFORME:
```markdown
# Informe de Literatura: [Tema]

**Fecha:** [fecha actual]
**Fuentes consultadas:** Semantic Scholar, arXiv
**Número de papers analizados:** [número]

---

## Resumen Ejecutivo

[3-5 párrafos con visión general de los hallazgos principales. Debe ser completo pero conciso.]

---

## 1. Introducción

### 1.1 Contexto y Motivación
[Descripción del contexto del área de investigación y por qué es relevante]

### 1.2 Objetivos del Informe
[Qué se pretende cubrir en este informe]

### 1.3 Alcance y Limitaciones
[Qué se incluye y qué se excluye, limitaciones de la búsqueda]

---

## 2. Metodología de Búsqueda

### 2.1 Fuentes de Datos
- **Semantic Scholar:** Base de datos académica con más de 200 millones de papers
- **arXiv:** Repositorio de preprints en ciencias de la computación y áreas relacionadas

### 2.2 Criterios de Búsqueda
- **Queries utilizadas:** [lista de términos de búsqueda]
- **Categorías:** [categorías de arXiv utilizadas]
- **Período temporal:** [rango de años si se especificó]
- **Criterios de inclusión:** [qué papers se incluyeron]

### 2.3 Proceso de Selección
[Descripción de cómo se seleccionaron los papers más relevantes]

---

## 3. Marco Teórico

### 3.1 Definiciones y Conceptos Clave
[Definiciones formales de los conceptos principales]

### 3.2 Evolución Histórica
[Breve historia del área de investigación]

### 3.3 Estado del Arte Actual
[Descripción del estado actual de la investigación]

---

## 4. Resultados

### 4.1 Tendencia 1: [Nombre de la tendencia]
[Descripción detallada con análisis profundo]

**Papers relevantes:**
- [Autor et al.] ([año]) - "[Título del paper]" [1
- [Autor et al.] ([año]) - "[Título del paper]" [2]

**Hallazgos principales:**
[Descripción detallada de los hallazgos]

### 4.2 Tendencia 2: [Nombre de la tendencia]
[Descripción detallada con análisis profundo]

**Papers relevantes:**
- [Autor et al.] ([año]) - "[Título del paper]" [3]

**Hallazgos principales:**
[Descripción detallada de los hallazgos]

### 4.3 Tendencia 3: [Nombre de la tendencia]
[Descripción detallada con análisis profundo]

**Papers relevantes:**
- [Autor et al.] ([año]) - "[Título del paper]" [4]

**Hallazgos principales:**
[Descripción detallada de los hallazgos]

### 4.4 Tabla Comparativa

| Paper | Año | Método | Contribución Principal | Citas |
|-------|-----|--------|------------------------|-------|
| [Título] | [año] | [método] | [contribución] | [número] |

---

## 5. Discusión

### 5.1 Análisis Comparativo
[Comparación formal entre los diferentes enfoques encontrados]

### 5.2 Consensos en la Literatura
[Acuerdos entre los diferentes autores y papers]

### 5.3 Disensos y Debates
[Desacuerdos o diferentes perspectivas en la literatura]

### 5.4 Implicaciones Prácticas
[Qué implicaciones tienen estos hallazgos para la práctica]

---

## 6. Gaps y Oportunidades de Investigación

### 6.1 Áreas No Exploradas
[Gaps identificados en la literatura actual]

### 6.2 Direcciones Futuras
[Potenciales líneas de investigación futuras]

### 6.3 Desafíos Abiertos
[Problemas que aún no tienen solución]

---

## 7. Conclusiones

### 7.1 Hallazgos Principales
[Resumen de los hallazgos más importantes]

### 7.2 Recomendaciones
[Recomendaciones basadas en la evidencia encontrada]

### 7.3 Reflexiones Finales
[Consideraciones finales sobre el estado de la investigación]

---

## Referencias

[1] Autor, A., Autor, B., & Autor, C. (Año). Título del paper. *Revista/Conferencia*, Volumen(Número), Páginas. URL

[2] Autor, D., & Autor, E. (Año). Título del paper. *Revista/Conferencia*, Volumen(Número), Páginas. URL

[3] Autor, F. et al. (Año). Título del paper. *arXiv preprint arXiv:XXXX.XXXXX*. URL

[4] Autor, G. et al. (Año). Título del paper. En *Proceedings of Conference Name* (pp. XXX-XXX). URL

---

## Apéndices

### Apéndice A: Queries de Búsqueda Completas
[Lista completa de todas las queries utilizadas]

### Apéndice B: Papers Descartados
[Lista de papers relevantes que no se incluyeron y razones]
```

REGLAS OBLIGATORIAS:
1. SIEMPRE cita las fuentes en el texto usando [número], por ejemplo: "Según Smith et al. [1], ..."
2. SIEMPRE incluye la sección de Referencias al final con TODOS los papers mencionados
3. Usa formato APA para las referencias
4. Cada referencia debe tener: Autores, Año, Título, Fuente, URL
5. Los números de referencia deben ser secuenciales [1], [2], [3], etc.
6. Incluye tablas comparativas cuando sea útil
7. Usa un tono académico formal pero accesible
8. Estructura el documento con secciones numeradas (1., 1.1, 1.2, etc.)
9. Incluye metadatos al inicio (fecha, fuentes, número de papers)
10. Señala limitaciones de la revisión de forma explícita
"""


ORQUESTADOR_PROMPT = """\
Eres el agente orquestador de un sistema de investigación académica multiagente.

Tu rol es coordinar el flujo de trabajo de investigación, delegando tareas
a subagentes especializados según sea necesario.

GESTIÓN DE CONTEXTO:
- Deep Agents gestiona automáticamente el contexto (offloading, summarización)
- Los resultados grandes de tools se guardan automáticamente en el filesystem
- Si necesitas información previa, usa read_file para recuperarla
- Los informes generados se guardan en informes/ y puedes leerlos con leer_informe
- Los papers descargados se guardan en papers/ y puedes listarlos con listar_papers_descargados

FLUJO DE TRABAJO OBLIGATORIO (sigue estos pasos en orden):

1. **Refinamiento** (PRIMER PASO - OBLIGATORIO para temas nuevos):
   - Si el usuario presenta un NUEVO TEMA de investigación, delega al refinador
   - El refinador analizará la consulta y propondrá términos específicos
   - El refinador usará preguntar_al_usuario para confirmar con el usuario
   - Espera la confirmación del usuario antes de continuar

2. **Confirmación del usuario**:
   - Si el usuario responde "Si", "Sí", "Procede", "Ok", "Adelante" o similar,
     DEBES proceder inmediatamente con la búsqueda usando los términos refinados
   - NO vuelvas a preguntar ni a refinar si el usuario ya confirmó
   - Usa los términos que el refinador propuso en el paso anterior

3. **Búsqueda**: Solo después de confirmar los términos con el usuario
   - Delega al buscador con los términos refinados
   - Usa buscar_papers_semantic_scholar para Semantic Scholar
   - Usa buscar_papers_arxiv para arXiv (incluye categorías sugeridas como cs.SE)
   - Descarga PDFs con descargar_paper
   - Procesa PDFs con procesar_paper_con_markitdown

4. **Análisis**: Delega al analizador para examinar papers específicos
   - Analiza los papers más relevantes encontrados
   - Extrae información clave y compara enfoques

5. **Síntesis**: Delega al sintetizador para crear el informe final
   - Integra hallazgos de búsqueda y análisis
   - Crea informe estructurado en Markdown
   - Guarda el informe en la carpeta informes/

Instrucciones:
- Si el usuario confirma con "Si" o similar, procede DIRECTAMENTE con la búsqueda
- NO vuelvas a delegar al refinador si ya refinaste el tema
- Analiza la solicitud del usuario para determinar el alcance de la investigación
- Planifica el flujo de trabajo apropiado
- Delega tareas a los subagentes especializados
- Coordina la entrega del informe final
- Informa al usuario sobre el progreso y resultado

Tipos de informes que puedes generar:
- Revisiones de literatura completas
- Encuestas de estado del arte
- Análisis comparativo de enfoques
- Identificación de tendencias emergentes
- Mapeo de gaps de investigación
"""


# =============================================================================
# DEFINICIÓN DE SUBAGENTES
# =============================================================================

subagents = [
    {
        "name": "refinador",
        "description": "Especialista en refinar consultas de investigación. Analiza el tema, propone términos de búsqueda específicos y confirma con el usuario antes de proceder.",
        "system_prompt": REFINADOR_PROMPT,
        "tools": [preguntar_al_usuario],
    },
    {
        "name": "buscador",
        "description": "Especialista en búsqueda académica. Busca papers en Semantic Scholar y arXiv, descarga PDFs y los procesa con MarkItDown.",
        "system_prompt": BUSCADOR_PROMPT,
        "tools": [
            buscar_papers_semantic_scholar,
            buscar_papers_arxiv,
            descargar_paper,
            procesar_paper_con_markitdown,
            listar_papers_descargados,
        ],
    },
    {
        "name": "analizador",
        "description": "Especialista en análisis de papers. Analiza papers individuales y procesa PDFs descargados con MarkItDown.",
        "system_prompt": ANALIZADOR_PROMPT,
        "tools": [
            analizar_paper,
            procesar_paper_con_markitdown,
            listar_papers_descargados,
        ],
    },
    {
        "name": "sintetizador",
        "description": "Especialista en síntesis académica. Crea informes de literatura estructurados.",
        "system_prompt": SINTETIZADOR_PROMPT,
        "tools": [guardar_informe, leer_informe],
    },
]


# =============================================================================
# CONFIGURACIÓN DE MODELO CON OPENROUTER
# =============================================================================

def crear_modelo():
    """Crea el modelo LLM usando OpenRouter.

    OpenRouter permite acceder a múltiples modelos (GPT-4, Claude, Llama, etc.)
    a través de una API unificada.

    Returns:
        Instancia de ChatOpenAI configurada para OpenRouter.
    """
    return ChatOpenAI(
        model=os.environ.get("OPENROUTER_MODEL", "openai/gpt-4.1"),
        api_key=os.environ["OPENROUTER_API_KEY"],
        base_url="https://openrouter.ai/api/v1",
        temperature=0.3,  # Baja temperatura para mayor precisión en investigación
    )


# =============================================================================
# CREACIÓN DEL AGENTE PRINCIPAL
# =============================================================================

def crear_agente_investigador():
    """Crea y retorna el agente investigador multiagente.

    Returns:
        Agente Deep Agent configurado para investigación académica con Langfuse.
    """
    # Crear modelo con OpenRouter
    model = crear_modelo()

    # Crear agente con Deep Agents
    agent = create_deep_agent(
        name="investigador-academico",
        model=model,
        tools=[
            buscar_papers_semantic_scholar,
            buscar_papers_arxiv,
            descargar_paper,
            procesar_paper_con_markitdown,
            listar_papers_descargados,
            analizar_paper,
            guardar_informe,
            leer_informe,
        ],
        system_prompt=ORQUESTADOR_PROMPT,
        subagents=subagents,
    )

    return agent


def obtener_callbacks_langfuse():
    """Crea callbacks de Langfuse para observabilidad.

    Returns:
        Lista con el CallbackHandler de Langfuse.
    """
    langfuse_handler = CallbackHandler()
    return [langfuse_handler]


# =============================================================================
# MODO INTERACTIVO
# =============================================================================

def modo_interactivo():
    """Ejecuta el agente en modo interactivo, permitiendo consultas bajo demanda."""
    print("=" * 70)
    print("📚 SISTEMA MULTIAGENTE DE INVESTIGACIÓN ACADÉMICA - MODO INTERACTIVO")
    print("=" * 70)
    print()

    # Verificar variables de entorno
    if not os.environ.get("OPENROUTER_API_KEY"):
        print("❌ Error: OPENROUTER_API_KEY no encontrada en variables de entorno")
        print("   Configura tu API key de OpenRouter en el archivo .env")
        return

    # Crear agente
    print("🔧 Inicializando agente investigador...")
    agent = crear_agente_investigador()

    # Configurar callbacks de Langfuse si están disponibles
    config = {"recursion_limit": 50}
    if os.environ.get("LANGFUSE_SECRET_KEY") and os.environ.get("LANGFUSE_PUBLIC_KEY"):
        config["callbacks"] = obtener_callbacks_langfuse()
        print("📊 Langfuse habilitado para observabilidad")

    print()
    print("✅ Agente listo. Escribe tu consulta de investigación.")
    print("   Comandos especiales:")
    print("   - 'salir' o 'exit' para terminar")
    print("   - 'limpiar' para borrar papers descargados")
    print("   - 'listar' para ver informes generados")
    print("   - 'nueva' para empezar una nueva investigación")
    print("-" * 70)
    print()

    # Mantener historial de mensajes para contexto entre turnos
    messages_history = []
    thread_id = "interactive-session-1"

    while True:
        try:
            # Leer consulta del usuario
            consulta = input("🔍 Tu consulta: ").strip()

            # Comandos especiales
            if consulta.lower() in ["salir", "exit", "quit", "q"]:
                print("\n👋 ¡Hasta luego!")
                break

            if consulta.lower() == "limpiar":
                import shutil
                if PAPERS_DIR.exists():
                    shutil.rmtree(PAPERS_DIR)
                    PAPERS_DIR.mkdir(exist_ok=True)
                    print("🗑️  Papers descargados eliminados.")
                else:
                    print("📁 No hay papers para eliminar.")
                continue

            if consulta.lower() == "listar":
                informes = list(INFORMES_DIR.glob("*.md"))
                if informes:
                    print("\n📄 Informes generados:")
                    for i, inf in enumerate(informes, 1):
                        print(f"   {i}. {inf.name}")
                else:
                    print("\n📁 No hay informes generados aún.")
                print()
                continue

            if consulta.lower() == "nueva":
                messages_history = []
                print("\n🔄 Nueva investigación iniciada. Historial limpiado.")
                print()
                continue

            if not consulta:
                continue

            # Añadir mensaje del usuario al historial
            messages_history.append({"role": "user", "content": consulta})

            # Ejecutar consulta con spinner y contexto
            print()
            spinner = Spinner("🔍 Iniciando investigación...")
            spinner.start()

            try:
                # Configurar con thread_id para mantener contexto
                run_config = {
                    **config, "configurable": {"thread_id": thread_id}}

                result = agent.invoke(
                    {"messages": messages_history},
                    config=run_config,
                )
                spinner.stop("Investigación completada")

                # Actualizar historial con los mensajes del resultado
                if result and "messages" in result:
                    messages_history = result["messages"]

            except Exception as e:
                spinner.stop(f"Error: {e}")
                raise

            # Mostrar solo los mensajes nuevos (últimos del asistente)
            print("\n" + "=" * 70)
            print("📊 RESULTADO")
            print("=" * 70)
            print()

            # Mostrar solo la última respuesta del asistente
            assistant_messages = [
                m for m in result.get("messages", [])
                if hasattr(m, "content") and m.content and getattr(m, "type", None) == "ai"
            ]

            if assistant_messages:
                print(assistant_messages[-1].content)
            else:
                # Fallback: mostrar todos los mensajes
                for message in result.get("messages", []):
                    if hasattr(message, "content") and message.content:
                        print(message.content)
                        print()

            print("-" * 70)
            print()

        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"\n❌ Error: {type(e).__name__}: {e}")
            print()


# =============================================================================
# EJECUCIÓN PRINCIPAL
# =============================================================================

def main():
    """Función principal que ejecuta el sistema de investigación."""
    # Verificar si se solicita modo interactivo
    if "--interactivo" in sys.argv or "-i" in sys.argv:
        modo_interactivo()
        return

    # Modo estándar (ejemplo predefinido)
    print("=" * 70)
    print("📚 SISTEMA MULTIAGENTE DE INVESTIGACIÓN ACADÉMICA")
    print("=" * 70)
    print()

    # Verificar variables de entorno
    if not os.environ.get("OPENROUTER_API_KEY"):
        print("❌ Error: OPENROUTER_API_KEY no encontrada en variables de entorno")
        print("   Configura tu API key de OpenRouter en el archivo .env")
        return

    # Crear agente
    print("🔧 Inicializando agente investigador...")
    agent = crear_agente_investigador()

    # Configurar callbacks de Langfuse si están disponibles
    config = {"recursion_limit": 50}
    if os.environ.get("LANGFUSE_SECRET_KEY") and os.environ.get("LANGFUSE_PUBLIC_KEY"):
        config["callbacks"] = obtener_callbacks_langfuse()
        print("📊 Langfuse habilitado para observabilidad")

    print()
    print("🔍 Iniciando investigación sobre: LangGraph y agentes multiagente")
    print("-" * 70)
    print()

    # Ejemplo de uso con loading animado
    loading_active = True
    loading_messages = [
        "🔍 Buscando papers en Semantic Scholar",
        "📚 Buscando papers en arXiv",
        "📥 Descargando PDFs",
        "📄 Procesando documentos con MarkItDown",
        "🔬 Analizando papers",
        "✍️  Sintetizando informe",
        "💾 Guardando resultados",
    ]
    loading_idx = [0]

    def animate_loading():
        """Animación de loading en el terminal."""
        spinner = itertools.cycle(
            ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"])
        while loading_active:
            msg = loading_messages[loading_idx[0] % len(loading_messages)]
            frame = next(spinner)
            print(f"\r{frame} {msg}...", end="", flush=True)
            time.sleep(0.1)
        print("\r" + " " * 80 + "\r", end="")  # Limpiar línea

    # Iniciar animación en hilo separado
    loading_thread = threading.Thread(target=animate_loading, daemon=True)
    loading_thread.start()

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": """Genera un informe de literatura sobre LangGraph y 
            sistemas de agentes multiagente. Incluye:
            1. Los papers más relevantes y citados
            2. Principales enfoques y arquitecturas
            3. Aplicaciones prácticas
            4. Tendencias actuales y direcciones futuras
            
            Guarda el informe como 'langgraph-literature-review.md'""",
                }
            ]
        },
        config=config,
    )

    # Detener animación
    loading_active = False
    loading_thread.join(timeout=1)

    print()
    print("=" * 70)
    print("✅ Investigación completada!")
    print(f"📄 Informe guardado en: informes/langgraph-literature-review.md")
    print("=" * 70)


if __name__ == "__main__":
    main()
