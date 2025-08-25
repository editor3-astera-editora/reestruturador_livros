import re 
import unidecode
from config import settings

from src.utils.logger import logger 
from src.preprocessing import document_handler
from src.rag_system import retriever_builder
from src.transformation import content_generator, structure_mapper, summary_generator
from src.assembly import document_assembler
import pypandoc
from langchain_community.callbacks import get_openai_callback

def normalize_title(title: str) -> str:
    """Função para limpar e normalizar títulos para garantir a correspondência."""

    cleaned_title = re.sub(r'^(?:#|##)\s*', '', title).strip()
    ascii_title = unidecode.unidecode(cleaned_title)
    normalized_title = re.sub(r'[^a-zA-Z0-9\s\.-]', '', ascii_title)

    return normalized_title.lower().strip()

def create_full_book_summary_str(structure_map: dict) -> str:
    """Cria uma string formatada com o sumário do livro inteiro."""
    summary_lines = []
    for unit_title, unit_data in structure_map.items():
        summary_lines.append(f"# {unit_title}")
        for chapter_title, sections in unit_data.items():
            summary_lines.append(f"  ## {chapter_title}")
            for section_title in sections:
                clean_section = re.sub(r'^##\s*', '', section_title).strip()
                summary_lines.append(f"    - {clean_section}")
    return "\n".join(summary_lines)

def run_pipeline():
    """
    Executa o pipeline completo de reestruturação do livro didático.
    """
    logger.info("--- INICIANDO PIPELINE DE REESTRUTURAÇÃO DE LIVRO ---")

    # FASE 1: DESCONSTRUÇÃO E PREPARAÇÃO
    input_docx_path = settings.INPUT_DIR / settings.INPUT_FILENAME
    intermediate_md_path = settings.INTERMEDIATE_DIR / settings.MARKDOWN_FILENAME
    document_handler.convert_docx_to_markdown(input_docx_path, intermediate_md_path, settings.INTERMEDIATE_DIR)
    
    with open(intermediate_md_path, 'r', encoding='utf-8') as f:
        original_md_content = f.read()
    corrected_md_content = document_handler.preprocess_markdown_headings(original_md_content)
    all_documents = document_handler.load_and_split_by_structure(corrected_md_content, intermediate_md_path.name)
    
    if not all_documents:
        logger.critical("Pipeline interrompido: nenhum documento foi extraído do arquivo de entrada.")
        return

    # FASE 2: MAPEAMENTO DA ESTRUTURA
    structure_map_path = settings.INTERMEDIATE_DIR / settings.STRUCTURE_MAP_FILENAME
    structure_map = structure_mapper.generate_structure_map(corrected_md_content, structure_map_path)
    full_book_summary = create_full_book_summary_str(structure_map)

    original_sections_map = {
        normalize_title(doc.metadata['title'].split('\n')[-1]): doc for doc in all_documents
    }
    
    # FASE 3: GERAÇÃO E EXPANSÃO DE CONTEÚDO
    logger.info("--- INICIANDO FASE DE GERAÇÃO E EXPANSÃO DE CONTEÚDO ---")
    
    processed_content = {}
    mapa_de_conteudo_global = {}

    for unit_title, unit_data in structure_map.items():
        logger.info(f"Processando Unidade: {unit_title}")
        processed_content[unit_title] = {'chapters': {}}
        full_unit_text_for_theme = ""

        for chapter_title, sections in unit_data.items():
            logger.info(f"  - Preparando Capítulo: {chapter_title}")
            
            chapter_docs = [original_sections_map[normalize_title(s)] for s in sections if normalize_title(s) in original_sections_map]
            if not chapter_docs:
                logger.warning(f"    Nenhum conteúdo fonte encontrado para o capítulo {chapter_title}. Pulando.")
                continue
            
            chapter_retriever = retriever_builder.build_retriever(chapter_docs)
            
            final_chapter_sections = {}
            
            # LÓGICA DE GERAÇÃO E EXPANSÃO (SEÇÃO POR SEÇÃO)
            for section_title in sections:
                clean_section_title = re.sub(r'^(?:#|##)\s*', '', section_title).strip()
                lookup_key = normalize_title(section_title)
                
                if lookup_key not in original_sections_map:
                    continue

                original_doc = original_sections_map[lookup_key]
                text_for_generation = original_doc.page_content
                if text_for_generation == "TÍTULO ESTRUTURAL":
                    text_for_generation = clean_section_title

                # 1. GERA O RASCUNHO INICIAL DA SEÇÃO
                logger.info(f"    - Gerando rascunho para a seção: {clean_section_title}")
                generated_section_text = content_generator.generate_section(
                    sumario_completo=full_book_summary, capitulo_atual=chapter_title, subtitulo_atual=clean_section_title,
                    texto_original_da_secao=text_for_generation, retriever_do_capitulo=chapter_retriever
                )

                # 2. INICIA O LOOP DE EXPANSÃO PARA A SEÇÃO ATUAL
                word_count = len(generated_section_text.split())
                target_words_per_section = (settings.TARGET_WORDS_PER_UNIT / len(unit_data)) / len(sections) if len(sections) > 0 else 250

                for i in range(settings.MAX_EXPANSION_ITERATIONS):
                    if word_count >= target_words_per_section:
                        break
                    
                    logger.info(f"      - Expansão da seção '{clean_section_title}' [{i+1}/{settings.MAX_EXPANSION_ITERATIONS}].")
                    
                    topics_to_expand = content_generator.identify_expansion_topics(generated_section_text)
                    if not topics_to_expand:
                        break

                    new_paragraphs = {}
                    for topic in topics_to_expand:
                        new_paragraphs[topic] = content_generator.generate_expansion_paragraph(topic, generated_section_text, mapa_de_conteudo_global)
                    
                    generated_section_text = content_generator.integrate_expansions(generated_section_text, new_paragraphs)
                    word_count = len(generated_section_text.split())

                final_chapter_sections[clean_section_title] = generated_section_text

            # 3. MONTA O TEXTO COMPLETO DO CAPÍTULO A PARTIR DAS SEÇÕES JÁ FINALIZADAS
            full_chapter_text = "\n\n".join(f"### {title}\n{text}" for title, text in final_chapter_sections.items())

            processed_content[unit_title]['chapters'][chapter_title] = {'content': full_chapter_text}
            
            # --- Enriquecimento Final do Capítulo ---
            curiosity = content_generator.generate_curiosities(full_chapter_text)
            if curiosity and curiosity.get("curiosidade"):
                processed_content[unit_title]['chapters'][chapter_title]['curiosity'] = curiosity["curiosidade"]

            summary = summary_generator.generate_chapter_summary(full_chapter_text, chapter_retriever)
            processed_content[unit_title]['chapters'][chapter_title]['summary'] = summary
            
            resumo_capitulo = summary_generator.summarize_text(full_chapter_text)
            mapa_de_conteudo_global[chapter_title] = resumo_capitulo
            full_unit_text_for_theme += full_chapter_text + "\n\n"

        if full_unit_text_for_theme.strip():
            global_retriever = retriever_builder.build_retriever(all_documents)
            processed_content[unit_title]['theme'] = summary_generator.generate_unit_theme(unit_title, full_unit_text_for_theme, global_retriever)

    # FASE 5: MONTAGEM
    output_path = settings.OUTPUT_DIR / settings.OUTPUT_FILENAME
    document_assembler.create_final_document(processed_content, output_path)
    
    logger.info("--- PIPELINE CONCLUÍDO COM SUCESSO ---")

if __name__ == "__main__":
    if not settings.OPENAI_API_KEY or "SUA_CHAVE_API_AQUI" in settings.OPENAI_API_KEY:
        logger.error("A chave da API da OpenAI não foi configurada. Verifique seu arquivo .env")
    else:
        with get_openai_callback() as cb:
            run_pipeline()
            
            print("\n" + "="*50)
            logger.info("--- CUSTO TOTAL DO PIPELINE ---")
            logger.info(f"Total de Tokens: {cb.total_tokens}")
            logger.info(f"  - Tokens de Prompt: {cb.prompt_tokens}")
            logger.info(f"  - Tokens de Conclusão: {cb.completion_tokens}")
            logger.info(f"Custo Total (USD): ${cb.total_cost:.4f}")
            print("="*50 + "\n")