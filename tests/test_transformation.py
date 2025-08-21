# tests/test_transformation.py
import pytest
import json
from unittest.mock import patch, MagicMock
from langchain_core.documents import Document
from langchain_core.messages import AIMessage

from src.transformation import structure_mapper, content_rewriter, summary_generator

def setup_llm_mock(MockChatOpenAI, response_content: str):
    """
    Configura o mock para a classe ChatOpenAI.
    Isso garante que, quando a instância do LLM for chamada dentro da chain,
    ela retorne um objeto AIMessage, que é o comportamento real.
    """
    mock_llm_instance = MockChatOpenAI.return_value
    
    # Configura o que a chamada ao método .invoke() da instância do LLM deve retornar
    mock_llm_instance.invoke.return_value = AIMessage(content=response_content)
    
    # A análise do erro "ChatOpenAI()()" sugere que a própria instância do mock
    # pode ser chamada como uma função. Configuramos seu retorno também por segurança.
    mock_llm_instance.return_value = AIMessage(content=response_content)


@patch('src.transformation.structure_mapper.ChatOpenAI')
def test_generate_structure_map(MockChatOpenAI, tmp_path):
    """Testa a geração do mapa de estrutura, mockando a resposta do LLM."""
    # O conteúdo que o LLM "retornaria", incluindo os marcadores que o código irá limpar
    mock_response_with_backticks = '''
    ```json
    {
      "Unidade 1": {
        "Capítulo 1": ["## 1.1 Seção A"]
      }
    }
    ```
    '''
    setup_llm_mock(MockChatOpenAI, mock_response_with_backticks)
    
    md_path = tmp_path / "fake.md"
    md_path.write_text("# Unidade 1\n## 1.1 Seção A\nConteúdo.", encoding='utf-8')
    
    output_path = tmp_path / "map.json"
    result = structure_mapper.generate_structure_map(md_path, output_path)
    
    # Asserts
    assert "Unidade 1" in result
    assert output_path.exists()
    # Verifica se o JSON salvo no arquivo está correto
    expected_json = {"Unidade 1": {"Capítulo 1": ["## 1.1 Seção A"]}}
    assert json.loads(output_path.read_text(encoding='utf-8')) == expected_json


@patch('src.transformation.content_rewriter.ChatOpenAI')
def test_rewrite_chunk(MockChatOpenAI):
    """Testa a reescrita de um chunk de texto."""
    setup_llm_mock(MockChatOpenAI, "Texto formal reescrito.")
    
    mock_retriever = MagicMock()
    mock_retriever.invoke.return_value = [Document(page_content="Contexto relevante.")]
    
    result = content_rewriter.rewrite_chunk("texto informal.", mock_retriever)
    
    mock_retriever.invoke.assert_called_once_with("texto informal.")
    assert result == "Texto formal reescrito."


@patch('src.transformation.summary_generator.ChatOpenAI')
def test_generate_chapter_summary(MockChatOpenAI):
    """Testa a geração de resumo de capítulo."""
    setup_llm_mock(MockChatOpenAI, "Este é o resumo do capítulo.")
    
    mock_retriever = MagicMock()
    
    result = summary_generator.generate_chapter_summary("Conteúdo completo do capítulo.", mock_retriever)
    
    assert result == "Este é o resumo do capítulo."