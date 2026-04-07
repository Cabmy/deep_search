"""RAG 检索工具 - 从向量库检索相关内容"""

from langchain_core.tools import tool

from rag import get_vectorstore


@tool
def rag_retrieve_tool(query: str) -> str:
    """从知识库检索相关资料。
    
    使用语义搜索从已抓取并保存的网页内容中检索与查询最相关的资料。
    在抓取了多个网页后使用此工具可以快速找到相关信息。
    
    Args:
        query: 要检索的问题或关键词
    
    Returns:
        检索到的相关内容及其来源
    """
    vectorstore = get_vectorstore()
    
    try:
        results = vectorstore.similarity_search_with_score(query, k=4)
    except Exception:
        return "知识库为空。请先使用 scrape_tool 抓取一些网页内容。"
    
    if not results:
        return f"未找到与 '{query}' 相关的已保存资料。请先搜索并抓取相关网页。"
    
    output = f"从知识库检索到 {len(results)} 条相关资料:\n\n"
    for i, (doc, score) in enumerate(results, 1):
        source = doc.metadata.get("source", "未知来源")
        preview = doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content
        output += f"[{i}] 来源: {source}\n"
        output += f"    相关度: {1 - score:.2f}\n"  # ChromaDB 返回距离，转为相似度
        output += f"    内容: {preview}\n\n"
    
    return output
