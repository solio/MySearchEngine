#!/usr/bin/env python3
import asyncio
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict

from api.search_service import SearchService


def print_evaluation_stats(spam_stats: Dict):
    print("\n" + "=" * 80)
    print("评估统计")
    print("=" * 80)
    print(f"总结果数: {spam_stats['total']}")
    print(f"保留结果: {spam_stats['passed']}")
    print(f"过滤结果: {spam_stats['filtered']}")
    print(f"过滤率: {spam_stats['filtered']/max(spam_stats['total'],1)*100:.1f}%")

    if spam_stats['reasons']:
        print("\n过滤原因统计:")
        for reason, count in spam_stats['reasons'].items():
            print(f"  - {reason}: {count}条")

    if spam_stats['needs_param_update']:
        print("\n⚠️  模型参数建议:")
        print(f"   {spam_stats['update_suggestion']}")
    else:
        print("\n✅ 参数评估正常，无需更新")
    print("=" * 80)


def save_search_results(query: str, results: list, spam_stats: Dict, use_targeted: bool = False, debug: bool = False):
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

        f.write("## 评估统计\n\n")
        f.write(f"- 总结果数: {spam_stats['total']}\n")
        f.write(f"- 保留结果: {spam_stats['passed']}\n")
        f.write(f"- 过滤结果: {spam_stats['filtered']}\n")
        f.write(f"- 过滤率: {spam_stats['filtered']/max(spam_stats['total'],1)*100:.1f}%\n")

        if spam_stats['reasons']:
            f.write("\n### 过滤原因\n\n")
            for reason, count in spam_stats['reasons'].items():
                f.write(f"- {reason}: {count}条\n")

        if spam_stats['needs_param_update']:
            f.write("\n### ⚠️ 参数更新建议\n\n")
            f.write(f"{spam_stats['update_suggestion']}\n")

        f.write("\n---\n\n")

        for i, result in enumerate(results, 1):
            f.write(f"## {i}. [{result.score:.1f}] {result.title}\n\n")
            f.write(f"- 链接: {result.url}\n")
            f.write(f"- 域名: {result.domain}\n")
            f.write(f"- 优质站点: {'是' if result.is_quality else '否'}\n\n")
            f.write(f"### 摘要\n\n{result.content}\n\n")

            if debug and result.debug_info:
                f.write("### 评估详情\n\n")
                for step in result.debug_info.get("steps", []):
                    f.write(f"- {step['check']}: {step['result']}")
                    if "score_change" in step and step["score_change"]:
                        f.write(f" ({step['score_change']})")
                    f.write("\n")
                f.write(f"\n最终得分: {result.debug_info.get('final_score', 0):.1f}\n\n")

            f.write("---\n\n")

    print(f"结果已保存到: {filepath}")
    return filepath


async def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <query> [--targeted] [--sites site1,site2] [--mock] [--debug]")
        return

    query = sys.argv[1]
    use_targeted = "--targeted" in sys.argv
    use_mock = "--mock" in sys.argv
    debug = "--debug" in sys.argv

    sites = None
    if "--sites" in sys.argv:
        idx = sys.argv.index("--sites")
        if idx + 1 < len(sys.argv):
            sites = sys.argv[idx + 1].split(",")

    service = SearchService(use_mock=use_mock)

    print(f"搜索: {query}")
    print("-" * 80)

    if use_targeted or sites:
        results, spam_stats = await service.targeted_search(query, sites=sites, debug=debug)
    else:
        results, spam_stats = await service.search(query, debug=debug)

    for i, result in enumerate(results, 1):
        print(f"{i}. [{result.score:.1f}] {result.title}")
        print(f"   {result.url}")
        print(f"   {result.content[:100]}...")
        print()

    print_evaluation_stats(spam_stats)

    if results or spam_stats:
        save_search_results(query, results, spam_stats, use_targeted or sites is not None, debug=debug)


if __name__ == "__main__":
    asyncio.run(main())
