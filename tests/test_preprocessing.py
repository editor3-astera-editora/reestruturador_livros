# tests/test_preprocessing.py
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from langchain_core.documents import Document
from src.preprocessing import document_handler

@pytest.fixture
def mock_markdown_content():
    """Fornece um conteúdo de markdown de exemplo para os testes."""
    return """
# Unidade 1: Título da Unidade 1

## Seção 1.1: Título da Seção 1.1
Conteúdo da seção 1.1.

## Seção 1.2: Título da Seção 1.2
Conteúdo da seção 1.2.

# Unidade 2: Título da Unidade 2

## Seção 2.1: Título da Seção 2.1
Conteúdo da seção 2.1.
"""

@patch('src.preprocessing.document_handler.pypandoc')
def test_convert_docx_to_markdown(mock_pypandoc, tmp_path):
    """
    Testa se a função de conversão chama o pypandoc com os argumentos corretos.
    """
    input_file = tmp_path / "test.docx"
    output_file = tmp_path / "test.md"
    
    document_handler.convert_docx_to_markdown(input_file, output_file)
    
    mock_pypandoc.convert_file.assert_called_once_with(
        source_file=str(input_file),
        to='markdown',
        outputfile=str(output_file),
        extra_args=['--wrap=none']
    )

def test_load_and_split_by_structure(mock_markdown_content, tmp_path):
    """
    Testa se o arquivo markdown é carregado e dividido corretamente em Documentos.
    """
    md_path = tmp_path / "test.md"
    md_path.write_text(mock_markdown_content, encoding='utf-8')
    
    documents = document_handler.load_and_split_by_structure(md_path)
    
    assert len(documents) == 3
    assert isinstance(documents[0], Document)
    
    # Verifica o conteúdo e metadados do primeiro documento
    assert documents[0].page_content == "Conteúdo da seção 1.1."
    assert documents[0].metadata['title'] == "# Unidade 1: Título da Unidade 1\n## Seção 1.1: Título da Seção 1.1"

    # Verifica o conteúdo e metadados do terceiro documento
    assert documents[2].page_content == "Conteúdo da seção 2.1."
    assert documents[2].metadata['title'] == "# Unidade 2: Título da Unidade 2\n## Seção 2.1: Título da Seção 2.1"