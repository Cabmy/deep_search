"""抓取工具 - 抓取网页并存入向量库"""

from langchain_core.tools import tool
from langchain_core.documents import Document

from scraper import scrape as fetch_page
from rag import get_vectorstore


@tool
def scrape_tool(url: str) -> str:
    """抓取网页内容并保存到知识库。
    
    获取指定 URL 的网页内容，提取正文文本，并自动保存到向量知识库中供后续检索。
    
    Args:
        url: 要抓取的网页 URL
    
    Returns:
        抓取的网页内容摘要，或错误信息
    """
    content = fetch_page(url)
    
    if not content:
        return f"无法抓取 {url} 的内容。可能是网页无法访问或内容为空。"
    
    # 存入向量库
    vectorstore = get_vectorstore()
    doc = Document(
        page_content=content,
        metadata={"source": url, "type": "webpage"}
    )
    vectorstore.add_documents([doc])
    
    # 返回摘要
    preview = content[:500] + "..." if len(content) > 500 else content
    return f"已抓取并保存 {url} 的内容 ({len(content)} 字符)。\n\n内容预览:\n{preview}"
