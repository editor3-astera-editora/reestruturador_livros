from typing import List 
from langchain_core.documents import Document 
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore
from langchain_chroma import Chroma 
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import settings
from src.utils.logger import logger

def build_retriever(documents: List[Document]):
    """
    Constrói e retorna um ParentDocumentRetriever configurado.
    """
    logger.info("Construindo o sistema RAG com ParentDocumentRetriever...")
    
    # Divisor para os documentos pais 
    parent_splitter = RecursiveCharacterTextSplitter(chunk_size=settings.CHUNK_SIZE_PARENT)

    # Divisor para os documentos filhos 
    child_splitter = RecursiveCharacterTextSplitter(chunk_size=settings.CHUNK_SIZE_CHILD)

    # Banco de dados vetorial para os chunks filhos 
    vectorstore = Chroma(
        collection_name="split_parents",
        embedding_function=OpenAIEmbeddings(model=settings.EMBEDDING_MODEL),
        parsist_directory=str(settings.VECTORSTORE_DIR)
    )

    # Armazenamento para os documentos pais 
    store = InMemoryStore()

    retriever = ParentDocumentRetriever(
        vectorstore=vectorstore,
        docstore=store,
        child_splitter=child_splitter,
        parent_splitter=parent_splitter,
    )

    logger.info("Adicionando documentos ao retriever...")
    retriever.add_documents(documents, ids=None)

    logger.info("Retriever construído e pronto para uso.")
    return retriever 