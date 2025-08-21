from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config import settings, prompts 

def generate_unit_theme(unit_content: str, retriever) -> str:
    """Gera a seção 'Temáticas da unidade'."""
    llm = ChatOpenAI(model=settings.LLM_MODEL, temperature=settings.LLM_TEMPERATURE, api_key=settings.OPENAI_API_KEY)
    prompt = PromptTemplate.from_template(prompts.UNIT_THEME_GENERATOR_PROMPT)
    chain = prompt | llm | StrOutputParser()

    # O próprio conteúdo da unidade é o contexto primário 
    context = unit_content 

    theme = chain.invoke({"context": context})
    return theme 

def generate_chapter_summary(chapter_content: str, retriver) -> str:
    """Gera a seção 'Resumindo' para um capítulo."""
    llm = ChatOpenAI(model=settings.LLM_MODEL, temperature=settings.LLM_TEMPERATURE, api_key=settings.OPENAI_API_KEY)
    prompt = PromptTemplate.from_template(prompts.CHAPTER_SUMMARY_GENERATOR_PROMPT)
    chain = prompt | llm | StrOutputParser()

    summary = chain.invoke({"context": chapter_content})
    return summary 