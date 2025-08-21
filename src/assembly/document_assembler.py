import docx 
from pathlib import Path 
from src.utils.logger import logger 

def create_final_document(processed_content: dict, output_path: Path):
    """
    Monta o documento .docx final a partir do conteúdo processado e estruturado.
    """
    logger.info("Montando o documento .docx final...")
    doc = docx.Document()

    for unit_title, unit_data in processed_content.items():
        doc.add_heading(unit_title, level=1)

        # Adiciona a seção de temáticas 
        if 'theme' in unit_data:
            doc.add_heading("Temáticas da unidade", level=2)
            doc.add_paragraph(unit_data['theme'])

        # Adiciona os capítulos 
        for chapter_title, chapter_data in unit_data.get('chapters', {}).items():
            doc.add_heading(chapter_title, level=2)

            # Adiciona o conteúdo do capítulo
            for section_title, section_content in chapter_data.get('content', {}).items():
                doc.add_heading(section_title, level=3)
                doc.add_paragraph(section_content)

            # Adiciona o resumo do capítulo 
            if 'summary' in chapter_data:
                doc.add_heading("Resumindo", level=3)
                doc.add_paragraph(chapter_data['summary'])
    
    doc.save(output_path)
    logger.info(f"Documento final salvo com sucesso em '{output_path}'")
