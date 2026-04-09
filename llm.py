"""LLM 封装 - 支持 Ollama / 阿里百炼"""

from typing import Any

from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import SecretStr

from config import (
    LLM_PROVIDER,
    OLLAMA_BASE_URL,
    OLLAMA_LLM_MODEL,
    OLLAMA_EMBEDDING_MODEL,
    BAILIAN_API_KEY,
    BAILIAN_LLM_MODEL,
    BAILIAN_EMBEDDING_MODEL,
    BAILIAN_BASE_URL,
)


def _require_bailian_key() -> str:
    if not BAILIAN_API_KEY:
        raise ValueError("未配置 BAILIAN_API_KEY，请先设置阿里百炼 API Key。")
    return BAILIAN_API_KEY


def get_llm(temperature: float = 0.7) -> Any:
    """获取 LangChain Chat 模型实例（按 LLM_PROVIDER 选择）"""
    provider = LLM_PROVIDER.lower().strip()
    if provider == "ollama":
        return ChatOllama(
            model=OLLAMA_LLM_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=temperature,
            num_ctx=2048,  # 减少上下文长度，降低显存压力
        )

    if provider == "bailian":
        from langchain_openai import ChatOpenAI

        chat_kwargs: dict[str, Any] = {
            "model": BAILIAN_LLM_MODEL,
            "api_key": SecretStr(_require_bailian_key()),
            "base_url": BAILIAN_BASE_URL,
            "temperature": temperature,
        }
        return ChatOpenAI(**chat_kwargs)

    raise ValueError(f"不支持的 LLM_PROVIDER: {LLM_PROVIDER}，可选: ollama / bailian")


def get_embeddings() -> Any:
    """获取 Embeddings 实例（按 LLM_PROVIDER 选择）"""
    provider = LLM_PROVIDER.lower().strip()
    if provider == "ollama":
        return OllamaEmbeddings(
            model=OLLAMA_EMBEDDING_MODEL,
            base_url=OLLAMA_BASE_URL,
        )

    if provider == "bailian":
        from langchain_community.embeddings import DashScopeEmbeddings

        return DashScopeEmbeddings(
            model=BAILIAN_EMBEDDING_MODEL,
            dashscope_api_key=_require_bailian_key(),
        )

    raise ValueError(f"不支持的 LLM_PROVIDER: {LLM_PROVIDER}，可选: ollama / bailian")


def chat(prompt: str, system: str = "") -> str:
    """兼容旧接口：调用当前 provider 模型，返回文本响应"""
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
