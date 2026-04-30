import asyncio
from typing import List, Dict, Optional
from urllib.parse import urlparse

from api.searxng_client import SearXNGClient
from filters.rule_engine import RuleEngine
from models.site_config import SiteConfig
from models.search_result import SearchResult


class SearchService:
    def __init__(
        self,
        searxng_url: str = "http://localhost:8080",
        config_path: str = "config/quality_sites.yaml",
    ):
        self.client = SearXNGClient(searxng_url)
        self.config = SiteConfig(config_path)
        self.rule_engine = RuleEngine(self.config)

    async def search(
        self,
        query: str,
        num_results: int = 20,
        time_range: Optional[str] = "month",
        use_quality_sites_only: bool = False,
    ) -> List[SearchResult]:
        tasks = []

        if use_quality_sites_only:
            for site in self.config.quality_sites:
                tasks.append(
                    self.client.search_site(query, site.domain, num_results=5, time_range=time_range)
                )
        else:
            tasks.append(self.client.search(query, num_results, time_range=time_range))

            for site in self.config.quality_sites:
                tasks.append(
                    self.client.search_site(query, site.domain, num_results=3, time_range=time_range)
                )

        all_results = []
        seen_urls = set()

        results_list = await asyncio.gather(*tasks, return_exceptions=True)
        for results in results_list:
            if isinstance(results, Exception):
                continue
            for result in results:
                if result.url not in seen_urls:
                    seen_urls.add(result.url)
                    all_results.append(result)

        filtered = self.rule_engine.filter_and_score(all_results)
        return filtered[:num_results]

    async def targeted_search(
        self,
        query: str,
        sites: Optional[List[str]] = None,
        num_results: int = 20,
        time_range: Optional[str] = "month",
    ) -> List[SearchResult]:
        if sites is None:
            sites = [site.domain for site in self.config.quality_sites]

        tasks = []
        for site in sites:
            tasks.append(
                self.client.search_site(query, site, num_results=5, time_range=time_range)
            )

        all_results = []
        seen_urls = set()

        results_list = await asyncio.gather(*tasks, return_exceptions=True)
        for results in results_list:
            if isinstance(results, Exception):
                continue
            for result in results:
                if result.url not in seen_urls:
                    seen_urls.add(result.url)
                    all_results.append(result)

        filtered = self.rule_engine.filter_and_score(all_results)
        return filtered[:num_results]
