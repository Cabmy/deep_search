import warnings
warnings.filterwarnings("ignore")

import time
from ddgs import DDGS

# 代理设置
PROXY = "http://127.0.0.1:7890"

MAX_RETRIES = 2
RETRY_DELAY = 3  # 秒


def search(query: str, max_results: int = 5) -> list[dict]:
    """搜索返回 [{title, url, snippet}]，带重试机制"""
    for attempt in range(MAX_RETRIES + 1):
        try:
            results = []
            with DDGS(proxy=PROXY) as ddgs:
                for r in ddgs.text(query, max_results=max_results):
                    results.append({
                        "title": r.get("title", ""),
                        "url": r.get("href", ""),
                        "snippet": r.get("body", ""),
                    })
            if results:
                return results
        except Exception as e:
            if attempt < MAX_RETRIES:
                print(f"  [搜索失败，{RETRY_DELAY}秒后重试 ({attempt+1}/{MAX_RETRIES})...]")
                time.sleep(RETRY_DELAY)
            else:
                print(f"  [搜索出错: {type(e).__name__}]")
    return []
