from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config import settings, prompts 

def rewrite_chunk(text_chunk: str, retriever) -> str:
    """
    Reescreve um pedaço de texto para um tom formal, usando o RAG para contexto.
    """
    llm = ChatOpenAI(
        model=settings.LLM_MODEL,
        temperature=settings.LLM_TEMPERATURE,
        top_p=settings.LLM_TOP_P,
        api_key=settings.OPENAI_API_KEY
    )

    prompt = PromptTemplate.from_template(prompts.CONTENT_REWRITTER_PROMPT)
    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser

    # Busca por contexto relevante uando o retriever 
    context_docs = retriever.invoke(text_chunk)
    context = "\n---\n".join([doc.page_content for doc in context_docs])

    rewritten_text = chain.invoke({
        "context": context, 
        "text_chunk": text_chunk
    })

    return rewritten_text