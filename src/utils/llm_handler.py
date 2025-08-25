from langchain_community.callbacks import get_openai_callback
from langchain_core.runnables.base import Runnable
from src.utils.logger import logger

def invoke_llm_with_tracking(chain: Runnable, params: dict, task_name: str) -> str:
    """
    Invoca uma cadeia LangChain, rastreia o uso de tokens e custos,
    e loga as informações.

    Args:
        chain: A cadeia LangChain a ser executada.
        params: Os parâmetros de entrada para a cadeia.
        task_name: Um nome descritivo para a tarefa (usado no log).

    Returns:
        A resposta da LLM como uma string.
    """
    response_content = ""
    try:
        with get_openai_callback() as cb:
            response = chain.invoke(params)
            
            # Garante que a resposta seja uma string, seja de um AIMessage ou de um StrOutputParser
            response_content = response if isinstance(response, str) else response.content

            token_info = {
                "prompt": cb.prompt_tokens,
                "completion": cb.completion_tokens,
                "total": cb.total_tokens,
                "cost_usd": f"${cb.total_cost:.6f}" # Formata o custo para 6 casas decimais
            }
            logger.info(f"  - [Uso de Tokens - {task_name}]: {token_info}")

    except Exception as e:
        logger.error(f"  - Erro durante a execução da tarefa '{task_name}': {e}")
        # Retorna uma string vazia ou lança a exceção, dependendo da necessidade de robustez
        return ""
        
    return response_content