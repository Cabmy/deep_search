"""集中配置管理"""

import os

# LLM 配置
LLM_MODEL = "qwen2.5:7b"  # 7b模型指令遵循能力更强
EMBEDDING_MODEL = "qwen2.5:1.5b"  # embedding用小模型
OLLAMA_BASE_URL = "http://localhost:11434"

# 代理设置
PROXY = "http://127.0.0.1:7890"

# ChromaDB 配置
CHROMA_PERSIST_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")
CHROMA_COLLECTION_NAME = "research_docs"

# 记忆管理
MEMORY_MODE = "both"  # "session" | "persistent" | "both"
MEMORY_DB_PATH = os.path.join(os.path.dirname(__file__), "memory.db")

# 搜索配置
SEARCH_MAX_RESULTS = 5
SCRAPE_MAX_PAGES = 3
SCRAPE_MAX_CHARS = 3000

# Agent 配置
AGENT_MAX_ITERATIONS = 15
