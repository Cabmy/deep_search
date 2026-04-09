"""ReAct 研究 Agent - 基于 LangChain"""

import json
import re
from typing import Callable, Any

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_core.callbacks import BaseCallbackHandler

from llm import get_llm, chat
from tools import search_tool, scrape_tool, rag_retrieve_tool, analyze_tool
from memory import get_session_memory, get_persistent_memory
from rag import get_vectorstore
from config import AGENT_MAX_ITERATIONS, MEMORY_MODE


class ToolCallbackHandler(BaseCallbackHandler):
    """工具调用监控回调"""
    def __init__(self, on_status: Callable[[Any], None] | None = None):
        self.on_status = on_status
    
    def on_tool_start(self, serialized: dict, input_str: str, **kwargs) -> None:
        tool_name = serialized.get("name", "未知工具")
        if self.on_status:
            self.on_status(("tool_start", tool_name, str(input_str)[:100]))
    
    def on_tool_end(self, output: Any, **kwargs) -> None:
        if self.on_status:
            # output可能是ToolMessage对象或字符串
            output_str = str(output.content if hasattr(output, 'content') else output)
            self.on_status(("tool_end", output_str[:100]))


# Agent 系统提示
SYSTEM_PROMPT = """你是一个中文研究助手。

## 工作流程（严格按顺序执行）:

### 第1步: 搜索
调用 search_tool，关键词必须是中文。

### 第2步: 抓取网页（重要！）
- 必须抓取至少3个URL
- 选择URL时，优先选择URL中包含目标关键词的链接
- 例如查"上海天气"，选 tianqi.com/shanghai/ 而不是 tianqi.com/（首页可能是其他城市）
- 避免选择首页、导航页，选择具体内容页

### 第3步: 检索知识库
调用 rag_retrieve_tool 检索已保存的内容。

### 第4步: 生成报告
报告必须包含抓取到的具体数据，不能只写"详细内容"或网站名称。

## 报告格式:

# [主题]

## 概述
搜索了X，抓取了Y个网页。

## 主要发现

### 1. [发现标题]
[具体内容：数字、日期、事实等]
来源: URL

### 2. [发现标题]
[具体内容]
来源: URL

## 总结
[综合分析]"""


def create_research_agent() -> Any:
    """创建研究 Agent"""
    llm = get_llm(temperature=0.3)
    tools = [search_tool, scrape_tool, rag_retrieve_tool, analyze_tool]
    
    return create_agent(
        model=llm,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
    )


def research(question: str, on_status: Callable[[Any], None] | None = None, use_memory: bool = True) -> str:
    """执行研究任务
    
    Args:
        question: 研究问题
        on_status: 状态回调函数
        use_memory: 是否使用记忆管理
    
    Returns:
        研究报告 (Markdown 格式)
    """
    def status(msg: Any) -> None:
        if on_status:
            on_status(msg)
    
    # 清理之前的向量库（每次研究独立）
    status("initializing")
    vectorstore = get_vectorstore()
    vectorstore.clear()
    
    # 准备记忆上下文
    memory_context = ""
    if use_memory and MEMORY_MODE in ("persistent", "both"):
        persistent_memory = get_persistent_memory()
        related_history = persistent_memory.search_related(question, limit=2)
        if related_history:
            memory_context = "\n\n历史研究参考:\n"
            for r in related_history:
                memory_context += f"- 曾研究过: {r['question']}\n"
                if r.get('summary'):
                    # 显示更长的摘要（最多600字），帮助LLM更好地利用历史知识
                    summary_preview = r['summary'][:600] + "..." if len(r['summary']) > 600 else r['summary']
                    memory_context += f"  历史研究摘要:\n{summary_preview}\n"
    
    # 创建并运行 Agent
    status("thinking")
    agent = create_research_agent()
    
    try:
        # 构建输入消息
        session_memory = get_session_memory()
        session_context = session_memory.get_context_string()

        user_message = question
        if session_context:
            user_message = f"{session_context}\n\n当前问题：{question}"
        if memory_context:
            user_message += memory_context

        messages = [HumanMessage(content=user_message)]
        
        # 运行 Agent（带详细日志）
        result: dict[str, Any] = agent.invoke(
            {"messages": messages},
            config={
                "recursion_limit": AGENT_MAX_ITERATIONS * 2,
                "callbacks": [ToolCallbackHandler(on_status)]
            }
        )
        
        # 提取最终响应
        final_messages = result.get("messages", [])
        report = ""
        for msg in reversed(final_messages):
            if hasattr(msg, 'content') and msg.content:
                # 跳过工具调用消息，只取纯文本响应
                if not getattr(msg, 'tool_calls', None):
                    report = msg.content
                    break
        
        if not report:
            report = "# 研究完成\n\n未能生成有效报告，请重试。"
        
        # 记录研究过程
        if use_memory:
            session_memory = get_session_memory()
            session_memory.add_user_message(question)
            session_memory.add_ai_message(report)
            
            # 持久化保存
            if MEMORY_MODE in ("persistent", "both"):
                persistent_memory = get_persistent_memory()
                persistent_memory.save_research(
                    question=question,
                    summary=report[:2000],  # 扩大到2000字，保留更多上下文
                    sources=[],
                )
        
        status("done")
        return report
        
    except Exception as e:
        status("error")
        return f"# 研究失败\n\n执行过程中出现错误: {str(e)}\n\n请检查网络连接和 Ollama 服务状态后重试。"


# # 保持向后兼容的 decompose 函数
# def decompose(question: str) -> list[str]:
#     """LLM 将问题拆解为子问题列表（保持向后兼容）"""
#     prompt = f"""你是一个研究助手。请将以下问题拆解为3-5个具体的子问题，用于搜索引擎查询。
# 只输出 JSON 数组格式，例如：["子问题1", "子问题2", "子问题3"]
# 不要输出任何其他内容。

# 问题：{question}"""

#     response = chat(prompt)

#     match = re.search(r'\[.*\]', response, re.DOTALL)
#     if match:
#         try:
#             return json.loads(match.group())
#         except json.JSONDecodeError:
#             pass

#     lines = [line.strip().lstrip("0123456789.-) ") for line in response.strip().split("\n") if line.strip()]
#     return lines[:5] if lines else [question]
