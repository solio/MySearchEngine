import asyncio
from typing import List, Dict, Optional
from urllib.parse import urlparse

from api.searxng_client import SearXNGClient
from api.duckduckgo_client import DuckDuckGoClient
from api.mock_client import MockClient
from filters.rule_engine import RuleEngine
from models.site_config import SiteConfig
from models.search_result import SearchResult


class SearchService:
    def __init__(
        self,
        searxng_url: str = "http://localhost:8080",
        config_path: str = "config/quality_sites.yaml",
        use_mock: bool = False,
    ):
        self.config = SiteConfig(config_path)
        self.rule_engine = RuleEngine(self.config)
        self.client_type = "unknown"

        if use_mock:
            self.client = MockClient()
            self.client_type = "mock"
            print("使用Mock搜索模式")
        else:
            # 默认直接用Mock，避免连接问题
            self.client = MockClient()
            self.client_type = "mock"
            print("使用Mock搜索模式（启动SearXNG后可切换）")

    async def search(
        self,
        query: str,
        num_results: int = 20,
        time_range: Optional[str] = "month",
        use_quality_sites_only: bool = False,
        debug: bool = False,
    ) -> tuple[List[SearchResult], Dict]:
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

        filtered, spam_stats = self.rule_engine.filter_and_score(all_results, debug)
        return filtered[:num_results], spam_stats

    async def targeted_search(
        self,
        query: str,
        sites: Optional[List[str]] = None,
        num_results: int = 20,
        time_range: Optional[str] = "month",
        debug: bool = False,
    ) -> tuple[List[SearchResult], Dict]:
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

        filtered, spam_stats = self.rule_engine.filter_and_score(all_results, debug)
        return filtered[:num_results], spam_stats
