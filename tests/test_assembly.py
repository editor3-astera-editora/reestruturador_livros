# tests/test_assembly.py
import pytest
from unittest.mock import patch, MagicMock
from src.assembly import document_assembler

@pytest.fixture
def processed_content_data():
    """Fornece uma estrutura de dados de conteúdo processado para o teste."""
    return {
        "Unidade 1": {
            "theme": "Tema da unidade 1.",
            "chapters": {
                "Capítulo 1": {
                    "content": {
                        "Seção 1.1": "Conteúdo da seção 1.1."
                    },
                    "summary": "Resumo do capítulo 1."
                }
            }
        }
    }

@patch('src.assembly.document_assembler.docx.Document')
def test_create_final_document(MockDocxDocument, processed_content_data, tmp_path):
    """
    Testa se o documento final é construído corretamente, chamando os métodos
    da biblioteca docx com os dados corretos.
    """
    mock_doc_instance = MockDocxDocument.return_value
    output_path = tmp_path / "final.docx"
    
    document_assembler.create_final_document(processed_content_data, output_path)
    
    # Verifica as chamadas para adicionar títulos e parágrafos
    mock_doc_instance.add_heading.assert_any_call("Unidade 1", level=1)
    mock_doc_instance.add_heading.assert_any_call("Temáticas da unidade", level=2)
    mock_doc_instance.add_paragraph.assert_any_call("Tema da unidade 1.")
    
    mock_doc_instance.add_heading.assert_any_call("Capítulo 1", level=2)
    mock_doc_instance.add_heading.assert_any_call("Seção 1.1", level=3)
    mock_doc_instance.add_paragraph.assert_any_call("Conteúdo da seção 1.1.")
    
    mock_doc_instance.add_heading.assert_any_call("Resumindo", level=3)
    mock_doc_instance.add_paragraph.assert_any_call("Resumo do capítulo 1.")
    
    # Verifica se o método save foi chamado com o caminho correto
    mock_doc_instance.save.assert_called_once_with(output_path)