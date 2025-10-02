from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
import os
from agent.utils.reranker import get_reranker

# Path to the vector database
DB_LOCATION = "agent/vector_db"

# Embedding model
EMBEDDING_MODEL = "mxbai-embed-large"

# Number of vectors to return for each RAG query. Increasing this will increase the accuracy of the RAG query but will reduce speed.
NUM_VECTORS = 10

# Candidate pool size fetched from Chroma before reranking. i.e. CANDIDATE_VECTORS are fetched and reranked into the NUM_VECTORS most relevant.
CANDIDATE_VECTORS = 40

class SimpleRetriever:
    def __init__(self, base_retriever, reranker):
        self.base_retriever = base_retriever  # Chroma retriever
        self.reranker = reranker              # Cross-encoder reranker
    
    def invoke(self, query):
        before = self.base_retriever.invoke(query)  # Get 40 candidates
        after = self.reranker.rerank(before, query) # Rerank to top 10
        return after

def retriever():
    # 1. Initialize embeddings
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    
    # 2. Check database exists
    if not os.path.exists(DB_LOCATION):
        raise FileNotFoundError(f"Database not found at {DB_LOCATION}")
    
    # 3. Create Chroma vector store
    # vector_store is Chroma object
    vector_store = Chroma(
        collection_name="pv-curves",
        persist_directory=DB_LOCATION,
        embedding_function=embeddings
    )
    
    # 4. Create base retriever
    # base_retriever is ChromaRetriever object
    base_retriever = vector_store.as_retriever(search_kwargs={"k": CANDIDATE_VECTORS})
    
    # 5. Create reranker
    reranker = get_reranker(top_k=NUM_VECTORS)
    
    # 6. Return combined retriever
    return SimpleRetriever(base_retriever, reranker)