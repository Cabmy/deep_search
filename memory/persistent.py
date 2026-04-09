"""持久化记忆管理 - 基于 SQLite"""

import sqlite3
import json
from typing import Optional, Any

from config import MEMORY_DB_PATH


class PersistentMemory:
    """持久化记忆 - 跨会话保存研究历史"""
    
    def __init__(self, db_path: Optional[str] = None) -> None:
        self.db_path: str = db_path or MEMORY_DB_PATH
        self._init_db()
    
    def _init_db(self) -> None:
        """初始化数据库表"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS research_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT NOT NULL,
                    summary TEXT,
                    sources TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    
    def save_research(self, question: str, summary: str, sources: Optional[list[str]] = None) -> int:
        """保存研究记录"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO research_history (question, summary, sources) VALUES (?, ?, ?)",
                (question, summary, json.dumps(sources or []))
            )
            conn.commit()
            return cursor.lastrowid if cursor.lastrowid is not None else 0
    

    def get_recent_research(self, limit: int = 10) -> list[dict[str, Any]]:
        """获取最近的研究历史"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM research_history ORDER BY created_at DESC LIMIT ?",
                (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def search_related(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        """搜索相关的历史研究（简单关键词匹配）"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM research_history WHERE question LIKE ? OR summary LIKE ? ORDER BY created_at DESC LIMIT ?",
                (f"%{query}%", f"%{query}%", limit)
            )
            return [dict(row) for row in cursor.fetchall()]


# 全局持久化记忆
_persistent_memory: Optional[PersistentMemory] = None


def get_persistent_memory() -> PersistentMemory:
    """获取全局持久化记忆实例"""
    global _persistent_memory
    if _persistent_memory is None:
        _persistent_memory = PersistentMemory()
    return _persistent_memory
