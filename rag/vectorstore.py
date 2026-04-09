"""ChromaDB 向量存储管理"""

from typing import Optional, Any
import chromadb
import os
import sqlite3
import shutil
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
        """清空当前 collection。

        保守策略：先通过 chromadb API 删除 collection（如果存在），
        然后读取 chroma.sqlite3 中剩余的 segment id 列表，
        删除 persist_dir 下不在该列表中的 UUID 目录（仅删除包含典型 segment 文件的目录），
        避免误删其它文件。
        """
        client = chromadb.PersistentClient(path=self.persist_dir)
        try:
            client.delete_collection(self.collection_name)
        except Exception:
            pass  # Collection 可能不存在或已被删除
        # 重置缓存的 vectorstore 实例
        self._vectorstore = None

        # 清理未被引用的 UUID 目录（保守删除：仅删除典型 segment 文件目录）
        try:
            db_path = os.path.join(self.persist_dir, "chroma.sqlite3")
            remaining_segment_ids: set[str] = set()
            if os.path.exists(db_path):
                try:
                    conn = sqlite3.connect(db_path)
                    cur = conn.cursor()
                    cur.execute("SELECT id FROM segments")
                    rows = cur.fetchall()
                    remaining_segment_ids = {r[0] for r in rows if r and r[0]}
                except Exception:
                    # 若读取 DB 失败，则不进行删除以避免误删
                    remaining_segment_ids = set()
                finally:
                    try:
                        conn.close()
                    except Exception:
                        pass

            # 列出 persist_dir 下的子目录并删除不在 remaining_segment_ids 中的目录（且目录内含典型文件）
            entries = [os.path.join(self.persist_dir, e) for e in os.listdir(self.persist_dir)]
            dirs = [p for p in entries if os.path.isdir(p)]
            typical_files = {"data_level0.bin", "header.bin", "length.bin", "link_lists.bin"}
            for d in dirs:
                base = os.path.basename(d)
                if base in remaining_segment_ids:
                    continue
                try:
                    files = set(os.listdir(d))
                except Exception:
                    continue
                # 仅当目录看起来像一个 Chroma segment 数据目录时才删除
                if typical_files.issubset(files):
                    try:
                        shutil.rmtree(d)
                    except Exception:
                        pass
        except Exception:
            # 容错：任何异常都不应阻止程序运行
            pass


# 全局单例
_default_store: Optional[VectorStore] = None


def get_vectorstore() -> VectorStore:
    """获取全局 VectorStore 实例"""
    global _default_store
    if _default_store is None:
        _default_store = VectorStore()
    return _default_store
