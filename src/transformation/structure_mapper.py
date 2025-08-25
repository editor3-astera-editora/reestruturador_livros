import json 
from pathlib import Path 
import re 
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from config import settings, prompts
from src.utils.logger import logger 
from src.utils.llm_handler import invoke_llm_with_tracking

def generate_structure_map(markdown_content: str, output_path: Path) -> dict:
    """
    Cria um mapa da estrutura processando uma unidade de cada vez para maior robustez.
    """
    logger.info("Gerando mapa da nova estrutura (unidade por unidade)...")
    
    llm = ChatOpenAI(
        # Usamos um modelo mais barato para esta tarefa estruturada
        model=settings.LLM_MODEL_STRUCTURE if hasattr(settings, 'LLM_MODEL_STRUCTURE') else 'gpt-3.5-turbo',
        temperature=0.0,
        api_key=settings.OPENAI_API_KEY
    )
    prompt_template = PromptTemplate.from_template(prompts.STRUCTURE_MAPPER_PROMPT)
    chain = prompt_template | llm

    unit_splits = re.split(r'(^#\s.*)', markdown_content, flags=re.MULTILINE)
    if unit_splits and not unit_splits[0].strip():
        unit_splits = unit_splits[1:]

    final_structure_map = {}

    for i in range(0, len(unit_splits), 2):
        unit_title = unit_splits[i].strip().replace('# ', '')
        unit_content = unit_splits[i+1] if (i + 1) < len(unit_splits) else ""
        
        section_list = re.findall(r'^##\s.*', unit_content, flags=re.MULTILINE)
        
        if not section_list:
            logger.warning(f"Nenhuma seção (##) encontrada para a '{unit_title}'.")
            continue

        logger.info(f"Mapeando seções para a '{unit_title}'...")
        
        response_content = invoke_llm_with_tracking(
            chain, 
            {"unit_title": unit_title, "section_list": "\n".join(section_list)},
            f"Mapeamento da Estrutura: {unit_title}"
        )

        try:
            json_content = response_content.strip().replace("```json", "").replace("```", "").strip()
            unit_map = json.loads(json_content)
            final_structure_map[unit_title] = unit_map
        except (json.JSONDecodeError, TypeError):
            logger.error(f"Falha ao mapear a estrutura para a '{unit_title}'. Resposta: {response_content}")
            final_structure_map[unit_title] = {}

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final_structure_map, f, ensure_ascii=False, indent=2)
        
    logger.info(f"Mapa da estrutura completo salvo em '{output_path}'")
    return final_structure_map