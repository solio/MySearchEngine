#!/usr/bin/env python3
"""
MySearchEngine Skill

基于AI的搜索MCP，专为投研场景优化的搜索引擎。
"""
import asyncio
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# 导入主程序中的搜索服务
from api.search_service import SearchService


def parse_search_result_file(file_path: Path) -> Optional[Dict[str, Any]]:
    """
    解析搜索结果文件

    Args:
        file_path: 搜索结果文件路径

    Returns:
        解析后的字典数据，解析失败返回None
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        lines = content.split("\n")

        result: Dict[str, Any] = {
            "id": file_path.stem,
            "file_path": str(file_path.absolute()),
            "query": "",
            "search_time": "",
            "mode": "",
            "total_results": 0,
            "passed_results": 0,
            "filtered_results": 0,
            "filter_rate": "",
            "filter_reasons": {},
            "results": [],
        }

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # 解析查询信息
            if line.startswith("- 查询:"):
                result["query"] = line[len("- 查询:") :].strip()
            elif line.startswith("- 时间:"):
                try:
                    time_str = line[len("- 时间:") :].strip()
                    dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
                    result["search_time"] = dt.isoformat()
                except Exception:
                    pass
            elif line.startswith("- 模式:"):
                result["mode"] = line[len("- 模式:") :].strip()
            elif line.startswith("- 结果数:"):
                try:
                    result["result_count"] = int(line[len("- 结果数:") :].strip())
                except Exception:
                    pass

            # 解析评估统计
            elif line.startswith("- 总结果数:"):
                try:
                    result["total_results"] = int(line[len("- 总结果数:") :].strip())
                except Exception:
                    pass
            elif line.startswith("- 保留结果:"):
                try:
                    result["passed_results"] = int(line[len("- 保留结果:") :].strip())
                except Exception:
                    pass
            elif line.startswith("- 过滤结果:"):
                try:
                    result["filtered_results"] = int(line[len("- 过滤结果:") :].strip())
                except Exception:
                    pass
            elif line.startswith("- 过滤率:"):
                result["filter_rate"] = line[len("- 过滤率:") :].strip()

            # 解析过滤原因
            elif line.startswith("- ") and "条" in line and ":" in line:
                try:
                    part1, part2 = line[len("- ") :].split(":", 1)
                    reason = part1.strip()
                    count = int(part2.strip().rstrip("条"))
                    result["filter_reasons"][reason] = count
                except Exception:
                    pass

            # 解析搜索结果条目
            elif re.match(r"^## \d+\.\s+", line):
                # 开始解析一个结果条目
                i = _parse_result_item(result, lines, i)

            i += 1

        return result

    except Exception:
        return None


def _parse_result_item(result: Dict[str, Any], lines: List[str], start_idx: int) -> int:
    """
    解析单个搜索结果条目

    Args:
        result: 结果字典，用于添加解析后的数据
        lines: 所有行
        start_idx: 开始索引

    Returns:
        结束索引
    """
    item: Dict[str, Any] = {
        "title": "",
        "url": "",
        "domain": "",
        "content": "",
        "is_quality_site": False,
        "score": 0.0,
    }

    # 提取标题和评分
    title_line = lines[start_idx].strip()
    score_match = re.search(r"\[(\d+\.?\d*)\]", title_line)
    if score_match:
        try:
            item["score"] = float(score_match.group(1))
        except Exception:
            pass
        title = re.sub(r"\[\d+\.?\d*\]\s*", "", title_line[3:]).strip()
        item["title"] = title

    i = start_idx + 1
    content_started = False
    content_lines = []

    while i < len(lines):
        line = lines[i].strip()

        if line.startswith("- 链接:"):
            item["url"] = line[len("- 链接:") :].strip()
        elif line.startswith("- 域名:"):
            item["domain"] = line[len("- 域名:") :].strip()
        elif line.startswith("- 优质站点:"):
            val = line[len("- 优质站点:") :].strip()
            item["is_quality_site"] = val in ["是", "true", "True"]
        elif line.startswith("### 摘要"):
            content_started = True
        elif line.startswith("### 评估详情"):
            content_started = False
        elif line.startswith("---"):
            # 条目结束
            break
        elif content_started and line and not line.startswith("#"):
            content_lines.append(line)

        i += 1

    item["content"] = "\n".join(content_lines).strip()
    result["results"].append(item)
    return i


def query_history(year: int, month: Optional[int] = None, day: Optional[int] = None, query: Optional[str] = None) -> Dict[str, Any]:
    """
    查询历史搜索结果

    Args:
        year: 年份（必填）
        month: 月份（可选，1-12）
        day: 日期（可选，1-31，需要month存在）
        query: 关键词（可选，个股名称或行业名称，模糊匹配）

    Returns:
        查询结果字典
    """
    base_path = Path("search_results")
    result: Dict[str, Any] = {
        "year": year,
        "month": month,
        "day": day,
        "query_filter": query,
        "count": 0,
        "records": [],
    }

    # 根据参数确定需要遍历的目录
    if month is not None and day is not None:
        # 精确到日：只遍历该日目录
        month_str = f"{month:02d}"
        day_str = f"{day:02d}"
        date_dir = base_path / f"{year}{month_str}{day_str}"
        _scan_date_directory(date_dir, result, query)
    elif month is not None:
        # 精确到月：遍历该月所有日目录
        for d in range(1, 32):
            month_str = f"{month:02d}"
            day_str = f"{d:02d}"
            date_dir = base_path / f"{year}{month_str}{day_str}"
            _scan_date_directory(date_dir, result, query)
    else:
        # 只提供年：遍历该年所有月日目录
        for m in range(1, 13):
            for d in range(1, 32):
                month_str = f"{m:02d}"
                day_str = f"{d:02d}"
                date_dir = base_path / f"{year}{month_str}{day_str}"
                _scan_date_directory(date_dir, result, query)

    result["count"] = len(result["records"])
    return result


def _scan_date_directory(date_dir: Path, result: Dict[str, Any], query_filter: Optional[str] = None) -> None:
    """
    扫描指定日期目录并添加结果到result中

    Args:
        date_dir: 日期目录路径
        result: 结果字典，会修改其中的records字段
        query_filter: 关键词过滤（可选）
    """
    if not date_dir.exists():
        return

    # 查找该目录下的搜索结果文件
    for file_path in sorted(date_dir.glob("*搜索结果.md")):
        record = parse_search_result_file(file_path)
        if record:
            # 如果有关键词过滤，只添加匹配的记录
            if query_filter:
                if query_filter.lower() in record.get("query", "").lower():
                    result["records"].append(record)
            else:
                result["records"].append(record)


def search(
    query: str,
    targeted: bool = False,
    debug: bool = False,
    use_mock: bool = False,
) -> Dict[str, Any]:
    """
    实时搜索

    Args:
        query: 搜索关键词
        targeted: 是否定向搜索（仅优质站点）
        debug: 是否返回详细评估信息
        use_mock: 是否使用mock模式

    Returns:
        搜索结果字典
    """
    service = SearchService(use_mock=use_mock)

    if targeted:
        results, spam_stats = asyncio.run(service.targeted_search(query, debug=debug))
    else:
        results, spam_stats = asyncio.run(service.search(query, debug=debug))

    # 构建返回结果
    result: Dict[str, Any] = {
        "query": query,
        "search_time": datetime.now().isoformat(),
        "mode": "定向搜索" if targeted else "普通搜索",
        "result_count": len(results),
        "total_results": spam_stats.get("total", 0),
        "passed_results": spam_stats.get("passed", 0),
        "filtered_results": spam_stats.get("filtered", 0),
        "filter_rate": f"{spam_stats.get('filtered', 0)/max(spam_stats.get('total', 1), 1)*100:.1f}%",
        "filter_reasons": spam_stats.get("reasons", {}),
        "param_update_suggestion": spam_stats.get("update_suggestion") if spam_stats.get("needs_param_update") else None,
        "results": [],
    }

    # 转换搜索结果
    for r in results:
        item: Dict[str, Any] = {
            "title": r.title,
            "url": r.url,
            "domain": r.domain,
            "content": r.content,
            "is_quality_site": r.is_quality,
            "score": r.score,
        }
        if debug and hasattr(r, "debug_info") and r.debug_info:
            item["debug_info"] = r.debug_info
        result["results"].append(item)

    return result


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python skill.py search <query> [--targeted] [--debug] [--mock]")
        print("  python skill.py history <year> [month] [day] [--query keyword]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "search":
        if len(sys.argv) < 3:
            print("Usage: python skill.py search <query> [--targeted] [--debug] [--mock]")
            sys.exit(1)

        query = sys.argv[2]
        targeted = "--targeted" in sys.argv
        debug = "--debug" in sys.argv
        use_mock = "--mock" in sys.argv

        result = search(query, targeted, debug, use_mock)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif command == "history":
        if len(sys.argv) < 3:
            print("Usage: python skill.py history <year> [month] [day] [--query keyword]")
            sys.exit(1)

        try:
            # 解析位置参数
            args = sys.argv[2:]
            year = None
            month = None
            day = None
            query = None

            # 提取--query参数
            if "--query" in args:
                query_idx = args.index("--query")
                if query_idx + 1 < len(args):
                    query = args[query_idx + 1]
                # 移除--query及其后面的参数，只处理前面的日期参数
                args = args[:query_idx]

            # 解析日期参数
            if len(args) >= 1:
                year = int(args[0])
            if len(args) >= 2:
                month = int(args[1])
            if len(args) >= 3:
                day = int(args[2])

            if year is None:
                print("Error: year is required")
                sys.exit(1)

        except Exception:
            print("Error: year, month and day must be integers")
            sys.exit(1)

        result = query_history(year, month, day, query)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        print(f"Unknown command: {command}")
        print("Available commands: search, history")
        sys.exit(1)
