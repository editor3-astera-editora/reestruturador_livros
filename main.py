import re 
import unidecode
from config import settings 
from src.utils.logger import logger 
from src.preprocessing import document_handler
from src.rag_system import retriever_builder
from src.transformation import structure_mapper, content_rewriter, summary_generator
from src.assembly import document_assembler
import pypandoc

def normalize_title(title: str) -> str:
    """Função para limpar e normalizar títulos para garantir a correspondência."""

    cleaned_title = re.sub(r'^(?:#|##)\s*', '', title).strip()
    ascii_title = unidecode.unidecode(cleaned_title)
    normalized_title = re.sub(r'[^a-zA-Z0-9\s\.-]', '', ascii_title)

    return normalized_title.lower().strip()

def run_pipeline():
    """
    Executa o pipeline completo de reestruturação do livro didático.
    """
    logger.info("--- INICIANDO PIPELINE DE REESTRUTURAÇÃO DO LIVRO ---")

    # --- FASE 1: DESCONTRUÇÃO ---
    input_docx_path = settings.INPUT_DIR / settings.INPUT_FILENAME
    intermediate_md_path = settings.INTERMEDIATE_DIR / settings.MARKDOWN_FILENAME

    document_handler.convert_docx_to_markdown(
        input_docx_path, 
        intermediate_md_path,
        settings.INTERMEDIATE_DIR
        )
    
    # Lê o conteúdo do markdown gerado
    with open(intermediate_md_path, 'r', encoding='utf-8') as f:
        original_md_content = f.read()

    # CORREÇÃO CENTRAL: Pré-processa o conteúdo UMA VEZ
    corrected_md_content = document_handler.preprocess_markdown_headings(original_md_content)
    # Usa o conteúdo corrigido para dividir o documento
    documents = document_handler.load_and_split_by_structure(corrected_md_content, intermediate_md_path.name)
    
    if not documents:
        logger.critical("O pipeline foi interrompido porque nenhum documento foi extraído do arquivo de entrada.")
        return

    # --- FASE 2: CONTEXTUALIZAÇÃO (RAG) ---
    retriever = retriever_builder.build_retriever(documents)

    # --- FASE 3: TRANSFORMAÇÃO ---
    logger.info("--- INICIANDO FASE DE TRANSFORMAÇÃO ---")

    # 3.1 Mapeamento da Estrutura
    structure_map_path = settings.INTERMEDIATE_DIR / settings.STRUCTURE_MAP_FILENAME
    structure_map = structure_mapper.generate_structure_map(corrected_md_content, structure_map_path)

    # 3.2 Processamento de Conteúdo
    original_sections = {
        normalize_title(doc.metadata['title'].split('\n')[-1]): doc.page_content
        for doc in documents
    }
    logger.info(f"Dicionário de seções criado. Chaves disponíveis: {list(original_sections.keys())}")

    processed_content = {}

    for unit_title, unit_data in structure_map.items():
        logger.info(f"Processando: {unit_title}")
        processed_content[unit_title] = {'chapters': {}}
        
        unit_original_content = ""
        lookup_key_unit = normalize_title(unit_title)
        if lookup_key_unit in original_sections:
            unit_original_content += original_sections.get(lookup_key_unit, "") + "\n\n"
        
        for sections in unit_data.values():
             for section_title in sections:
                 lookup_key = normalize_title(section_title)
                 if lookup_key in original_sections:
                     unit_original_content += original_sections.get(lookup_key, "") + "\n\n"
        
        if unit_original_content.strip():
            processed_content[unit_title]['theme'] = summary_generator.generate_unit_theme(unit_original_content, retriever)

        for chapter_title, sections in unit_data.items():
            logger.info(f"  - Processando: {chapter_title}")
            processed_content[unit_title]['chapters'][chapter_title] = {'content': {}}
            chapter_rewritten_content = ""

            for section_title in sections:
                lookup_key = normalize_title(section_title)
                logger.info(f"  --- Procurando pela chave normalizada: '{lookup_key}'")
                
                if lookup_key in original_sections:
                    original_text = original_sections.get(lookup_key, "")
                    if original_text:
                        clean_section_title = re.sub(r'^(?:#|##)\s*', '', section_title).strip()
                        logger.info(f"    - Reescrevendo seção: {clean_section_title}")
                        rewritten_text = content_rewriter.rewrite_chunk(original_text, retriever)
                        # Salva o conteúdo reescrito
                        processed_content[unit_title]['chapters'][chapter_title]['content'][clean_section_title] = rewritten_text
                        chapter_rewritten_content += rewritten_text + "\n\n"
                else:
                    logger.warning(f"  - CHAVE NÃO ENCONTRADA (lookup_key='{lookup_key}' a partir do título '{section_title}')")
            
            if chapter_rewritten_content.strip():
                logger.info(f"  - Gerando resumo para: {chapter_title}")
                summary = summary_generator.generate_chapter_summary(chapter_rewritten_content, retriever)
                processed_content[unit_title]['chapters'][chapter_title]['summary'] = summary

    # --- FASE 5: MONTAGEM ---
    output_path = settings.OUTPUT_DIR / settings.OUTPUT_FILENAME
    document_assembler.create_final_document(processed_content, output_path)
    
    logger.info("--- PIPELINE CONCLUÍDO COM SUCESSO ---")
    
if __name__ == "__main__":
    run_pipeline()