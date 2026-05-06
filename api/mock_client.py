from typing import List
from models.search_result import SearchResult


class MockClient:
    def __init__(self):
        pass

    async def search(
        self,
        query: str,
        num_results: int = 20,
        time_range: str = None,
    ) -> List[SearchResult]:
        # 特殊查询返回空结果，用于测试失败原因
        if "不存在的概念" in query or "xyz123" in query:
            return []
        # 特殊查询返回全是垃圾的结果，用于测试ALL_FILTERED
        if "技术分析专用测试" in query:
            return [
                SearchResult(
                    url="https://example.com/quote/601012",
                    title=f"{query}(601012)实时行情 K线图 技术分析",
                    content=f"{query}(601012)的实时行情，及时准确的提供{query}的flash分时走势、K线图、均价线系统、MACD、KDJ、交易量等全面技术分析。",
                    domain="example.com",
                ),
                SearchResult(
                    url="https://example.com/kline/601012",
                    title=f"{query}每日K线图分析",
                    content=f"今日{query}K线图走势，MACD指标金叉，KDJ超买，交易量放大，建议关注。",
                    domain="example.com",
                ),
            ]

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
                url="https://example.com/kline/601012",
                title=f"{query}每日K线图分析",
                content=f"今日{query}K线图走势，MACD指标金叉，KDJ超买，交易量放大，建议关注。",
                domain="example.com",
            ),
            SearchResult(
                url="https://example.com/stock/601012",
                title=f"{query}千股千评：今日点评",
                content=f"{query}今日上涨3%，技术面看好，资金流向显示主力净流入，短期有望继续上行。",
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
        results = await self.search(query, num_results)
        filtered = [r for r in results if site in r.domain]
        return filtered if filtered else results[:1]
