#!/usr/bin/env python3
"""
批量投研工具

读取股票列表文件，对每个股票执行搜索，保存结果。
"""
import asyncio
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

from api.search_service import SearchService


def load_stock_list(file_path: str) -> List[Tuple[str, str]]:
    """
    读取股票列表文件

    文件格式：每行一个股票，格式为「股票代码|股票名称」

    Args:
        file_path: 文件路径

    Returns:
        (股票代码, 股票名称)列表
    """
    stock_list = []
    path = Path(file_path)

    if not path.exists():
        print(f"错误：文件不存在 - {file_path}")
        sys.exit(1)

    lines = path.read_text(encoding="utf-8").split("\n")
    for line in lines:
        line = line.strip()
        if not line or "|" not in line:
            continue
        code, name = line.split("|", 1)
        stock_list.append((code.strip(), name.strip()))

    return stock_list


def save_search_result(query: str, results: list, spam_stats: dict, use_targeted: bool):
    """
    保存搜索结果到文件

    Args:
        query: 查询关键词
        results: 搜索结果列表
        spam_stats: 评估统计
        use_targeted: 是否为定向搜索
    """
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

        f.write(f"## 评估统计\n\n")
        f.write(f"- 总结果数: {spam_stats.get('total', 0)}\n")
        f.write(f"- 保留结果: {spam_stats.get('passed', 0)}\n")
        f.write(f"- 过滤结果: {spam_stats.get('filtered', 0)}\n")
        f.write(f"- 过滤率: {spam_stats.get('filtered', 0)/max(spam_stats.get('total', 1), 1)*100:.1f}%\n")

        if spam_stats.get("reasons"):
            f.write(f"\n### 过滤原因\n\n")
            for reason, count in spam_stats.get("reasons", {}).items():
                f.write(f"- {reason}: {count}条\n")

        f.write("\n---\n\n")

        for i, result in enumerate(results, 1):
            f.write(f"## {i}. [{result.score:.1f}] {result.title}\n\n")
            f.write(f"- 链接: {result.url}\n")
            f.write(f"- 域名: {result.domain}\n")
            f.write(f"- 优质站点: {'是' if result.is_quality else '否'}\n\n")
            f.write(f"### 摘要\n\n{result.content}\n\n")
            f.write("---\n\n")

    return filepath


def main():
    if len(sys.argv) < 2 or "--file" not in sys.argv:
        print("Usage: python batch.py --file <stock_list_file> [--targeted] [--debug] [--mock]")
        print("\n示例:")
        print("  python batch.py --file stocks.txt --mock")
        print("  python batch.py --file stocks.txt --targeted --debug")
        sys.exit(1)

    # 解析参数
    file_idx = sys.argv.index("--file")
    if file_idx + 1 >= len(sys.argv):
        print("错误：--file 参数需要指定文件路径")
        sys.exit(1)

    file_path = sys.argv[file_idx + 1]
    use_targeted = "--targeted" in sys.argv
    debug = "--debug" in sys.argv
    use_mock = "--mock" in sys.argv

    # 加载股票列表
    stock_list = load_stock_list(file_path)
    if not stock_list:
        print("错误：未读取到有效的股票列表")
        sys.exit(1)

    print(f"已加载 {len(stock_list)} 只股票")
    print("-" * 60)

    # 创建搜索服务
    service = SearchService(use_mock=use_mock)

    # 逐个搜索
    success_count = 0
    fail_count = 0

    for code, name in stock_list:
        print(f"[{success_count+fail_count+1}/{len(stock_list)}] 正在搜索：{name}({code})")

        try:
            if use_targeted:
                results, spam_stats = asyncio.run(service.targeted_search(name, debug=debug))
            else:
                results, spam_stats = asyncio.run(service.search(name, debug=debug))

            if results:
                saved_path = save_search_result(name, results, spam_stats, use_targeted)
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
    print(f"  总股票数：{len(stock_list)}")
    print(f"  成功：{success_count}")
    print(f"  失败：{fail_count}")
    print("=" * 60)


if __name__ == "__main__":
    main()
