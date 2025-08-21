import pypandoc 
import re 
from pathlib import Path 
from typing import List 
from langchain_core.documents import Document 
from src.utils.logger import logger 

import docx 
from docx.document import Document as DocumentClass 
from docx.oxml.table import CT_Tbl 
from docx.oxml.text.paragraph import CT_P

def remove_section_from_docx(doc: DocumentClass, section_title: str):
    """
    Encontra um título de seção e remove todo o conteúdo a partir dele.
    """
    logger.info(f"Procurando e removendo a seção: '{section_title}'")
    elements_to_remove = []
    found_section = False 

    # Itera sobre todos os elementos do corpo do documento (parágrafos e tabelas)
    for element in doc.element.body:
        if found_section:
            elements_to_remove.append(element)
        elif isinstance(element, CT_P):
            p = docx.text.paragraph.Paragraph(element, doc)
            if section_title.lower() in p.text.lower():
                found_section = True 
                elements_to_remove.append(element)
        
    if found_section:
        for element in elements_to_remove:
            doc.element.body.remove(element)
        logger.info(f"Seção '{section_title}' removida com sucesso.")
    else:
        logger.warning(f"A seção '{section_title}' não foi encontrada no documento.")    

def remove_image_urls_from_docx(doc: DocumentClass):
    """
    Remove parágrafos que contêm URLs de imagens e a linha de fonte correspondente.
    """
    logger.info("Removendo URLs de imagens e fontes do documento...")
    paragraphs_to_remove = []

    for p in doc.paragraphs:
        # Verifica se o parágrafo contém uma URL
        if re.search(r'https?://\S+', p.text):
            paragraphs_to_remove.append(p)
        # Verifica se o parágrafo começa com "Fonte:"
        elif p.text.strip().lower().startswith('fonte:'):
            paragraphs_to_remove.append(p)

    for p in paragraphs_to_remove:
        # A remoção de um parágrafo é feita acessando o elemento XML pai
        parent_element = p._p.getparent()
        if parent_element is not None:
            parent_element.remove(p._p)
            
    logger.info(f"{len(paragraphs_to_remove)} parágrafos contendo URLs/fontes foram removidos.")

def convert_docx_to_markdown(input_path: Path, output_path: Path, intermediate_dir: Path):
    """Converte um arquivo .docx para Markdown usando pandoc."""
    logger.info(f"Convertendo '{input_path.name}' para Markdown...")

    # 1. Carregar o documento 
    doc = docx.Document(input_path)

    # 2. Aplicar as limpezas 
    remove_section_from_docx(doc, "Exercícios resolvidos")
    remove_image_urls_from_docx(doc)

    # 3. Salva um arquivo .docx limpo temporariamente 
    cleaned_docx_path = intermediate_dir / "cleaned_document.docx"
    doc.save(cleaned_docx_path)
    logger.info(f"Documento limpo salvo temporariamente em '{cleaned_docx_path}'")

    # 4. Converter o documento limpo para Markdown
    logger.info(f"Convertendo documento limpo para Markdown...")

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