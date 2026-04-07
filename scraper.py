import httpx
from bs4 import BeautifulSoup


def scrape(url: str) -> str:
    """抓取网页正文，返回纯文本（截断到前3000字）"""
    try:
        resp = httpx.get(url, timeout=10, follow_redirects=True, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # 移除无用标签
        for tag in soup(["script", "style", "nav", "footer", "header", "iframe", "noscript"]):
            tag.decompose()

        # 尝试查找主内容区域
        main_content = None
        # 按优先级尝试
        selectors = ["article", "main", ".content", ".post-content", ".article-content", "#content"]
        for selector in selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        # 如果没找到，用body
        if not main_content:
            main_content = soup.body if soup.body else soup
        
        # 直接获取文本
        text = main_content.get_text(separator="\n", strip=True)
        
        # 清理多余空行
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        cleaned_text = "\n".join(lines)
        
        return cleaned_text[:3000] if cleaned_text else ""
        
    except Exception as e:
        return ""
