import docx
import pypandoc
from pathlib import Path
from src.utils.logger import logger
from config import settings 
import re

def create_final_document(processed_content: dict, output_path: Path):
    """
    Monta uma string Markdown completa do livro e a converte para .docx usando pandoc e um reference.docx.
    """
    logger.info("Montando o conteúdo final em formato Markdown...")
    
    final_markdown_lines = []
    
    for unit_title, unit_data in processed_content.items():
        final_markdown_lines.append(f"# {unit_title}\n")
        
        if 'theme' in unit_data:
            final_markdown_lines.append(f"## Temáticas da unidade\n")
            final_markdown_lines.append(f"{unit_data['theme']}\n")
            
        for chapter_title, chapter_data in unit_data.get('chapters', {}).items():
            final_markdown_lines.append(f"## {chapter_title}\n")
            
            if 'content' in chapter_data:
                # O 'content' já vem com subtítulos ###, então apenas o adicionamos.
                final_markdown_lines.append(f"{chapter_data['content']}\n")
                
            if 'curiosity' in chapter_data:
                final_markdown_lines.append(f"### Você sabia?\n")
                final_markdown_lines.append(f"{chapter_data['curiosity']}\n")

            if 'summary' in chapter_data:
                final_markdown_lines.append(f"### Resumindo\n")
                final_markdown_lines.append(f"{chapter_data['summary']}\n")

    final_markdown_string = "\n".join(final_markdown_lines)
    
    final_md_path = settings.INTERMEDIATE_DIR / "final_book.md"
    with open(final_md_path, 'w', encoding='utf-8') as f:
        f.write(final_markdown_string)
    
    logger.info(f"Arquivo Markdown final montado em '{final_md_path}'.")
    logger.info("Convertendo o Markdown final para .docx com estilos via reference.docx...")

    reference_doc_path = settings.BASE_DIR / "config" / "reference.docx"

    try:
        pypandoc.convert_file(
            source_file=str(final_md_path),
            to='docx',
            format='gfm',  # Informa ao pandoc que a fonte é GitHub Flavored Markdown
            outputfile=str(output_path),
            extra_args=[f'--reference-doc={str(reference_doc_path)}', '--toc']
        )
        logger.info(f"Documento final salvo com sucesso em '{output_path}'")
    except FileNotFoundError:
        logger.error(f"ARQUIVO DE REFERÊNCIA NÃO ENCONTRADO: Verifique se 'reference.docx' existe em '{reference_doc_path}'")
    except Exception as e:
        logger.error(f"Ocorreu um erro durante a conversão final para .docx com pandoc: {e}")