import chromadb
from chromadb.utils import embedding_functions
from pathlib import Path
from typing import List

# class VectorStore:
#     def __init__(self, persist_directory: Path):
#         self.client = chromadb.PersistentClient(path=str(persist_directory))
#         self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
#             model_name="all-MiniLM-L6-v2"
#         )

#     def store_document(self, collection_name: str, chunks: List[str]) -> int:
#         collection = self.client.get_or_create_collection(
#             name=collection_name,
#             embedding_function=self.embedding_fn
#         )
#         ids = [f"chunk_{i}" for i in range(len(chunks))]
#         collection.add(documents=chunks, ids=ids)
#         return len(chunks)

#     def retrieve(self, collection_name: str, query: str, top_k: int = 4) -> List[str]:
#         try:
#             collection = self.client.get_collection(name=collection_name)
#         except Exception as e:
#             raise ValueError(f"Document '{collection_name}' not found in vector store") from e
        
#         results = collection.query(query_texts=[query], n_results=top_k)
#         return results["documents"][0]




class VectorStore:
    def __init__(self, persist_dir: str):
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
    
    def store_document(self, document_id: str, chunks: List[str]) -> int:
        """Store document chunks with document_id as metadata"""
        ids = [f"{document_id}_{i}" for i in range(len(chunks))]
        metadatas = [{"document_id": document_id, "chunk_index": i} for i in range(len(chunks))]
        
        self.collection.add(
            documents=chunks,
            ids=ids,
            metadatas=metadatas
        )
        return len(chunks)
    
    def retrieve(self, document_id: str, query: str, top_k: int = 5) -> List[str]:
        """Retrieve relevant chunks for a document"""
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where={"document_id": document_id}
        )
        return results["documents"][0] if results["documents"] else []
    
    def delete_document(self, document_id: str):
        """Delete all chunks for a document"""
        self.collection.delete(where={"document_id": document_id})