import json 
from pathlib import Path 
import re 
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from config import settings, prompts
from src.utils.logger import logger 


def generate_structure_map(markdown_content: str, output_path: Path) -> dict:
    """
    Usa o LLM para criar um mapa de nova estrutura de capítulos ea partir de uma string de conteúdo.
    """
    logger.info("Gerando mapa de nova estrutura com o LLM...")

    # Extrai o sumário do conteúdo corrigido
    table_of_contents = "\n".join(re.findall(r'^(?:#|##)\s.*', markdown_content, re.MULTILINE))

    # Adiciona uma verificação para garantir que o sumário não está vazio
    if not table_of_contents.strip():
        logger.error("O sumário extraído do Markdown está vazio. O mapa da estrutura não pode ser gerado.")
        # Retorna um mapa vazio para evitar que o pipeline quebre, mas sinaliza o erro
        return {}

    llm = ChatOpenAI(
        model=settings.LLM_MODEL,
        temperature=settings.LLM_TEMPERATURE,
        api_key=settings.OPENAI_API_KEY
    )

    prompt = PromptTemplate.from_template(prompts.STRUCTURE_MAPPER_PROMPT)
    chain = prompt | llm 

    # --- INÍCIO DA MODIFICAÇÃO PARA DEPURAÇÃO ---
    # Vamos logar exatamente o que estamos enviando para a LLM
    final_prompt_input = {"table_of_contents": table_of_contents}
    logger.info("--- INÍCIO DO CONTEÚDO ENVIADO PARA O MAPEAMENTO DE ESTRUTURA ---")
    logger.info(json.dumps(final_prompt_input, indent=2, ensure_ascii=False))
    logger.info("--- FIM DO CONTEÚDO ENVIADO PARA O MAPEAMENTO DE ESTRUTURA ---")
    # --- FIM DA MODIFICAÇÃO PARA DEPURAÇÃO ---

    try:
        response = chain.invoke({"table_of_contents": table_of_contents})
        json_content = response.content.strip().replace("```json", "").replace("```", "")
        structure_map = json.loads(json_content)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(structure_map, f, ensure_ascii=False, indent=2)

        logger.info(f"Mapa da estrutura salvo em '{output_path}'")
        return structure_map
    except json.JSONDecodeError as e:
        logger.error(f"Falha ao decodificar a resposta JSON do LLM. Resposta recebida: {response.content}")
        raise
    except Exception as e:
        logger.error(f"Ocorreu um erro inesperado durante o mapeamento da estrutura: {e}")
        raise