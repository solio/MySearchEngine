#!/usr/bin/env python3
import asyncio
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

from api.search_service import SearchService


def print_evaluation_stats(spam_stats: Dict):
    print("\n" + "=" * 80)
    print("评估统计")
    print("=" * 80)
    print(f"总结果数: {spam_stats['total']}")
    print(f"保留结果: {spam_stats['passed']}")
    print(f"过滤结果: {spam_stats['filtered']}")
    filter_rate = spam_stats['filtered'] / max(spam_stats['total'], 1)
    print(f"过滤率: {filter_rate*100:.1f}%")

    # 输出详细过滤原因
    if spam_stats.get('reasons'):
        print("\n过滤原因统计:")
        for reason, count in spam_stats['reasons'].items():
            print(f"  - {reason}: {count}条")

    # 输出问题统计
    if spam_stats.get('problems'):
        print("\n识别的问题:")
        for problem in spam_stats['problems']:
            print(f"  ❌ {problem}")

    # 输出问题样例
    if spam_stats.get('problem_samples'):
        print("\n问题样例:")
        for reason, samples in spam_stats['problem_samples'].items():
            print(f"\n  【{reason}】样例:")
            for i, sample in enumerate(samples, 1):
                print(f"    {i}. {sample['title']}")
                print(f"       {sample['url'][:60]}..." if len(sample['url']) > 60 else f"       {sample['url']}")

    # 输出详细统计
    print(f"\n详细统计:")
    if 'total_spam_keywords' in spam_stats:
        avg_keywords = spam_stats['total_spam_keywords'] / max(spam_stats['total'], 1)
        print(f"  - 垃圾关键词总数: {spam_stats['total_spam_keywords']} (平均{avg_keywords:.1f}个/条)")
    if 'bad_url_count' in spam_stats:
        print(f"  - 垃圾URL数量: {spam_stats['bad_url_count']}")
    if 'low_quality_count' in spam_stats:
        print(f"  - 低质量内容数量: {spam_stats['low_quality_count']}")

    if spam_stats.get('needs_param_update'):
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
        filter_rate = spam_stats['filtered'] / max(spam_stats['total'], 1)
        f.write(f"- 过滤率: {filter_rate*100:.1f}%\n")

        # 详细统计
        if spam_stats.get('total_spam_keywords') is not None:
            avg_keywords = spam_stats['total_spam_keywords'] / max(spam_stats['total'], 1)
            f.write(f"- 垃圾关键词总数: {spam_stats['total_spam_keywords']} (平均{avg_keywords:.1f}个/条)\n")
        if spam_stats.get('bad_url_count') is not None:
            f.write(f"- 垃圾URL数量: {spam_stats['bad_url_count']}\n")
        if spam_stats.get('low_quality_count') is not None:
            f.write(f"- 低质量内容数量: {spam_stats['low_quality_count']}\n")

        if spam_stats.get('reasons'):
            f.write("\n### 过滤原因\n\n")
            for reason, count in spam_stats['reasons'].items():
                f.write(f"- {reason}: {count}条\n")

        # Debug模式：输出识别的问题和样例
        if debug:
            if spam_stats.get('problems'):
                f.write("\n### 识别的问题\n\n")
                for problem in spam_stats['problems']:
                    f.write(f"- ❌ {problem}\n")

            if spam_stats.get('problem_samples'):
                f.write("\n### 问题样例\n\n")
                for reason, samples in spam_stats['problem_samples'].items():
                    f.write(f"\n#### {reason}\n\n")
                    for i, sample in enumerate(samples, 1):
                        f.write(f"{i}. {sample['title']}\n")
                        f.write(f"   URL: {sample['url']}\n")
                        f.write(f"   评分: {sample['score']:.1f}\n\n")

        if spam_stats.get('needs_param_update'):
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

    return filepath


def load_search_list(file_path: str) -> List[Tuple[str, str, bool]]:
    """
    读取搜索列表文件

    文件格式：
    - 个股：每行一个股票，格式为「股票代码|股票名称」
    - 行业：每行一个行业，格式为「行业|行业名称」

    Args:
        file_path: 文件路径

    Returns:
        (标识, 名称, 是否行业)列表，标识对于股票是代码，对于行业是"行业"
    """
    search_list = []
    path = Path(file_path)

    if not path.exists():
        print(f"错误：文件不存在 - {file_path}")
        sys.exit(1)

    lines = path.read_text(encoding="utf-8").split("\n")
    for line in lines:
        line = line.strip()
        if not line or "|" not in line:
            continue
        prefix, name = line.split("|", 1)
        prefix = prefix.strip()
        name = name.strip()
        is_industry = prefix == "行业"
        search_list.append((prefix, name, is_industry))

    return search_list


async def single_search(query: str, use_targeted: bool = False, sites: List[str] = None, use_mock: bool = False, debug: bool = False):
    """单个搜索"""
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
        filepath = save_search_results(query, results, spam_stats, use_targeted or sites is not None, debug=debug)
        print(f"结果已保存到: {filepath}")


async def batch_search(file_path: str, use_targeted: bool = False, use_mock: bool = False, debug: bool = False):
    """批量搜索"""
    # 加载搜索列表（股票+行业）
    search_list = load_search_list(file_path)
    if not search_list:
        print("错误：未读取到有效的搜索列表")
        sys.exit(1)

    # 统计股票和行业数量
    stock_count = sum(1 for _, _, is_industry in search_list if not is_industry)
    industry_count = sum(1 for _, _, is_industry in search_list if is_industry)
    print(f"已加载 {stock_count} 只股票，{industry_count} 个行业")
    print("-" * 60)

    # 创建搜索服务
    service = SearchService(use_mock=use_mock)

    # 逐个搜索
    success_count = 0
    fail_count = 0

    for prefix, name, is_industry in search_list:
        type_label = "行业" if is_industry else "股票"
        display_name = f"{name}" if is_industry else f"{name}({prefix})"
        print(f"[{success_count+fail_count+1}/{len(search_list)}] 正在搜索{type_label}：{display_name}")

        try:
            if use_targeted:
                results, spam_stats = await service.targeted_search(name, debug=debug)
            else:
                results, spam_stats = await service.search(name, debug=debug)

            if results:
                saved_path = save_search_results(name, results, spam_stats, use_targeted, debug=debug)
                print(f"  成功！保存到：{saved_path}")
                success_count += 1
            else:
                print(f"  未找到有效结果")
                fail_count += 1

        except Exception as e:
            print(f"  失败：{e}")
            fail_count += 1

    # 总结
    print("\n" + "=" * 60)
    print(f"批量搜索完成")
    print(f"  总数：{len(search_list)} (股票{stock_count} + 行业{industry_count})")
    print(f"  成功：{success_count}")
    print(f"  失败：{fail_count}")
    print("=" * 60)


async def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  单个搜索: python main.py <query> [--targeted] [--sites site1,site2] [--mock] [--debug]")
        print("  批量搜索: python main.py --file <search_list_file> [--targeted] [--mock] [--debug]")
        print("\n示例:")
        print("  python main.py 隆基绿能 --mock")
        print("  python main.py 光伏 --mock")
        print("  python main.py --file example_stocks.txt --mock --targeted")
        return

    # 检查是否是批量搜索模式
    if sys.argv[1] == "--file":
        if len(sys.argv) < 3:
            print("错误：--file 参数需要指定文件路径")
            print("Usage: python main.py --file <stock_list_file> [--targeted] [--mock] [--debug]")
            return

        file_path = sys.argv[2]
        use_targeted = "--targeted" in sys.argv
        use_mock = "--mock" in sys.argv
        debug = "--debug" in sys.argv

        await batch_search(file_path, use_targeted, use_mock, debug)
    else:
        # 单个搜索模式
        query = sys.argv[1]
        use_targeted = "--targeted" in sys.argv
        use_mock = "--mock" in sys.argv
        debug = "--debug" in sys.argv

        sites = None
        if "--sites" in sys.argv:
            idx = sys.argv.index("--sites")
            if idx + 1 < len(sys.argv):
                sites = sys.argv[idx + 1].split(",")

        await single_search(query, use_targeted, sites, use_mock, debug)


if __name__ == "__main__":
    asyncio.run(main())
