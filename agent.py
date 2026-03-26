import json
import re

from llm import chat
from search import search
from scraper import scrape


def decompose(question: str) -> list[str]:
    """LLM 将问题拆解为子问题列表"""
    prompt = f"""你是一个研究助手。请将以下问题拆解为3-5个具体的子问题，用于搜索引擎查询。
只输出 JSON 数组格式，例如：["子问题1", "子问题2", "子问题3"]
不要输出任何其他内容。

问题：{question}"""

    response = chat(prompt)

    # 从响应中提取 JSON 数组
    match = re.search(r'\[.*\]', response, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # 兜底：按行分割
    lines = [line.strip().lstrip("0123456789.-) ") for line in response.strip().split("\n") if line.strip()]
    return lines[:5] if lines else [question]


def research(question: str, on_status=None) -> str:
    """Agent 主循环：拆解 → 搜索 → 抓取 → 生成报告

    on_status: 可选回调函数，用于输出进度信息
    """
    def status(msg):
        if on_status:
            on_status(msg)

    # 1. 拆解问题
    status("decompose")
    sub_questions = decompose(question)
    status(("sub_questions", sub_questions))

    # 2. 对每个子问题搜索并抓取
    all_materials = []
    for sq in sub_questions:
        status(("searching", sq))
        results = search(sq, max_results=5)
        status(("search_done", len(results)))

        # 抓取前3个结果的正文
        for r in results[:3]:
            content = scrape(r["url"])
            if content:
                all_materials.append({
                    "question": sq,
                    "title": r["title"],
                    "url": r["url"],
                    "content": content,
                })

    # 3. 整合素材，生成报告
    if not all_materials:
        status("no_materials")
        return "# 研究失败\n\n未能获取到任何搜索资料，可能是网络问题。请检查代理设置后重试。\n\n可在 `search.py` 中设置 `PROXY = \"socks5://127.0.0.1:7890\"` 指定代理。"

    status("generating")
    materials_text = ""
    for m in all_materials:
        materials_text += f"\n---\n来源: {m['title']} ({m['url']})\n相关子问题: {m['question']}\n内容:\n{m['content']}\n"

    # 截断素材总量，避免超出上下文
    materials_text = materials_text[:15000]

    report_prompt = f"""你是一个研究分析师。根据以下搜索资料，针对用户问题撰写一份结构化研究报告。

要求：
- 使用 Markdown 格式
- 包含：概述、主要发现（分点）、总结
- 在关键信息后标注来源链接
- 如果资料不足，如实说明

用户问题：{question}

搜索资料：
{materials_text}"""

    report = chat(report_prompt)
    return report
