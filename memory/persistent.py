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
            conn.execute("""
                CREATE TABLE IF NOT EXISTS key_findings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    research_id INTEGER,
                    finding TEXT NOT NULL,
                    confidence REAL DEFAULT 0.5,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (research_id) REFERENCES research_history(id)
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
    
    def add_finding(self, research_id: int, finding: str, confidence: float = 0.5) -> None:
        """添加研究发现"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO key_findings (research_id, finding, confidence) VALUES (?, ?, ?)",
                (research_id, finding, confidence)
            )
            conn.commit()
    
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
    
    def get_context_summary(self, query: Optional[str] = None) -> str:
        """获取记忆上下文摘要"""
        related: list[dict[str, Any]]
        if query:
            related = self.search_related(query, limit=3)
        else:
            related = self.get_recent_research(limit=3)
        
        if not related:
            return "暂无历史研究记录。"
        
        summary = "相关历史研究:\n"
        for r in related:
            summary += f"- 问题: {r['question'][:50]}...\n"
            summary += f"  摘要: {r['summary'][:100]}...\n\n" if r['summary'] else "\n"
        
        return summary


# 全局持久化记忆
_persistent_memory: Optional[PersistentMemory] = None


def get_persistent_memory() -> PersistentMemory:
    """获取全局持久化记忆实例"""
    global _persistent_memory
    if _persistent_memory is None:
        _persistent_memory = PersistentMemory()
    return _persistent_memory
