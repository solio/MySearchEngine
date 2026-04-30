import httpx
from typing import List
from urllib.parse import urlparse, quote

from models.search_result import SearchResult


class DuckDuckGoClient:
    def __init__(self, timeout: int = 40):
        self.timeout = timeout
        self.base_url = "https://duckduckgo.com/html"

    async def search(
        self,
        query: str,
        num_results: int = 20,
        time_range: str = None,
    ) -> List[SearchResult]:
        params = {
            "q": query,
        }

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            # 使用duckduckgo API endpoint
            response = await client.get(
                "https://api.duckduckgo.com/",
                params={
                    "q": query,
                    "format": "json",
                    "no_html": 1,
                    "skip_disambig": 1,
                },
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()

        results = []

        for item in data.get("Results", []):
            url = item.get("FirstURL", "")
            domain = urlparse(url).netloc
            result = SearchResult(
                url=url,
                title=item.get("Text", "")[:80],
                content=item.get("Text", ""),
                domain=domain,
            )
            results.append(result)

        for topic in data.get("RelatedTopics", []):
            if "FirstURL" in topic:
                url = topic.get("FirstURL", "")
                domain = urlparse(url).netloc
                result = SearchResult(
                    url=url,
                    title=topic.get("Text", "")[:80],
                    content=topic.get("Text", ""),
                    domain=domain,
                )
                results.append(result)

        return results[:num_results]

    async def search_site(
        self,
        query: str,
        site: str,
        num_results: int = 10,
        time_range: str = None,
    ) -> List[SearchResult]:
        site_query = f"site:{site} {query}"
        return await self.search(site_query, num_results, time_range)
