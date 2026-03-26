# Deep Research - 智能研究助手

Deep Research 是一个 **CLI（命令行）研究助手**。你输入一个问题，它会：

1. 用大模型把问题拆成多个子问题
2. 每个子问题去搜索引擎搜索
3. 抓取搜索到的网页内容
4. 把所有内容喂给大模型，生成一份结构化的研究报告

**总结：自动搜索 + 阅读 + 写报告的 AI 助手。**

## 技术栈

| 类别 | 技术 | 说明 |
|------|------|------|
| 语言 | Python 3.11 | Conda 环境管理 |
| LLM 推理 | [Ollama](https://ollama.com/) | 本地大模型推理框架，GPU 加速 |
| LLM 模型 | `qwen2.5`（通义千问 2.5） | 阿里云开源模型，中文能力强 |
| 网页搜索 | [ddgs](https://pypi.org/project/ddgs/) | DuckDuckGo 搜索 Python SDK |
| 网页抓取 | [httpx](https://www.python-httpx.org/) + [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) | HTTP 请求 + HTML 解析 |
| 终端 UI | [Rich](https://github.com/Textualize/rich) | 彩色格式化终端输出、Markdown 渲染 |

## LLM 模型与参数

### 模型信息

- **模型名称**: `qwen2.5`（Qwen 2.5 系列）
- **推理框架**: Ollama（本地部署，无需 API Key）
- **运行方式**: GPU 加速推理
- **调用方式**: `ollama.chat()` 多轮对话接口

### Agent 流程参数

| 参数 | 值 | 位置 | 说明 |
|------|-----|------|------|
| 子问题数量 | 3-5 个 | `agent.py` | LLM 将用户问题拆解为 3-5 个子问题 |
| 每个子问题搜索结果数 | 5 条 | `agent.py` → `search(sq, max_results=5)` | 每个子问题返回的搜索结果数量 |
| 每个子问题抓取网页数 | 前 3 个 | `agent.py` → `results[:3]` | 从搜索结果中抓取前 3 个网页 |
| 素材总量截断 | 15000 字符 | `agent.py` → `materials_text[:15000]` | 避免超出 LLM 上下文窗口 |

### 搜索参数

| 参数 | 值 | 位置 | 说明 |
|------|-----|------|------|
| 代理地址 | `http://127.0.0.1:7890` | `search.py` → `PROXY` | Clash 代理，搜索时使用 |
| 最大重试次数 | 2 次 | `search.py` → `MAX_RETRIES` | 搜索失败后的重试次数 |
| 重试间隔 | 3 秒 | `search.py` → `RETRY_DELAY` | 每次重试之间的等待时间 |

### 抓取参数

| 参数 | 值 | 位置 | 说明 |
|------|-----|------|------|
| 请求超时 | 10 秒 | `scraper.py` → `httpx.get(timeout=10)` | 网页请求超时时间 |
| 正文截断 | 3000 字符 | `scraper.py` → `text[:3000]` | 每个网页提取的最大文本量 |
| User-Agent | `DeepResearchBot/1.0` | `scraper.py` | 自定义请求标识 |
| 解析方式 | 提取 `<p>` 标签文本 | `scraper.py` | 仅抓取段落标签内容 |

## 项目结构

```
deep_search/
├── main.py          # CLI 入口，Rich 终端输出，报告保存到 reports/
├── agent.py         # Agent 主循环：拆解 → 搜索 → 抓取 → 生成报告
├── llm.py           # Ollama 模型调用封装
├── search.py        # DuckDuckGo 搜索（带代理和重试）
├── scraper.py       # 网页正文抓取（httpx + BeautifulSoup）
├── requirements.txt # Python 依赖
└── reports/         # 生成的研究报告存放目录
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

# 拉取 Qwen 2.5 模型
ollama pull qwen2.5
```

### 3. 运行

```bash
python main.py
```

输入研究问题后，程序会自动完成搜索、抓取、生成报告的全流程，最终报告保存在 `reports/` 目录下。

## 网络代理配置

搜索功能需要通过代理访问 DuckDuckGo，默认使用 Clash 代理：

- 代理地址：`http://127.0.0.1:7890`（在 `search.py` 中的 `PROXY` 常量修改）
- 注意：网页抓取（`scraper.py`）不经过代理

## 已知限制

- 模型越大效果越好，但推理耗时也相应增加
- 网页抓取仅提取 `<p>` 标签，可能遗漏其他元素中的内容
- 网页抓取为串行执行，无并发
- 素材截断到 15000 字符，超长内容可能丢失信息
