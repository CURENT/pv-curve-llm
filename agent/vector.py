from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
import os
from pathlib import Path
from agent.utils.reranker import get_reranker

# Get the project root directory (where this file is located)
PROJECT_ROOT = Path(__file__).parent.parent

# Path to the vector database (absolute path)
DB_LOCATION = str(PROJECT_ROOT / "agent" / "vector_db")

# Embedding model
EMBEDDING_MODEL = "mxbai-embed-large"

# Number of vectors to return for each RAG query. Increasing this will increase the accuracy of the RAG query but will reduce speed.
NUM_VECTORS = 10

# Candidate pool size fetched from Chroma before reranking. i.e. CANDIDATE_VECTORS are fetched and reranked into the NUM_VECTORS most relevant.
CANDIDATE_VECTORS = 40

class SimpleRetriever:
    def __init__(self, base_retriever, reranker):
        self.base_retriever = base_retriever
        self.reranker = reranker
    
    def invoke(self, query):
        before = self.base_retriever.invoke(query)
        after = self.reranker.rerank(before, query)
        
        return after

def retriever():
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    
    if not os.path.exists(DB_LOCATION):
        raise FileNotFoundError(f"Database not found at {DB_LOCATION}")
    
    vector_store = Chroma(
        collection_name="pv-curves",
        persist_directory=DB_LOCATION,
        embedding_function=embeddings
    )
    
    base_retriever = vector_store.as_retriever(search_kwargs={"k": CANDIDATE_VECTORS})
    reranker = get_reranker(top_k=NUM_VECTORS)
    
    return SimpleRetriever(base_retriever, reranker)