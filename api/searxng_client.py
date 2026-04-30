import httpx
from typing import List, Optional
from urllib.parse import urlparse

from models.search_result import SearchResult


class SearXNGClient:
    def __init__(self, base_url: str = "http://localhost:8080", timeout: int = 40, test_connection: bool = True):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        if test_connection:
            import asyncio
            asyncio.run(self._test_connection())

    async def _test_connection(self):
        """测试SearXNG连接是否可用"""
        async with httpx.AsyncClient(timeout=5) as client:
            try:
                response = await client.get(f"{self.base_url}/")
                response.raise_for_status()
            except Exception as e:
                raise ConnectionError(f"SearXNG不可用: {e}")

    async def search(
        self,
        query: str,
        num_results: int = 20,
        language: str = "zh-CN",
        time_range: Optional[str] = None,
    ) -> List[SearchResult]:
        params = {
            "q": query,
            "format": "json",
            "language": language,
        }

        if time_range:
            params["time_range"] = time_range

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/search", params=params)
            response.raise_for_status()
            data = response.json()

        results = []
        for item in data.get("results", [])[:num_results]:
            url = item.get("url", "")
            domain = urlparse(url).netloc
            result = SearchResult(
                url=url,
                title=item.get("title", ""),
                content=item.get("content", ""),
                domain=domain,
            )
            results.append(result)

        return results

    async def search_site(
        self,
        query: str,
        site: str,
        num_results: int = 10,
        language: str = "zh-CN",
        time_range: Optional[str] = None,
    ) -> List[SearchResult]:
        site_query = f"site:{site} {query}"
        return await self.search(site_query, num_results, language, time_range)
