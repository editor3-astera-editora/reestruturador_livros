# tests/test_rag_system.py
import pytest
from unittest.mock import patch, MagicMock
from langchain_core.documents import Document
from src.rag_system import retriever_builder

@patch('src.rag_system.retriever_builder.ParentDocumentRetriever')
@patch('src.rag_system.retriever_builder.InMemoryStore')
@patch('src.rag_system.retriever_builder.Chroma')
@patch('src.rag_system.retriever_builder.OpenAIEmbeddings')
@patch('src.rag_system.retriever_builder.RecursiveCharacterTextSplitter')
def test_build_retriever(
    MockSplitter, MockEmbeddings, MockChroma, MockStore, MockRetriever
):
    """
    Testa se o retriever é instanciado e configurado com os componentes corretos.
    """
    # Configura os mocks para retornar instâncias falsas
    mock_retriever_instance = MockRetriever.return_value
    
    # Dados de entrada
    dummy_documents = [Document(page_content="teste")]
    
    # Chama a função
    retriever = retriever_builder.build_retriever(dummy_documents)
    
    # Verificações
    assert MockSplitter.call_count == 2  # Um para o pai, um para o filho
    MockEmbeddings.assert_called_once()
    MockChroma.assert_called_once()
    MockStore.assert_called_once()
    MockRetriever.assert_called_once()
    
    # Verifica se add_documents foi chamado na instância do retriever
    mock_retriever_instance.add_documents.assert_called_once_with(dummy_documents, ids=None)
    
    # Verifica se a função retorna a instância mockada
    assert retriever == mock_retriever_instance