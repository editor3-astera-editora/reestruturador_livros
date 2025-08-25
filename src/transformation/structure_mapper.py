import json 
from pathlib import Path 
import re 
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from config import settings, prompts
from src.utils.logger import logger 
from src.utils.llm_handler import invoke_llm_with_tracking

def generate_structure_map(markdown_content: str, output_path: Path) -> dict:
    logger.info("Gerando mapa de nova estrutura com o LLM...")
    
    table_of_contents = "\n".join(re.findall(r'^(?:#|##)\s.*', markdown_content, re.MULTILINE))
    if not table_of_contents.strip():
        logger.error("O sumário extraído do Markdown está vazio.")
        return {}

    llm = ChatOpenAI(model=settings.LLM_MODEL, temperature=0.0, api_key=settings.OPENAI_API_KEY)
    prompt_template = PromptTemplate.from_template(prompts.STRUCTURE_MAPPER_PROMPT)
    chain = prompt_template | llm

    final_prompt_input = {"table_of_contents": table_of_contents}
    
    # Chamada centralizada com rastreamento
    response_content = invoke_llm_with_tracking(
        chain, final_prompt_input, task_name="Mapeamento de Estrutura"
    )

    try:
        json_content = response_content.strip().replace("```json", "").replace("```", "")
        structure_map = json.loads(json_content)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(structure_map, f, ensure_ascii=False, indent=2)
        logger.info(f"Mapa da estrutura salvo em '{output_path}'")
        return structure_map
    except json.JSONDecodeError:
        logger.error(f"Falha ao decodificar a resposta JSON do LLM. Resposta recebida: {response_content}")
        raise