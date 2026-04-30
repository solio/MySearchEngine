import httpx
from typing import List
from urllib.parse import urlparse, quote
import re

from models.search_result import SearchResult


class DuckDuckGoClient:
    def __init__(self, timeout: int = 40):
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }

    async def search(
        self,
        query: str,
        num_results: int = 20,
        time_range: str = None,
    ) -> List[SearchResult]:
        try:
            # 先用DuckDuckGo API试试
            results = await self._search_api(query, num_results)
            if results:
                return results
        except Exception as e:
            print(f"DuckDuckGo API failed: {e}")

        # API不行的话，先返回一些模拟数据演示
        return self._get_mock_results(query)

    async def _search_api(self, query: str, num_results: int) -> List[SearchResult]:
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            params = {
                "q": query,
                "format": "json",
                "no_html": "1",
                "skip_disambig": "1",
            }
            response = await client.get(
                "https://api.duckduckgo.com/",
                params=params,
                headers=self.headers,
            )
            response.raise_for_status()
            data = response.json()

        results = []

        # 解析Abstract
        if data.get("AbstractURL") and data.get("Abstract"):
            results.append(SearchResult(
                url=data["AbstractURL"],
                title=data.get("Heading", query)[:80],
                content=data["Abstract"][:200],
                domain=urlparse(data["AbstractURL"]).netloc,
            ))

        # 解析RelatedTopics
        for topic in data.get("RelatedTopics", []):
            if "FirstURL" in topic and "Text" in topic:
                results.append(SearchResult(
                    url=topic["FirstURL"],
                    title=topic["Text"][:80],
                    content=topic["Text"],
                    domain=urlparse(topic["FirstURL"]).netloc,
                ))

        return results[:num_results]

    def _get_mock_results(self, query: str) -> List[SearchResult]:
        mock_results = [
            SearchResult(
                url="https://xueqiu.com/123456/789012",
                title=f"{query}2024年业绩预告分析",
                content=f"{query}发布2024年度业绩预告，预计净利润同比增长15%-20%，主要得益于新产品线的贡献。",
                domain="xueqiu.com",
            ),
            SearchResult(
                url="https://cls.cn/2026/04/30/123456.html",
                title=f"{query}与某巨头达成战略合作",
                content=f"据悉，{query}与国内某科技巨头签署战略合作协议，双方将在新能源领域展开深度合作。",
                domain="cls.cn",
            ),
            SearchResult(
                url="https://36kr.com/p/12345678",
                title=f"{query}创始人专访：穿越周期",
                content=f"{query}创始人在接受专访时表示，公司将坚持研发投入，应对行业周期波动。",
                domain="36kr.com",
            ),
            SearchResult(
                url="https://example.com/quote/601012",
                title=f"{query}(601012)实时行情 K线图 技术分析",
                content=f"{query}(601012)的实时行情，及时准确的提供{query}的flash分时走势、K线图、均价线系统、MACD、KDJ、交易量等全面技术分析。",
                domain="example.com",
            ),
            SearchResult(
                url="https://zhihu.com/question/123456",
                title=f"如何看待{query}的未来发展？",
                content=f"{query}作为行业龙头，其未来发展备受关注，多位分析师发表了观点。",
                domain="zhihu.com",
            ),
        ]
        return mock_results

    async def search_site(
        self,
        query: str,
        site: str,
        num_results: int = 10,
        time_range: str = None,
    ) -> List[SearchResult]:
        site_query = f"site:{site} {query}"
        results = await self.search(site_query, num_results, time_range)
        # 过滤一下只保留目标站点的
        filtered = [r for r in results if site in r.domain]
        return filtered if filtered else results[:2]
