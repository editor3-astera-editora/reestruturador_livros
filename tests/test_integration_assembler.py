# tests/test_integration_assembler.py
import pytest
import docx
from pathlib import Path
from src.assembly import document_assembler
from config import settings

@pytest.fixture
def sample_rich_content():
    """
    Cria uma estrutura de dados de exemplo com conteúdo rico em Markdown
    para testar a conversão completa e a formatação.
    """
    # Conteúdo gerado pela LLM, com subtítulos, bullets, negrito e uma tabela
    chapter_content = """
Este é o primeiro parágrafo do conteúdo do capítulo. Ele deve ser renderizado como texto normal.

### Propriedades dos Materiais

Este parágrafo introduz as propriedades. A seguir, uma lista das mais importantes:
- **Resistência Mecânica:** Capacidade de suportar cargas sem deformação ou falha.
- *Durabilidade:* Habilidade de resistir ao desgaste, corrosão e deterioração ao longo do tempo.

#### Tipos de Aço

Existem vários tipos de aço utilizados, cada um com uma aplicação específica.

A tabela a seguir compara dois tipos comuns:

| Característica | Aço Carbono | Aço Inoxidável |
| :--- | :--- | :--- |
| Custo | Baixo | Alto |
| Resistência à Corrosão | Baixa | Alta |
| Aplicação Comum | Estruturas de edifícios | Fachadas e cozinhas |

Este é o parágrafo final da seção, concluindo o raciocínio.
"""
    
    return {
        "Unidade 1: Teste de Formatação": {
            "theme": "Esta é a temática da Unidade 1, usada para testar a renderização de títulos de nível 2.",
            "chapters": {
                "Capítulo 1: Teste Completo de Elementos": {
                    "content": chapter_content,
                    "curiosity": "O bambu pode crescer até 91 cm em um único dia e é mais forte que o aço em termos de resistência à tração.",
                    "summary": "Este capítulo testou a renderização de subtítulos, listas, negrito, itálico e tabelas."
                }
            }
        }
    }

def test_final_docx_formatting_with_pandoc(sample_rich_content, tmp_path):
    """
    Teste de integração que executa o processo de montagem final para
    validar a conversão de Markdown para estilos do Word via pandoc.
    """
    # Garante que o reference.docx real exista
    reference_doc_path = settings.BASE_DIR / "config" / "reference.docx"
    assert reference_doc_path.exists(), f"ARQUIVO DE REFERÊNCIA NÃO ENCONTRADO em {reference_doc_path}. Crie este arquivo para que o teste funcione."

    output_docx_path = tmp_path / "VALIDACAO_FORMATACAO.docx"

    # Executa a função de montagem final
    document_assembler.create_final_document(sample_rich_content, output_docx_path)

    # --- Verificações Automatizadas ---
    assert output_docx_path.exists(), "O arquivo .docx de saída não foi criado."
    assert output_docx_path.stat().st_size > 0, "O arquivo .docx de saída está vazio."

    # --- Verificação Manual (A mais importante) ---
    print("\n\n" + "="*80)
    print("[VALIDAÇÃO VISUAL NECESSÁRIA]")
    print("Teste de integração de formatação concluído.")
    print(f"Abra o seguinte arquivo gerado para verificar o resultado:")
    print(f"==> {output_docx_path}")
    print("\nVerifique os seguintes pontos no documento Word:")
    print("  1. Tabela de Conteúdos: Deve estar no início e conter todos os títulos e subtítulos.")
    print("  2. Estilos de Título: 'Unidade 1' (Título 1), 'Capítulo 1' (Título 2), 'Propriedades...' (Título 3), 'Tipos de Aço' (Título 4).")
    print("  3. Lista: Deve ser uma lista de bullet points nativa do Word.")
    print("  4. Formatação de Texto: 'Resistência Mecânica' deve estar em negrito e 'Durabilidade' em itálico.")
    print("  5. Tabela: Deve ser uma tabela do Word, não texto simples.")
    print("="*80 + "\n")