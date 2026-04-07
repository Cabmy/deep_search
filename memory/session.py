"""会话内记忆管理"""

from typing import Optional
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage


class SessionMemory:
    """会话内记忆 - 基于消息历史"""
    
    def __init__(self, max_messages: int = 20) -> None:
        self.max_messages: int = max_messages
        self._history: InMemoryChatMessageHistory = InMemoryChatMessageHistory()
    
    def add_user_message(self, message: str) -> None:
        """添加用户消息"""
        self._history.add_user_message(message)
        self._trim_history()
    
    def add_ai_message(self, message: str) -> None:
        """添加 AI 消息"""
        self._history.add_ai_message(message)
        self._trim_history()
    
    def _trim_history(self) -> None:
        """限制消息数量"""
        if len(self._history.messages) > self.max_messages:
            self._history.messages = self._history.messages[-self.max_messages:]
    
    def get_messages(self) -> list[BaseMessage]:
        """获取所有消息"""
        return self._history.messages
    
    def get_context_string(self) -> str:
        """获取历史上下文字符串"""
        if not self._history.messages:
            return ""
        
        context = "历史对话:\n"
        for msg in self._history.messages[-6:]:
            role = "用户" if isinstance(msg, HumanMessage) else "助手"
            # 处理 content 可能是 str 或 list 的情况
            content_str = msg.content if isinstance(msg.content, str) else str(msg.content)
            content = content_str[:200] + "..." if len(content_str) > 200 else content_str
            context += f"{role}: {content}\n"
        return context
    
    def clear(self) -> None:
        """清空记忆"""
        self._history.clear()


# 全局会话记忆
_session_memory: Optional[SessionMemory] = None


def get_session_memory() -> SessionMemory:
    """获取全局会话记忆实例"""
    global _session_memory
    if _session_memory is None:
        _session_memory = SessionMemory()
    return _session_memory


def reset_session_memory() -> None:
    """重置会话记忆"""
    global _session_memory
    if _session_memory:
        _session_memory.clear()
    _session_memory = None
