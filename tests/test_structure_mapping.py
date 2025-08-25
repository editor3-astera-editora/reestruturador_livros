# tests/test_structure_mapping.py
import pytest
from unittest.mock import patch
from src.transformation import structure_mapper

@pytest.fixture
def sample_markdown_content():
    """Fornece um conteúdo de markdown de exemplo com múltiplas unidades."""
    return """
# Unidade 1: Fundamentos
## 1.1 Tópico A
Conteúdo A.
## 1.2 Tópico B
Conteúdo B.

# Unidade 2: Avançado
## 2.1 Tópico C
Conteúdo C.
## 2.2 Tópico D
Conteúdo D.
"""

@patch('src.transformation.structure_mapper.invoke_llm_with_tracking')
def test_generate_structure_map_unit_by_unit(mock_invoke_llm, sample_markdown_content, tmp_path):
    """
    Testa se o mapeador de estrutura processa cada unidade separadamente
    e monta o dicionário final corretamente.
    """
    # Simula a resposta da LLM para cada unidade
    def mock_llm_response(chain, params, task_name):
        if "Unidade 1" in task_name:
            return '''
            {
              "Capítulo 1": ["## 1.1 Tópico A"],
              "Capítulo 2": ["## 1.2 Tópico B"],
              "Capítulo 3": [],
              "Capítulo 4": []
            }
            '''
        elif "Unidade 2" in task_name:
            return '''
            {
              "Capítulo 1": ["## 2.1 Tópico C", "## 2.2 Tópico D"],
              "Capítulo 2": [],
              "Capítulo 3": [],
              "Capítulo 4": []
            }
            '''
        return "{}"

    mock_invoke_llm.side_effect = mock_llm_response
    
    output_path = tmp_path / "structure_map.json"

    # Executa a função a ser testada
    result_map = structure_mapper.generate_structure_map(sample_markdown_content, output_path)

    # --- Verificações Corrigidas ---
    # 1. Verifica se o mock foi chamado duas vezes (uma para cada unidade)
    assert mock_invoke_llm.call_count == 2, "A LLM não foi chamada para cada unidade separadamente."

    # 2. Verifica se a estrutura do mapa final está correta, usando as chaves completas
    assert "Unidade 1: Fundamentos" in result_map
    assert "Unidade 2: Avançado" in result_map
    assert "Capítulo 1" in result_map["Unidade 1: Fundamentos"]
    assert "Capítulo 1" in result_map["Unidade 2: Avançado"]
    
    # 3. Verifica o conteúdo do mapeamento, usando as chaves completas
    assert result_map["Unidade 1: Fundamentos"]["Capítulo 2"] == ["## 1.2 Tópico B"]
    assert len(result_map["Unidade 2: Avançado"]["Capítulo 1"]) == 2

    print("\nTeste da divisão de capítulos passou. A lógica de processar unidade por unidade está funcionando.")