# tests/test_integration_assembler.py
import pytest
import docx
from pathlib import Path
from src.assembly import document_assembler
from config import settings

@pytest.fixture
def sample_processed_content():
    """
    Cria uma estrutura de dados de exemplo com conteúdo rico em Markdown
    para testar a conversão completa.
    """
    chapter_content = """
Este é o primeiro parágrafo do conteúdo do capítulo. Ele deve ser renderizado como texto normal.

#### Este é um subtópico de nível 4
Este parágrafo está sob um subtópico interno e deve ter um recuo ou estilo diferente.

Aqui está uma lista de itens importantes:
- **Item em negrito:** Descrição do primeiro item.
- *Item em itálico:* Descrição do segundo item.
- Terceiro item normal.

A seguir, uma tabela comparativa gerada pela LLM:

| Característica | Opção A | Opção B |
| :--- | :--- | :--- |
| Custo | Baixo | Alto |
| Durabilidade | Média | Alta |
| Manutenção | Frequente | Rara |

Este é o parágrafo final da seção, concluindo o raciocínio.
"""
    
    return {
        "Unidade 1": {
            "theme": "Esta é a temática da Unidade 1.",
            "chapters": {
                "Capítulo 1: Título do Capítulo": {
                    "content": chapter_content,
                    "curiosity": "O bambu pode crescer até 91 cm em um único dia.",
                    "summary": "Este capítulo introduziu a formatação rica, incluindo subtópicos, listas e tabelas."
                }
            }
        }
    }

def test_full_assembly_and_pandoc_conversion(sample_processed_content, tmp_path):
    """
    Teste de integração que executa o processo de montagem e conversão final,
    gerando um arquivo .docx real para inspeção.
    """
    # Garante que um dummy reference.docx exista para o pandoc não falhar.
    # Para o teste real, ele usará o que estiver em config/reference.docx
    reference_doc_path = settings.BASE_DIR / "config" / "reference.docx"
    if not reference_doc_path.exists():
        # Cria um dummy se não existir, para o teste não quebrar.
        dummy_doc = docx.Document()
        dummy_doc.save(reference_doc_path)

    output_docx_path = tmp_path / "test_output.docx"

    # Executa a função que estamos testando
    document_assembler.create_final_document(sample_processed_content, output_docx_path)

    # --- Verificações Automatizadas ---
    # 1. Verifica se o arquivo .docx de saída foi realmente criado.
    assert output_docx_path.exists(), "O arquivo .docx de saída não foi criado."

    # 2. Verifica se o arquivo não está vazio.
    assert output_docx_path.stat().st_size > 0, "O arquivo .docx de saída está vazio."

    # --- Verificação Manual (a mais importante) ---
    print(f"\n[VALIDAÇÃO MANUAL NECESSÁRIA]")
    print(f"Teste de integração concluído. O arquivo de saída foi gerado em:")
    print(f"{output_docx_path}")
    print("Abra este arquivo no Word para verificar se a formatação está correta:")
    print("  - Tabela de Conteúdos no início.")
    print("  - Títulos e subtítulos com os estilos do seu reference.docx.")
    print("  - Listas de bullet points formatadas corretamente.")
    print("  - Texto em **negrito** e *itálico* renderizado corretamente.")
    print("  - A tabela Markdown foi convertida para uma tabela do Word.")