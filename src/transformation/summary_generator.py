from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config import settings, prompts 
from src.utils.llm_handler import invoke_llm_with_tracking

def generate_unit_theme(unit_title: str, chapter_summaries: str, retriever) -> str:
    """Gera a seção 'Temáticas da unidade' com base nos resumos dos capítulos."""
    llm = ChatOpenAI(model=settings.LLM_MODEL, temperature=0.3, api_key=settings.OPENAI_API_KEY)
    prompt = PromptTemplate.from_template(prompts.UNIT_THEME_GENERATOR_PROMPT)
    chain = prompt | llm | StrOutputParser()
    return invoke_llm_with_tracking(
        chain, 
        {"unit_title": unit_title, "chapter_summaries": chapter_summaries}, 
        "Geração de Tema da Unidade"
    )

def generate_chapter_summary(chapter_content: str, retriever) -> str:
    llm = ChatOpenAI(model=settings.LLM_MODEL, temperature=0.2, api_key=settings.OPENAI_API_KEY)
    prompt = PromptTemplate.from_template(prompts.CHAPTER_SUMMARY_GENERATOR_PROMPT)
    chain = prompt | llm | StrOutputParser()
    return invoke_llm_with_tracking(chain, {"context": chapter_content}, "Geração de Resumo do Capítulo")

def summarize_text(text_to_summarize: str) -> str:
    if not text_to_summarize or not text_to_summarize.strip(): return ""
    llm = ChatOpenAI(model=settings.LLM_MODEL, temperature=0.0, api_key=settings.OPENAI_API_KEY)
    prompt = PromptTemplate.from_template(prompts.TEXT_SUMMARIZER_PROMPT)
    chain = prompt | llm | StrOutputParser()
    return invoke_llm_with_tracking(chain, {"text_to_summarize": text_to_summarize}, "Sumarização para Mapa Global")