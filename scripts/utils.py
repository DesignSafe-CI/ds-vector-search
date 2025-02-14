"""chromaDB/ollama utils"""

import chromadb
import ollama
import uuid
import constants


def get_chroma_client():
    """Get chromaDB client"""
    return chromadb.HttpClient(host="chroma", port=8000)


def get_chroma_collection():
    """Retrieve the chromaDB collection containing DesignSafe pubs"""
    client = get_chroma_client()
    return client.get_collection(constants.CHROMA_COLLECTION_NAME)


def get_ollama_client():
    """Get ollama client"""
    return ollama.Client(host="http://ollama:11434")


def get_embeddings(documents: list[str]):
    """Embed a list of strings using ollama"""
    client = get_ollama_client()
    embeddings = client.embed(model=constants.EMBEDDING_MODEL, input=documents)
    return embeddings.embeddings


def chunk_array(arr: list, chunk_size: int = 50):
    """Iterate through an array yielding sub-arrays of size chunk_size"""
    cursor_l = 0
    cursor_r = chunk_size
    res = []
    while cursor_r < len(arr):
        res.append(arr[cursor_l:cursor_r])
        cursor_l += chunk_size
        cursor_r += chunk_size
    res.append(arr[cursor_l:])

    return res


def insert_documents(docs: list[str], embeddings: list[list[float]], project_id: str):
    """
    Insert documents and their embeddings into ChromaDB.
    The project ID is stored as metadata
    """
    ids = [str(uuid.uuid4()) for _ in docs]
    metadatas = [{"projectId": project_id} for _ in docs]
    chroma_client = get_chroma_client()
    collection = chroma_client.get_collection(constants.CHROMA_COLLECTION_NAME)
    collection.add(documents=docs, metadatas=metadatas, embeddings=embeddings, ids=ids)


def query_db(query_text: str):
    """Embed a query string using ollama, then find closest matches in the database."""
    query_embedding = get_embeddings([query_text])
    collection = get_chroma_collection()
    return collection.query(query_embedding)
