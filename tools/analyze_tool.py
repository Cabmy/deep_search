"""分析工具 - 使用 LLM 分析内容"""

from langchain_core.tools import tool

from llm import chat


@tool
def analyze_tool(content: str, instruction: str = "总结要点") -> str:
    """分析或总结给定的内容。
    
    使用 LLM 对提供的文本内容进行分析、总结或按指定方式处理。
    可用于在研究过程中整理中间发现。
    
    Args:
        content: 要分析的文本内容
        instruction: 分析指令，如 "总结要点"、"提取关键事实"、"列出争议点" 等
    
    Returns:
        分析结果
    """
    if not content.strip():
        return "没有提供内容进行分析。"
    
    prompt = f"""请对以下内容进行分析。

分析要求: {instruction}

内容:
{content[:5000]}

请提供清晰、结构化的分析结果:"""

    return chat(prompt)
