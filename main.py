import re 
from config import settings 
from src.utils.logger import logger 
from src.preprocessing import document_handler
from src.rag_system import retriever_builder
from src.transformation import structure_mapper, content_rewriter, summary_generator
from src.assembly import document_assembler

def run_pipeline():
    """
    Executa o pipeline completo de reestruturação do livro didático.
    """
    logger.info("--- INICIANDO PIPELINE DE REESTRUTURAÇÃO DO LIVRO ---")

    # --- FASE 1: DESCONTRUÇÃO ---
    input_docx_path = settings.INPUT_DIR / settings.INPUT_FILENAME
    intermediate_md_path = settings.INTERMEDIATE_DIR / settings.MARKDOWN_FILENAME

    document_handler.convert_docx_to_markdown(input_docx_path, intermediate_md_path)
    documents = document_handler.load_and_split_by_structure(intermediate_md_path)

    # --- FASE 2: CONTEXTUALIZAÇÃO (RAG) ---
    retriever = retriever_builder.build_retriever(documents)

    # --- FASE 3: TRANSFORMAÇÃO ---
    logger.info("--- INICIANDO FASE DE TRANSFORMAÇÃO ---")

    # 3.1 Mapeamento da Estrutura
    structure_map_path = settings.INTERMEDIATE_DIR / settings.STRUCTURE_MAP_FILENAME
    structure_map = structure_mapper.generate_structure_map(intermediate_md_path, structure_map_path)

    # 3.2 Processamento de Conteúdo
    processed_content = {}
    original_sections = {doc.metadata['title'].split('\n')[-1].strip(): doc.page_content for doc in documents}

    for unit_title, unit_data in structure_map.items():
        logger.info(f"Processando: {unit_title}")
        processed_content[unit_title] = {'chapters': {}}

        # Coleta todo o conteúdo original da unidade para gerar o tema 
        unit_original_content = ""
        for chapter_title, sections in unit_data.items():
             for section_title in sections:
                 # Limpa o título (ex: "## 1.1 O que é Vida?")
                 clean_title = re.sub(r'^##\s*', '', section_title).strip()
                 if clean_title in original_sections:
                     unit_original_content += original_sections[clean_title] + "\n\n"

        # Gera as temáticas da unidade
        processed_content[unit_title]['theme'] = summary_generator.generate_unit_theme(unit_original_content, retriever)

        # Processa cada capítulo
        for chapter_title, sections in unit_data.items():
            logger.info(f"  - Processando: {chapter_title}")
            processed_content[unit_title]['chapters'][chapter_title] = {'content': {}}
            chapter_rewritten_content = ""

            for section_title in sections:
                clean_title = re.sub(r'^##\s*', '', section_title).strip()
                if clean_title in original_sections:
                    original_text = original_sections[clean_title]
                    logger.info(f"    - Reescrevendo seção: {clean_title}")
                    
                    rewritten_text = content_rewriter.rewrite_chunk(original_text, retriever)
                    
                    processed_content[unit_title]['chapters'][chapter_title]['content'][clean_title] = rewritten_text
                    chapter_rewritten_content += rewritten_text + "\n\n"

            # Gera o resumo do capítulo
            logger.info(f"  - Gerando resumo para: {chapter_title}")
            summary = summary_generator.generate_chapter_summary(chapter_rewritten_content, retriever)
            processed_content[unit_title]['chapters'][chapter_title]['summary'] = summary

    # --- FASE 5: MONTAGEM ---
    output_path = settings.OUTPUT_DIR / settings.OUTPUT_FILENAME
    document_assembler.create_final_document(processed_content, output_path)
    
    logger.info("--- PIPELINE CONCLUÍDO COM SUCESSO ---")

if __name__ == "__main__":
    run_pipeline()