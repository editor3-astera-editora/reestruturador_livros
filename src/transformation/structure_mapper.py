import json 
from pathlib import Path 
import re 
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from config import settings, prompts
from src.utils.logger import logger 


def generate_structure_map(markdown_path: Path, output_path: Path) -> dict:
    """
    Usa o LLM para criar um mapa de nova estrutura de capítulos e salva em JSON.
    """
    logger.info("Gerando mapa de nova estrutura com o LLM...")
    with open(markdown_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extrai apenas os cabeçalhos para criar um sumário 
    table_of_contents = "\n".join(re.findall(r'^(#|##)\s.*', content, re.MULTILINE))

    llm = ChatOpenAI(
        model=settings.LLM_MODEL,
        temperature=settings.LLM_TEMPERATURE,
        api_key=settings.OPENAI_API_KEY
    )

    prompt = PromptTemplate.from_template(prompts.STRUCTURE_MAPPER_PROMPT)
    chain = prompt | llm 

    response = chain.invoke({"table_of_contents": table_of_contents})

    try:
        # Limpa a saída do LLM para garantir que seja um JSON válido 
        json_content = response.content.strip().replace("```json", "").replace("```", "")
        structure_map = json.loads(json_content)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(structure_map, f, ensure_ascii=False, ident=2)

        logger.info(f"Mapa da estrutura salvo em '{output_path}'")
        return structure_map
    except json.JSONDecodeError as e:
        logger.error(f"Falha ao decodificar a resposta JSON do LLM. Resposta: {response.content}. Erro: {e}")
        raise 

    