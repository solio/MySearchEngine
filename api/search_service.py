import asyncio
import logging
from typing import List, Dict, Optional
from urllib.parse import urlparse

from api.searxng_client import SearXNGClient
from api.duckduckgo_client import DuckDuckGoClient
from api.mock_client import MockClient
from filters.rule_engine import RuleEngine
from models.site_config import SiteConfig
from models.search_result import SearchResult

logger = logging.getLogger("mysearchengine.search_service")


class SearchService:
    def __init__(
        self,
        searxng_url: str = "http://localhost:8080",
        config_path: str = "config/quality_sites.yaml",
        use_mock: bool = False,
    ):
        self.config = SiteConfig(config_path)
        self.rule_engine = RuleEngine(self.config)

        if use_mock:
            self.client = MockClient()
            logger.info("使用Mock搜索模式")
            self.primary_client = None
            self.fallback_client = None
        else:
            self.primary_client = SearXNGClient(searxng_url)
            self.fallback_client = DuckDuckGoClient()
            self.client = self.primary_client
            logger.info("使用SearXNG搜索（DuckDuckGo作为备用）")

    async def _search_with_client(
        self,
        client,
        query: str,
        num_results: int = 20,
        time_range: Optional[str] = "month",
        use_quality_sites_only: bool = False,
    ) -> List[SearchResult]:
        tasks = []

        if use_quality_sites_only:
            for site in self.config.quality_sites:
                tasks.append(
                    client.search_site(query, site.domain, num_results=5, time_range=time_range)
                )
        else:
            tasks.append(client.search(query, num_results, time_range=time_range))

            for site in self.config.quality_sites:
                tasks.append(
                    client.search_site(query, site.domain, num_results=3, time_range=time_range)
                )

        all_results = []
        seen_urls = set()

        results_list = await asyncio.gather(*tasks, return_exceptions=True)
        for i, results in enumerate(results_list):
            if isinstance(results, Exception):
                logger.warning(f"搜索任务{i}失败: {results}", exc_info=True)
                continue
            for result in results:
                if result.url not in seen_urls:
                    seen_urls.add(result.url)
                    all_results.append(result)

        return all_results

    async def search(
        self,
        query: str,
        num_results: int = 20,
        time_range: Optional[str] = "month",
        use_quality_sites_only: bool = False,
        debug: bool = False,
    ) -> tuple[List[SearchResult], Dict]:
        logger.info(f"开始搜索: '{query}', 模式: {'仅优质站点' if use_quality_sites_only else '普通'}")

        # 先用主客户端
        all_results = []
        if self.primary_client:
            logger.debug("尝试主客户端 (SearXNG)")
            all_results = await self._search_with_client(
                self.primary_client, query, num_results, time_range, use_quality_sites_only
            )
            logger.info(f"主客户端返回: {len(all_results)}条结果")

        # 如果主客户端没有结果，尝试备用客户端
        if len(all_results) == 0 and self.fallback_client:
            logger.warning("主客户端无结果，尝试备用客户端 (DuckDuckGo)")
            all_results = await self._search_with_client(
                self.fallback_client, query, num_results, time_range, use_quality_sites_only
            )
            logger.info(f"备用客户端返回: {len(all_results)}条结果")

        # 如果都没结果，用mock
        if len(all_results) == 0 and self.primary_client:
            logger.warning("所有客户端都无结果，使用Mock")
            mock_client = MockClient()
            all_results = await self._search_with_client(
                mock_client, query, num_results, time_range, use_quality_sites_only
            )

        logger.info(f"原始搜索结果: {len(all_results)}条")
        filtered, spam_stats = self.rule_engine.filter_and_score(all_results, debug)
        logger.info(f"过滤后结果: {len(filtered)}条")

        if spam_stats.get("failure_reason"):
            logger.warning(f"搜索结果异常: {spam_stats['failure_message']}")

        return filtered[:num_results], spam_stats

    async def _targeted_search_with_client(
        self,
        client,
        query: str,
        sites: List[str],
        num_results: int = 20,
        time_range: Optional[str] = "month",
    ) -> List[SearchResult]:
        tasks = []
        for site in sites:
            tasks.append(
                client.search_site(query, site, num_results=5, time_range=time_range)
            )

        all_results = []
        seen_urls = set()

        results_list = await asyncio.gather(*tasks, return_exceptions=True)
        for i, results in enumerate(results_list):
            if isinstance(results, Exception):
                logger.warning(f"站点搜索任务{i}失败: {results}", exc_info=True)
                continue
            for result in results:
                if result.url not in seen_urls:
                    seen_urls.add(result.url)
                    all_results.append(result)

        return all_results

    async def targeted_search(
        self,
        query: str,
        sites: Optional[List[str]] = None,
        num_results: int = 20,
        time_range: Optional[str] = "month",
        debug: bool = False,
    ) -> tuple[List[SearchResult], Dict]:
        logger.info(f"开始定向搜索: '{query}'")
        if sites is None:
            sites = [site.domain for site in self.config.quality_sites]

        logger.debug(f"在{len(sites)}个站点上搜索")

        # 先用主客户端
        all_results = []
        if self.primary_client:
            logger.debug("尝试主客户端 (SearXNG)")
            all_results = await self._targeted_search_with_client(
                self.primary_client, query, sites, num_results, time_range
            )
            logger.info(f"主客户端返回: {len(all_results)}条结果")

        # 如果主客户端没有结果，尝试备用客户端
        if len(all_results) == 0 and self.fallback_client:
            logger.warning("主客户端无结果，尝试备用客户端 (DuckDuckGo)")
            all_results = await self._targeted_search_with_client(
                self.fallback_client, query, sites, num_results, time_range
            )
            logger.info(f"备用客户端返回: {len(all_results)}条结果")

        # 如果都没结果，用mock
        if len(all_results) == 0 and self.primary_client:
            logger.warning("所有客户端都无结果，使用Mock")
            mock_client = MockClient()
            all_results = await self._targeted_search_with_client(
                mock_client, query, sites, num_results, time_range
            )

        logger.info(f"原始搜索结果: {len(all_results)}条")
        filtered, spam_stats = self.rule_engine.filter_and_score(all_results, debug)
        logger.info(f"过滤后结果: {len(filtered)}条")

        if spam_stats.get("failure_reason"):
            logger.warning(f"搜索结果异常: {spam_stats['failure_message']}")

        return filtered[:num_results], spam_stats
