import pypandoc 
import re 
from pathlib import Path 
from typing import List 
from langchain_core.documents import Document 
from src.utils.logger import logger 

def convert_docx_to_markdown(input_path: Path, output_path: Path):
    """Converte um arquivo .docx para Markdown usando pandoc."""
    logger.info(f"Convertendo '{input_path.name}' para Markdown...")
    try:
        pypandoc.convert_file(
            source_file=str(input_path),
            to='markdown',
            outputfile=str(output_path),
            extra_args=['--wrap=none'] # evita quebra de linhas indesejadas 
        )
        logger.info(f"Arquivo Markdown salvo em '{output_path}'")
    except Exception as e:
        logger.error(f"Falha ao converter DOCX para Markdown. Certifique-se que o Pandoc está instalado. Erro: {e}")
        raise

def load_and_split_by_structure(markdown_path: Path) -> List[Document]:
    """
    Carrega um arquivo Markdown e divide em Documentos com base em sua estrutura
    de cabeçalhos (#, ##). Cada seção se torna um Documento.
    """
    logger.info(f"Carregando e estruturando o arquivo Markdown: '{markdown_path.name}'")
    with open(markdown_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Divide o conteúdo por títulos de Unidade (começando com '#')
    unit_splits = re.split(r'(^#\s.*)', content, flags=re.MULTILINE)
    documents = []

    # O primeiro elemento pode ser vazio 
    if unit_splits[0].strip() == '':
        unit_splits = unit_splits[1:]
    
    for i in range(0, len(unit_splits), 2):
        unit_title = unit_splits[i].strip()
        unit_content = unit_splits[i+1]

        # Divide o conteúdo da unidade por seções (começando com '## ')
        section_splits = re.split(r'(^##\s.*)', unit_content, flags=re.MULTILINE)

        if section_splits[0].strip() == '':
            section_splits = section_splits[1:]
        
        for j in range(0, len(section_splits), 2):
            section_title = section_splits[j].strip()
            section_content = section_splits[j+1].strip()

            # Remove o título do conteúdo para evitar duplicação
            full_title = f"{unit_title}\n{section_title}"

            doc = Document(
                page_content=section_content,
                metadata={"source": str(markdown_path), "title": full_title}
            )
            documents.append(doc)

    logger.info(f"Documento dividido em {len(documents)} seções lógicas.")
    return documents