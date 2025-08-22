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
        if re.search(r'https?://\S+', p.text):
            paragraphs_to_remove.append(p)
        elif p.text.strip().lower().startswith('fonte:'):
            paragraphs_to_remove.append(p)

    for p in paragraphs_to_remove:
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
            source_file=str(cleaned_docx_path),
            to='markdown',
            outputfile=str(output_path),
            extra_args=['--wrap=none'] # evita quebra de linhas indesejadas 
        )
        logger.info(f"Arquivo Markdown salvo em '{output_path}'")
    except Exception as e:
        logger.error(f"Falha ao converter DOCX para Markdown. Certifique-se que o Pandoc está instalado. Erro: {e}")
        raise

def preprocess_markdown_headings(content: str) -> str:
    """
    Corrige o Markdown para usar # e ## ao invés de ** para títulos.
    """
    logger.info("Pré-processando Markdown para corrigir cabeçalhos...")
    lines = content.split('\n')
    processed_lines = []
    for line in lines:
        stripped_line = line.strip()

        # Procura por linhas que são SÓ negrito (ex: **UNIDADE 1**)
        match = re.fullmatch(r'\*\*(.*?)\*\*', stripped_line)
        if match: 
            inner_text = match.group(1).strip()
            # Se for um título de Unidade, usa #
            if inner_text.lower().startswith('unidade'):
                processed_lines.append(f'# {inner_text}')
            # Para outros títulos em negrito, usa ##
            else:
                processed_lines.append(f'## {inner_text}')
        else:
            processed_lines.append(line)
    
    return "\n".join(processed_lines)

def load_and_split_by_structure(content: str, source_name: str) -> List[Document]:
    """
    Divide o conteúdo de uma string Markdown em Documentos, associando o texto
    ao último cabeçalho encontrado.
    """
    logger.info(f"Estruturando o arquivo Markdown: '{source_name}'")

    lines = content.split('\n')
    sections = []
    current_content_lines = []
    current_title = ""
    unit_title = ""

    for line in lines:
        stripped_line = line.strip()
        # Verifica se a linha é um título de Unidade ou Seção
        if stripped_line.startswith('# '):
            # Salva a seção anterior antes de começar uma nova
            if current_title and current_content_lines:
                sections.append({'title': current_title, 'content': "\n".join(current_content_lines).strip()})

            unit_title = stripped_line
            current_title = unit_title
            current_content_lines = []
        
        elif stripped_line.startswith('## '):
            # Salva a seção anterior
            if current_title and current_content_lines:
                sections.append({'title': current_title, 'content': "\n".join(current_content_lines).strip()})
            
            # Começa uma nova seção, mantendo o contexto da unidade
            current_title = f"{unit_title}\n{stripped_line}"
            current_content_lines = []
        else:
            # É uma linha de conteúdo, adiciona ao bloco atual
            current_content_lines.append(line)
        
    # Adiciona a última seção que estava no buffer ao final do arquivo
    if current_title:
        sections.append({'title': current_title, 'content': "\n".join(current_content_lines).strip()})

    # Converte as seções coletadas em Documentos do LangChain
    documents = []
    for sec in sections:
        # Importante: Cria documentos mesmo para títulos sem conteúdo,
        # mas adiciona um texto placeholder para que não sejam descartados.
        # O conteúdo real virá da busca no dicionário `original_sections` no main.py.
        # A principal função aqui é garantir que TODOS os títulos sejam registrados.
        page_content = sec['content'] if sec['content'] else "Este é um título estrutural."
        documents.append(Document(
            page_content=page_content,
            metadata={'source': source_name, 'title': sec['title']}
        ))
    
    logger.info(f"Documento dividido em {len(documents)} seções lógicas (incluindo títulos estruturais).")
    return documents