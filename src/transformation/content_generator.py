import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config import settings, prompts
from src.utils.logger import logger
from src.utils.llm_handler import invoke_llm_with_tracking

def _run_chain(prompt_template_str: str, params: dict, temperature: float = 0.4) -> str:
    """Helper para executar uma cadeia LLM."""
    llm = ChatOpenAI(model=settings.LLM_MODEL, temperature=temperature, api_key=settings.OPENAI_API_KEY)
    prompt = PromptTemplate.from_template(prompt_template_str)
    chain = prompt | llm | StrOutputParser()
    return chain.invoke(params)

def generate_section(sumario_completo: str, capitulo_atual: str, subtitulo_atual: str, texto_original_da_secao: str, retriever_do_capitulo) -> str:
    llm = ChatOpenAI(model=settings.LLM_MODEL, temperature=settings.LLM_TEMPERATURE, top_p=settings.LLM_TOP_P, api_key=settings.OPENAI_API_KEY)
    prompt = PromptTemplate.from_template(prompts.CHAPTER_SECTION_GENERATOR_PROMPT)
    chain = prompt | llm | StrOutputParser()
    context_docs = retriever_do_capitulo.invoke(texto_original_da_secao)
    conteudo_do_rag_adicional = "\n---\n".join([doc.page_content for doc in context_docs if doc.page_content != texto_original_da_secao])
    
    return invoke_llm_with_tracking(chain, {
        "sumario_completo": sumario_completo, "capitulo_atual": capitulo_atual, "subtitulo_atual": subtitulo_atual,
        "texto_original_da_secao": texto_original_da_secao, "conteudo_do_rag_adicional": conteudo_do_rag_adicional
    }, f"Geração da Seção: {subtitulo_atual[:30]}")

def identify_expansion_topics(chapter_text: str) -> list:
    # --- INÍCIO DA CORREÇÃO ---
    llm = ChatOpenAI(model=settings.LLM_MODEL, temperature=0.0, api_key=settings.OPENAI_API_KEY)
    prompt = PromptTemplate.from_template(prompts.TOPIC_ANALYSIS_PROMPT)
    chain = prompt | llm | StrOutputParser()
    response = invoke_llm_with_tracking(
        chain, {"chapter_text": chapter_text}, "Análise de Tópicos para Expansão"
    )
    # --- FIM DA CORREÇÃO ---
    try:
        clean_response = response.strip().replace("```json", "").replace("```", "").strip()
        topics = json.loads(clean_response)
        return topics if isinstance(topics, list) else []
    except (json.JSONDecodeError, TypeError): 
        logger.warning(f"Não foi possível decodificar a lista de tópicos para expansão. Resposta: {response}")
        return []

def generate_expansion_paragraph(topic: str, base_text: str, mapa_de_conteudo_global: dict) -> str:
    mapa_str = json.dumps(mapa_de_conteudo_global, indent=2, ensure_ascii=False)
    # --- INÍCIO DA CORREÇÃO ---
    llm = ChatOpenAI(model=settings.LLM_MODEL, temperature=settings.LLM_TEMPERATURE, api_key=settings.OPENAI_API_KEY)
    prompt = PromptTemplate.from_template(prompts.EXPANSION_GENERATOR_PROMPT)
    chain = prompt | llm | StrOutputParser()
    return invoke_llm_with_tracking(chain, {
        "mapa_de_conteudo_global": mapa_str, "topic_to_expand": topic, "base_text": base_text
    }, f"Expansão do Tópico: {topic[:30]}")
    # --- FIM DA CORREÇÃO ---

def integrate_expansions(base_text: str, expansion_paragraphs: dict) -> str:
    paragraphs_str = "\n\n".join(f"--- NOVO PARÁGRAFO SOBRE '{topic}' ---\n{para}" for topic, para in expansion_paragraphs.items())
    # --- INÍCIO DA CORREÇÃO ---
    llm = ChatOpenAI(model=settings.LLM_MODEL, temperature=0.2, api_key=settings.OPENAI_API_KEY)
    prompt = PromptTemplate.from_template(prompts.INTEGRATION_PROMPT)
    chain = prompt | llm | StrOutputParser()
    return invoke_llm_with_tracking(chain, {
        "base_text": base_text, "expansion_paragraphs": paragraphs_str
    }, "Integração de Conteúdo Expandido")
    # --- FIM DA CORREÇÃO ---

def generate_curiosities(chapter_content: str) -> dict:
    logger.info("    - Verificando a necessidade de uma seção 'Você sabia?'...")
    # --- INÍCIO DA CORREÇÃO ---
    llm = ChatOpenAI(model=settings.LLM_MODEL, temperature=0.7, api_key=settings.OPENAI_API_KEY)
    prompt = PromptTemplate.from_template(prompts.CURIOSITY_GENERATOR_PROMPT)
    chain = prompt | llm | StrOutputParser()
    response = invoke_llm_with_tracking(
        chain, {"context": chapter_content}, "Geração de Curiosidade"
    )
    # --- FIM DA CORREÇÃO ---
    try:
        clean_response = response.strip().replace("```json", "").replace("```", "").strip()
        curiosity_data = json.loads(clean_response)
        if curiosity_data.get("curiosidade"): logger.info("      -> Curiosidade gerada!")
        return curiosity_data
    except (json.JSONDecodeError, TypeError):
        logger.warning(f"      -> Não foi possível gerar uma curiosidade em formato JSON. Resposta: {response}")
        return {"curiosidade": None}