#!/usr/bin/env python3
import asyncio
import sys
from datetime import datetime
from pathlib import Path

from api.search_service import SearchService


def save_search_results(query: str, results: list, use_targeted: bool = False):
    now = datetime.now()
    date_str = now.strftime("%Y%m%d")
    datetime_str = now.strftime("%Y%m%d_%H%M%S")

    dir_path = Path("search_results") / date_str
    dir_path.mkdir(parents=True, exist_ok=True)

    filename = f"{datetime_str}-搜索结果.md"
    filepath = dir_path / filename

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# 搜索结果\n\n")
        f.write(f"- 查询: {query}\n")
        f.write(f"- 时间: {now.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"- 模式: {'定向搜索' if use_targeted else '普通搜索'}\n")
        f.write(f"- 结果数: {len(results)}\n\n")
        f.write("---\n\n")

        for i, result in enumerate(results, 1):
            f.write(f"## {i}. [{result.score:.1f}] {result.title}\n\n")
            f.write(f"- 链接: {result.url}\n")
            f.write(f"- 域名: {result.domain}\n")
            f.write(f"- 优质站点: {'是' if result.is_quality else '否'}\n\n")
            f.write(f"### 摘要\n\n{result.content}\n\n")
            f.write("---\n\n")

    print(f"结果已保存到: {filepath}")
    return filepath


async def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <query> [--targeted] [--sites site1,site2]")
        return

    query = sys.argv[1]
    use_targeted = "--targeted" in sys.argv

    sites = None
    if "--sites" in sys.argv:
        idx = sys.argv.index("--sites")
        if idx + 1 < len(sys.argv):
            sites = sys.argv[idx + 1].split(",")

    service = SearchService()

    print(f"搜索: {query}")
    print("-" * 80)

    if use_targeted or sites:
        results = await service.targeted_search(query, sites=sites)
    else:
        results = await service.search(query)

    for i, result in enumerate(results, 1):
        print(f"{i}. [{result.score:.1f}] {result.title}")
        print(f"   {result.url}")
        print(f"   {result.content[:100]}...")
        print()

    if results:
        save_search_results(query, results, use_targeted or sites is not None)


if __name__ == "__main__":
    asyncio.run(main())
