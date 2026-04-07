"""搜索工具 - 封装 DuckDuckGo 搜索"""

from langchain_core.tools import tool

from search import search as ddg_search
from config import SEARCH_MAX_RESULTS


@tool
def search_tool(query: str) -> str:
    """搜索互联网获取相关信息。
    
    使用 DuckDuckGo 搜索引擎搜索指定的查询词，返回搜索结果列表。
    每个结果包含标题、URL 和摘要。
    
    Args:
        query: 要搜索的关键词或问题
    
    Returns:
        格式化的搜索结果，包含标题、URL 和摘要
    """
    results = ddg_search(query, max_results=SEARCH_MAX_RESULTS)
    
    if not results:
        return f"未找到与 '{query}' 相关的搜索结果。请尝试其他关键词。"
    
    output = f"搜索 '{query}' 找到 {len(results)} 条结果:\n\n"
    for i, r in enumerate(results, 1):
        output += f"{i}. {r['title']}\n"
        output += f"   URL: {r['url']}\n"
        output += f"   摘要: {r['snippet']}\n\n"
    
    return output
