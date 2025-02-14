"""Utils for initializing chromaDB/ollama resources."""
import ollama
import chromadb
import constants

ollama_client = ollama.Client(host="http://ollama:11434")
chroma_client = chromadb.HttpClient(host="chroma", port=8000)


def bootstrap_db():
    """Initialize the ChromaDB collection and pull the embedding model from ollama"""
    ollama_client.pull(constants.EMBEDDING_MODEL)
    if constants.CHROMA_COLLECTION_NAME not in chroma_client.list_collections():
        chroma_client.create_collection(
            constants.CHROMA_COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
        )


def reset_db():
    """Delete the chromaDB collection if it exists"""
    chroma_client.delete_collection(constants.CHROMA_COLLECTION_NAME)
    bootstrap_db()
