from langchain_community.callbacks import get_openai_callback
from langchain_core.runnables.base import Runnable
from src.utils.logger import logger

def invoke_llm_with_tracking(chain: Runnable, params: dict, task_name: str) -> str:
    """
    Invoca uma cadeia LangChain. O rastreamento de custo será feito por um 
    context manager global no ponto de entrada do script (main.py).
    """
    response_content = ""
    try:
        # Executa a chamada diretamente, sem o callback local
        response = chain.invoke(params)
        response_content = response if isinstance(response, str) else response.content
    except Exception as e:
        logger.error(f"  - Erro durante a execução da tarefa '{task_name}': {e}")
        return ""
        
    return response_content