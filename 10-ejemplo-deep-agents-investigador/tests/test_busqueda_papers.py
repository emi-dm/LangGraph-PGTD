"""
Tests para verificar que la búsqueda y descarga de papers funciona correctamente.

Ejecución:
    # Tests unitarios (con mocks, sin llamadas a APIs reales)
    uv run pytest 10-ejemplo-deep-agents-investigador/tests/test_busqueda_papers.py -v

    # Tests de integración (llamadas reales a APIs)
    uv run pytest 10-ejemplo-deep-agents-investigador/tests/test_busqueda_papers.py -v --run-integration

Tests incluidos:
- Búsqueda en Semantic Scholar (mocked)
- Búsqueda en arXiv (mocked)
- Descarga de PDFs (mocked y real)
- Procesamiento con MarkItDown
- Listado de papers descargados
"""

from agente import (
    PAPERS_DIR,
    buscar_papers_arxiv,
    buscar_papers_semantic_scholar,
    descargar_paper,
    listar_papers_descargados,
    procesar_paper_con_markitdown,
)
import os
import shutil
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Añadir el directorio src al path para importar el agente
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


# =============================================================================
# CONFIGURACIÓN DE PYTEST
# =============================================================================

def pytest_addoption(parser):
    """Añade opción para ejecutar tests de integración."""
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="Ejecutar tests de integración (llamadas reales a APIs)",
    )


def pytest_collection_modifyitems(config, items):
    """Salta tests de integración a menos que se use --run-integration."""
    if not config.getoption("--run-integration"):
        skip_integration = pytest.mark.skip(
            reason="Usa --run-integration para ejecutar tests de integración"
        )
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)


# =============================================================================
# DATOS MOCK PARA TESTS
# =============================================================================

MOCK_SEMANTIC_SCHOLAR_RESPONSE = {
    "data": [
        {
            "title": "Attention Is All You Need",
            "authors": [{"name": "Vaswani"}, {"name": "Shazeer"}, {"name": "Parmar"}],
            "abstract": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks.",
            "citationCount": 120000,
            "year": 2017,
            "url": "https://www.semanticscholar.org/paper/attention-is-all-you-need",
            "openAccessPdf": {"url": "https://arxiv.org/pdf/1706.03762"},
        },
        {
            "title": "BERT: Pre-training of Deep Bidirectional Transformers",
            "authors": [{"name": "Devlin"}, {"name": "Chang"}, {"name": "Lee"}],
            "abstract": "We introduce a new language representation model called BERT.",
            "citationCount": 80000,
            "year": 2018,
            "url": "https://www.semanticscholar.org/paper/bert",
            "openAccessPdf": None,
        },
        {
            "title": "Language Models are Few-Shot Learners",
            "authors": [{"name": "Brown"}, {"name": "Mann"}, {"name": "Ryder"}],
            "abstract": "Recent work has demonstrated substantial gains on many NLP tasks.",
            "citationCount": 25000,
            "year": 2020,
            "url": "https://www.semanticscholar.org/paper/gpt3",
            "openAccessPdf": {"url": "https://arxiv.org/pdf/2005.14165"},
        },
    ]
}

MOCK_ARXIV_RESPONSE = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/1706.03762v7</id>
    <title>Attention Is All You Need</title>
    <summary>The dominant sequence transduction models are based on complex recurrent or convolutional neural networks.</summary>
    <published>2017-06-12T00:00:00Z</published>
    <author><name>Ashish Vaswani</name></author>
    <author><name>Noam Shazeer</name></author>
    <author><name>Niki Parmar</name></author>
  </entry>
  <entry>
    <id>http://arxiv.org/abs/2005.14165v4</id>
    <title>Language Models are Few-Shot Learners</title>
    <summary>Recent work has demonstrated substantial gains on many NLP tasks.</summary>
    <published>2020-05-28T00:00:00Z</published>
    <author><name>Tom B. Brown</name></author>
    <author><name>Benjamin Mann</name></author>
  </entry>
</feed>
"""


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture(autouse=True)
def cleanup_papers():
    """Limpia la carpeta papers antes y después de cada test."""
    if PAPERS_DIR.exists():
        shutil.rmtree(PAPERS_DIR)
    PAPERS_DIR.mkdir(exist_ok=True)
    yield
    if PAPERS_DIR.exists():
        shutil.rmtree(PAPERS_DIR)
    PAPERS_DIR.mkdir(exist_ok=True)


@pytest.fixture
def mock_semantic_scholar():
    """Mock para la API de Semantic Scholar."""
    mock_response = MagicMock()
    mock_response.json.return_value = MOCK_SEMANTIC_SCHOLAR_RESPONSE
    mock_response.raise_for_status = MagicMock()
    return mock_response


@pytest.fixture
def mock_arxiv():
    """Mock para la API de arXiv."""
    mock_response = MagicMock()
    mock_response.text = MOCK_ARXIV_RESPONSE
    mock_response.raise_for_status = MagicMock()
    return mock_response


# =============================================================================
# TESTS DE BÚSQUEDA EN SEMANTIC SCHOLAR (UNITARIOS CON MOCKS)
# =============================================================================

class TestBuscarPapersSemanticScholar:
    """Tests para la búsqueda en Semantic Scholar (usando mocks)."""

    @patch("agente.request_with_retry")
    def test_busqueda_basica(self, mock_request):
        """Verifica que la búsqueda básica retorna resultados."""
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_SEMANTIC_SCHOLAR_RESPONSE
        mock_request.return_value = mock_response

        resultado = buscar_papers_semantic_scholar("LangGraph", max_results=3)

        assert resultado is not None
        assert "Paper 1:" in resultado
        assert "Attention Is All You Need" in resultado
        assert "❌" not in resultado

    @patch("agente.request_with_retry")
    def test_busqueda_retorna_multiples_papers(self, mock_request):
        """Verifica que se retornan múltiples papers."""
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_SEMANTIC_SCHOLAR_RESPONSE
        mock_request.return_value = mock_response

        resultado = buscar_papers_semantic_scholar(
            "large language models", max_results=5)

        assert "Paper 1:" in resultado
        assert "Paper 2:" in resultado
        assert "Paper 3:" in resultado

    @patch("agente.request_with_retry")
    def test_busqueda_incluye_metadatos(self, mock_request):
        """Verifica que los resultados incluyen metadatos básicos."""
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_SEMANTIC_SCHOLAR_RESPONSE
        mock_request.return_value = mock_response

        resultado = buscar_papers_semantic_scholar(
            "transformer architecture", max_results=2)

        assert "**Autores:**" in resultado
        assert "**Año:**" in resultado
        assert "**Citas:**" in resultado
        assert "**URL:**" in resultado
        assert "**Abstract:**" in resultado

    @patch("agente.request_with_retry")
    def test_busqueda_con_rango_anos(self, mock_request):
        """Verifica que el filtro de años funciona."""
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_SEMANTIC_SCHOLAR_RESPONSE
        mock_request.return_value = mock_response

        resultado = buscar_papers_semantic_scholar(
            "GPT", max_results=3, year_range="2023-2024"
        )

        assert resultado is not None
        assert "❌" not in resultado

    @patch("agente.request_with_retry")
    def test_busqueda_query_inexistente(self, mock_request):
        """Verifica comportamiento con query sin resultados."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": []}
        mock_request.return_value = mock_response

        resultado = buscar_papers_semantic_scholar(
            "xyznonexistent", max_results=1)

        assert resultado is not None
        assert "No se encontraron" in resultado

    @patch("agente.request_with_retry")
    def test_busqueda_maneja_error_api(self, mock_request):
        """Verifica manejo de errores de la API."""
        mock_request.side_effect = Exception("Connection error")

        resultado = buscar_papers_semantic_scholar("test", max_results=1)

        assert "❌" in resultado
        assert "Error" in resultado

    def test_busqueda_query_inexistente(self):
        """Verifica comportamiento con query sin resultados."""
        resultado = buscar_papers_semantic_scholar(
            "xyzqwerty123nonexistent456", max_results=1
        )

        # Puede retornar resultados vacíos o un mensaje
        assert resultado is not None


# =============================================================================
# TESTS DE BÚSQUEDA EN ARXIV
# =============================================================================

class TestBuscarPapersArxiv:
    """Tests para la búsqueda en arXiv."""

    def test_busqueda_basica(self):
        """Verifica que la búsqueda básica en arXiv retorna resultados."""
        resultado = buscar_papers_arxiv("machine learning", max_results=3)

        assert resultado is not None
        assert "Paper 1:" in resultado
        assert "❌" not in resultado

    def test_busqueda_incluye_metadatos(self):
        """Verifica que los resultados incluyen metadatos básicos."""
        resultado = buscar_papers_arxiv("neural networks", max_results=2)

        assert "**Autores:**" in resultado
        assert "**Publicado:**" in resultado
        assert "**URL:**" in resultado
        assert "**Abstract:**" in resultado

    def test_busqueda_retorna_url_arxiv(self):
        """Verifica que las URLs son de arXiv."""
        resultado = buscar_papers_arxiv("deep learning", max_results=1)

        assert "arxiv.org" in resultado

    def test_busqueda_orden_relevancia(self):
        """Verifica que el orden por relevancia funciona."""
        resultado = buscar_papers_arxiv(
            "reinforcement learning", max_results=3, sort_by="relevance"
        )

        assert resultado is not None
        assert "Paper 1:" in resultado

    def test_busqueda_orden_fecha(self):
        """Verifica que el orden por fecha funciona."""
        resultado = buscar_papers_arxiv(
            "transformer", max_results=3, sort_by="lastUpdatedDate"
        )

        assert resultado is not None
        assert "Paper 1:" in resultado


# =============================================================================
# TESTS DE DESCARGA DE PDFs
# =============================================================================

class TestDescargarPaper:
    """Tests para la descarga de papers PDF."""

    def test_descargar_pdf_arxiv(self):
        """Verifica que se puede descargar un PDF de arXiv."""
        # Usar un paper conocido de arXiv (Attention Is All You Need)
        pdf_url = "https://arxiv.org/pdf/1706.03762"
        resultado = descargar_paper(pdf_url, "attention-is-all-you-need.pdf")

        assert "✅" in resultado
        assert PAPERS_DIR.exists()
        assert (PAPERS_DIR / "attention-is-all-you-need.pdf").exists()

    def test_pdf_se_guarda_correctamente(self):
        """Verifica que el PDF descargado tiene contenido."""
        pdf_url = "https://arxiv.org/pdf/1706.03762"
        descargar_paper(pdf_url, "test-paper.pdf")

        pdf_path = PAPERS_DIR / "test-paper.pdf"
        assert pdf_path.exists()
        assert pdf_path.stat().st_size > 1000  # Al menos 1KB

    def test_descarga_con_nombre_automatico(self):
        """Verifica que se genera nombre automático si no se proporciona."""
        pdf_url = "https://arxiv.org/pdf/1706.03762"
        resultado = descargar_paper(pdf_url)

        assert "✅" in resultado
        # Debe haber creado algún archivo PDF
        pdfs = list(PAPERS_DIR.glob("*.pdf"))
        assert len(pdfs) >= 1

    def test_descarga_url_invalida(self):
        """Verifica manejo de errores con URL inválida."""
        resultado = descargar_paper("https://invalid-url-12345.com/fake.pdf")

        assert "❌" in resultado


# =============================================================================
# TESTS DE PROCESAMIENTO CON MARKITDOWN
# =============================================================================

class TestProcesarPaperConMarkitdown:
    """Tests para el procesamiento de PDFs con MarkItDown."""

    @pytest.fixture(autouse=True)
    def setup_pdf(self):
        """Descarga un PDF de prueba antes de cada test."""
        pdf_url = "https://arxiv.org/pdf/1706.03762"
        descargar_paper(pdf_url, "test-markitdown.pdf")
        yield

    def test_procesar_pdf_basico(self):
        """Verifica que se puede procesar un PDF a Markdown."""
        resultado = procesar_paper_con_markitdown("test-markitdown.pdf")

        assert resultado is not None
        assert "📄" in resultado
        assert "convertido a Markdown" in resultado
        assert "❌" not in resultado

    def test_markdown_contiene_contenido(self):
        """Verifica que el Markdown generado tiene contenido real."""
        resultado = procesar_paper_con_markitdown("test-markitdown.pdf")

        # Debe contener texto del paper
        assert len(resultado) > 500  # Al menos 500 caracteres

    def test_procesar_pdf_inexistente(self):
        """Verifica manejo de errores con PDF inexistente."""
        resultado = procesar_paper_con_markitdown("no-existe.pdf")

        assert "❌" in resultado
        assert "no encontrado" in resultado.lower()


# =============================================================================
# TESTS DE LISTADO DE PAPERS
# =============================================================================

class TestListarPapersDescargados:
    """Tests para el listado de papers descargados."""

    def test_listar_sin_papers(self):
        """Verifica mensaje cuando no hay papers."""
        resultado = listar_papers_descargados()

        assert "No hay papers" in resultado

    def test_listar_con_papers(self):
        """Verifica que se listan los papers descargados."""
        # Descargar un PDF de prueba
        pdf_url = "https://arxiv.org/pdf/1706.03762"
        descargar_paper(pdf_url, "paper-listado-test.pdf")

        resultado = listar_papers_descargados()

        assert "paper-listado-test.pdf" in resultado
        assert "MB" in resultado  # Debe mostrar el tamaño


# =============================================================================
# TESTS DE INTEGRACIÓN
# =============================================================================

class TestIntegracion:
    """Tests de integración que verifican el flujo completo."""

    def test_flujo_busqueda_descarga_procesamiento(self):
        """Verifica el flujo completo: buscar -> descargar -> procesar."""
        # 1. Buscar papers
        resultado_busqueda = buscar_papers_semantic_scholar(
            "attention mechanism", max_results=1
        )
        assert "Paper 1:" in resultado_busqueda

        # 2. Descargar un paper conocido
        resultado_descarga = descargar_paper(
            "https://arxiv.org/pdf/1706.03762",
            "integration-test.pdf"
        )
        assert "✅" in resultado_descarga

        # 3. Procesar con MarkItDown
        resultado_procesamiento = procesar_paper_con_markitdown(
            "integration-test.pdf")
        assert "📄" in resultado_procesamiento
        assert len(resultado_procesamiento) > 500

        # 4. Listar papers
        resultado_listado = listar_papers_descargados()
        assert "integration-test.pdf" in resultado_listado

    def test_busqueda_dual_semantic_y_arxiv(self):
        """Verifica que ambas fuentes de búsqueda funcionan."""
        query = "reinforcement learning"

        resultado_semantic = buscar_papers_semantic_scholar(
            query, max_results=2)
        resultado_arxiv = buscar_papers_arxiv(query, max_results=2)

        assert "Paper 1:" in resultado_semantic
        assert "Paper 1:" in resultado_arxiv
        assert "❌" not in resultado_semantic
        assert "❌" not in resultado_arxiv


# =============================================================================
# MAIN (para ejecutar directamente)
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
