# Deep Research - 智能研究助手

Deep Research 是一个基于 **LangChain ReAct Agent** 的 CLI 研究助手，具备自主决策能力和 RAG（检索增强生成）功能。

## 核心特性

✨ **ReAct Agent 自主决策** - Agent 自主选择搜索策略、判断信息充分性，动态调整研究深度  
🗄️ **ChromaDB 向量检索** - 抓取内容自动存入向量库，支持语义检索复用  
🧠 **双模式记忆管理** - 会话内记忆 + 可选持久化历史记录  
🔧 **4 个工具集成** - 搜索、抓取、RAG 检索、内容分析

## 技术栈

| 类别       | 技术                                                                                                      | 说明                        |
| ---------- | --------------------------------------------------------------------------------------------------------- | --------------------------- |
| Agent 框架 | **LangChain** + **LangGraph**                                                                             | ReAct Agent，自主工具调用   |
| RAG        | **ChromaDB** + Ollama Embeddings                                                                          | 本地向量数据库，语义检索    |
| LLM 推理   | [Ollama](https://ollama.com/)                                                                             | 本地大模型推理，GPU 加速    |
| LLM 模型   | `qwen2.5` (通义千问 2.5)                                                                                  | 阿里开源中文模型            |
| 网页搜索   | [ddgs](https://pypi.org/project/ddgs/)                                                                    | DuckDuckGo 搜索 Python SDK  |
| 网页抓取   | [httpx](https://www.python-httpx.org/) + [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) | HTTP 请求 + HTML 解析       |
| 记忆管理   | LangChain Memory + SQLite                                                                                 | 会话内/持久化记忆           |
| 终端 UI    | [Rich](https://github.com/Textualize/rich)                                                                | 彩色终端输出、Markdown 渲染 |

## 架构设计

```
用户输入问题
    ↓
ReAct Agent (自主决策循环)
    ├── 🔍 search_tool: 搜索互联网
    ├── 📄 scrape_tool: 抓取网页 → 自动存入 ChromaDB
    ├── 🗄️ rag_tool: 语义检索已抓取内容
    └── 🤖 analyze_tool: LLM 分析总结
    ↓
生成 Markdown 研究报告
```

## 项目结构

```
deep_search/
├── main.py              # CLI 入口
├── agent.py             # ReAct Agent 核心
├── config.py            # 集中配置管理
├── llm.py               # LangChain Ollama 集成
├── tools/               # LangChain 工具集
│   ├── search_tool.py   # DuckDuckGo 搜索
│   ├── scrape_tool.py   # 网页抓取 + 存入向量库
│   ├── rag_tool.py      # ChromaDB 语义检索
│   └── analyze_tool.py  # LLM 内容分析
├── rag/                 # RAG 模块
│   └── vectorstore.py   # ChromaDB 封装
├── memory/              # 记忆管理
│   ├── session.py       # 会话内记忆
│   └── persistent.py    # 持久化记忆 (SQLite)
├── search.py            # 搜索底层实现
├── scraper.py           # 抓取底层实现
└── reports/             # 生成的报告目录
```

## 快速开始

### 1. 环境准备

```bash
# 创建并激活 Conda 环境
conda create -n deep_search python=3.11
conda activate deep_search

# 安装依赖
pip install -r requirements.txt
```

### 2. 启动 Ollama 并拉取模型

```bash
# 启动 Ollama 服务
nohup ollama serve &

# 拉取 Qwen 2.5 模型（用于推理和 Embeddings）
ollama pull qwen2.5
```

### 3. 运行

```bash
python main.py
```

## 配置说明

所有配置项在 `config.py` 中：

```python
# LLM 配置
LLM_MODEL = "qwen2.5"              # 推理模型
EMBEDDING_MODEL = "qwen2.5"        # Embedding 模型

# 代理设置
PROXY = "http://127.0.0.1:7890"    # 搜索代理（Clash）

# ChromaDB 配置
CHROMA_PERSIST_DIR = "./chroma_db" # 向量库路径

# 记忆管理
MEMORY_MODE = "session"            # "session" | "persistent" | "both"

# Agent 配置
AGENT_MAX_ITERATIONS = 15          # 最大 ReAct 循环次数
```

## RAG 工作机制

1. **抓取时自动入库**：`scrape_tool` 抓取网页后自动调用 `vectorstore.add_documents()`
2. **语义检索**：`rag_retrieve_tool` 使用 Ollama Embeddings 进行向量化，ChromaDB 相似度检索
3. **复用避免重复**：同一会话内，Agent 可通过 RAG 检索已抓取内容，无需重复抓取

## 记忆管理

### 会话内记忆 (Session Memory)
- 保存当前研究的对话历史
- 每次运行结束自动清空

### 持久化记忆 (Persistent Memory)
- 跨会话保存研究历史到 SQLite (`memory.db`)
- 可查询历史研究记录
- 通过 `MEMORY_MODE` 配置开关

## 网络代理配置

搜索功能需要代理访问 DuckDuckGo：

- 默认代理：`http://127.0.0.1:7890` (Clash)
- 修改位置：`config.py` 中的 `PROXY` 常量
- **注意**：网页抓取不经过代理

## 依赖项

核心依赖（见 `requirements.txt`）：

```
langchain>=0.3.0
langchain-ollama>=0.2.0
langchain-chroma>=0.2.0
langchain-community>=0.3.0
langgraph>=0.2.0
chromadb>=0.5.0
ollama
ddgs
httpx
beautifulsoup4
rich
```
