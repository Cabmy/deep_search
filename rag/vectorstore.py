"""ChromaDB 向量存储管理"""

from typing import Optional, Any
import chromadb
from langchain_chroma import Chroma
from langchain_core.documents import Document

from config import CHROMA_PERSIST_DIR, CHROMA_COLLECTION_NAME
from llm import get_embeddings


class VectorStore:
    """ChromaDB 向量存储封装"""
    
    def __init__(self, collection_name: Optional[str] = None, persist_dir: Optional[str] = None) -> None:
        self.collection_name: str = collection_name or CHROMA_COLLECTION_NAME
        self.persist_dir: str = persist_dir or CHROMA_PERSIST_DIR
        self._vectorstore: Optional[Chroma] = None
    
    @property
    def vectorstore(self) -> Chroma:
        """懒加载 vectorstore"""
        if self._vectorstore is None:
            self._vectorstore = Chroma(
                collection_name=self.collection_name,
                embedding_function=get_embeddings(),
                persist_directory=self.persist_dir,
            )
        return self._vectorstore
    
    def add_documents(self, documents: list[Document]) -> list[str]:
        """添加文档到向量库"""
        if not documents:
            return []
        return self.vectorstore.add_documents(documents)
    
    def similarity_search(self, query: str, k: int = 4) -> list[Document]:
        """相似度检索"""
        return self.vectorstore.similarity_search(query, k=k)
    
    def similarity_search_with_score(self, query: str, k: int = 4) -> list[tuple[Document, float]]:
        """带分数的相似度检索"""
        return self.vectorstore.similarity_search_with_score(query, k=k)
    
    def clear(self) -> None:
        """清空当前 collection"""
        client = chromadb.PersistentClient(path=self.persist_dir)
        try:
            client.delete_collection(self.collection_name)
        except Exception:
            pass  # Collection 不存在
        self._vectorstore = None


# 全局单例
_default_store: Optional[VectorStore] = None


def get_vectorstore() -> VectorStore:
    """获取全局 VectorStore 实例"""
    global _default_store
    if _default_store is None:
        _default_store = VectorStore()
    return _default_store
