import httpx
import logging
from typing import List, Optional
from urllib.parse import urlparse

from models.search_result import SearchResult

logger = logging.getLogger("mysearchengine.searxng_client")


class SearXNGClient:
    def __init__(self, base_url: str = "http://localhost:8080", timeout: int = 10):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def search(
        self,
        query: str,
        num_results: int = 20,
        language: str = "zh-CN",
        time_range: Optional[str] = None,
    ) -> List[SearchResult]:
        data = {
            "q": query,
            "format": "json",
            "language": language,
        }

        if time_range:
            data["time_range"] = time_range

        try:
            logger.debug(f"Requesting search from {self.base_url} for query: {query}")
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/search", data=data)
                logger.debug(f"Response status: {response.status_code}")
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

            logger.info(f"Found {len(results)} results for query: {query}")
            return results
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error searching for '{query}': {e.response.status_code} - {e}", exc_info=True)
            if e.response.status_code == 403:
                logger.error("403 Forbidden: SearXNG may have JSON format disabled or blocking requests")
            return []
        except httpx.ConnectError as e:
            logger.error(f"Network connection error searching for '{query}': {e}", exc_info=True)
            logger.error("Please check if SearXNG is running at {self.base_url}")
            return []
        except httpx.TimeoutException as e:
            logger.error(f"Request timeout searching for '{query}': {e}", exc_info=True)
            return []
        except httpx.HTTPError as e:
            logger.error(f"HTTP error searching for '{query}': {e}", exc_info=True)
            return []
        except Exception as e:
            logger.error(f"Unexpected error searching for '{query}': {e}", exc_info=True)
            return []

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
