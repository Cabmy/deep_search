import httpx
from bs4 import BeautifulSoup


def scrape(url: str) -> str:
    """抓取网页正文，返回纯文本（截断到前3000字）"""
    try:
        resp = httpx.get(url, timeout=10, follow_redirects=True, headers={
            "User-Agent": "Mozilla/5.0 (compatible; DeepResearchBot/1.0)"
        })
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # 移除 script 和 style 标签
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        paragraphs = soup.find_all("p")
        text = "\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
        return text[:3000]
    except Exception:
        return ""
