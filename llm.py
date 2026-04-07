"""LLM 封装 - 基于 LangChain Ollama"""

from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage

from config import LLM_MODEL, EMBEDDING_MODEL, OLLAMA_BASE_URL


def get_llm(temperature: float = 0.7) -> ChatOllama:
    """获取 LangChain ChatOllama 实例"""
    return ChatOllama(
        model=LLM_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=temperature,
        num_ctx=2048,  # 减少上下文长度，降低显存压力
    )


def get_embeddings() -> OllamaEmbeddings:
    """获取 Ollama Embeddings 实例"""
    return OllamaEmbeddings(
        model=EMBEDDING_MODEL,
        base_url=OLLAMA_BASE_URL,
    )


def chat(prompt: str, system: str = "") -> str:
    """兼容旧接口：调用 Ollama 模型，返回文本响应"""
    llm = get_llm()
    messages = []
    if system:
        messages.append(SystemMessage(content=system))
    messages.append(HumanMessage(content=prompt))
    
    response = llm.invoke(messages)
    # response.content 可能是 str 或 list，确保返回 str
    content = response.content
    if isinstance(content, list):
        return str(content)
    return content
