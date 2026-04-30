from typing import List, Tuple, Dict
from urllib.parse import urlparse
import re

from models.search_result import SearchResult
from models.site_config import SiteConfig


class RuleEngine:
    def __init__(self, site_config: SiteConfig):
        self.config = site_config

    def extract_domain(self, url: str) -> str:
        parsed = urlparse(url)
        return parsed.netloc

    def score(self, result: SearchResult, debug: bool = False) -> Tuple[float, bool, str, Dict]:
        score = 50.0
        spam_reason = None
        is_spam = False
        debug_info = {
            "steps": [],
            "initial_score": 50.0,
            "final_score": 0.0,
        }

        domain = self.extract_domain(result.url)
        result.domain = domain

        # 检查垃圾URL模式
        bad_url = self.config.matches_bad_url_pattern(result.url)
        if bad_url:
            debug_info["steps"].append({
                "check": "垃圾URL模式",
                "result": "匹配",
                "action": "直接过滤",
                "score_change": 0,
            })
            debug_info["final_score"] = 0.0
            result.debug_info = debug_info
            return 0.0, True, "匹配垃圾URL模式", debug_info
        debug_info["steps"].append({
            "check": "垃圾URL模式",
            "result": "通过",
            "score_change": 0,
        })

        # 检查垃圾关键词
        full_text = result.title + " " + result.content
        spam_count = self.config.count_spam_keywords(full_text)
        debug_info["spam_keyword_count"] = spam_count

        if spam_count >= 3:
            debug_info["steps"].append({
                "check": "垃圾关键词",
                "result": f"发现{spam_count}个",
                "action": "直接过滤",
                "score_change": 0,
            })
            debug_info["final_score"] = 0.0
            result.debug_info = debug_info
            return 0.0, True, f"垃圾关键词过多({spam_count}个)", debug_info

        debug_info["steps"].append({
            "check": "垃圾关键词",
            "result": f"发现{spam_count}个",
        })

        # 优质域名加分
        is_quality_domain = self.config.is_quality_domain(domain)
        domain_weight = self.config.get_domain_weight(domain)
        if is_quality_domain:
            score += 40.0
            result.is_quality = True
            debug_info["steps"].append({
                "check": "优质域名",
                "result": f"是({domain})",
                "score_change": "+40",
                "new_score": score,
            })
        else:
            debug_info["steps"].append({
                "check": "优质域名",
                "result": f"否({domain})",
                "score_change": 0,
            })
        debug_info["domain_weight"] = domain_weight

        # 优质URL模式加分
        good_url = self.config.matches_good_url_pattern(result.url)
        if good_url:
            score += 20.0
            debug_info["steps"].append({
                "check": "优质URL模式",
                "result": "匹配",
                "score_change": "+20",
                "new_score": score,
            })
        else:
            debug_info["steps"].append({
                "check": "优质URL模式",
                "result": "不匹配",
                "score_change": 0,
            })

        # 标题长度加分
        title_len = len(result.title)
        if 20 <= title_len <= 80:
            score += 10.0
            debug_info["steps"].append({
                "check": "标题长度",
                "result": f"{title_len}字(符合)",
                "score_change": "+10",
                "new_score": score,
            })
        else:
            debug_info["steps"].append({
                "check": "标题长度",
                "result": f"{title_len}字(偏短/偏长)",
                "score_change": 0,
            })
        debug_info["title_length"] = title_len

        # 垃圾关键词加减分
        if spam_count == 0:
            score += 15.0
            debug_info["steps"].append({
                "check": "无垃圾关键词奖励",
                "result": "是",
                "score_change": "+15",
                "new_score": score,
            })
        elif spam_count == 1:
            score -= 10.0
            debug_info["steps"].append({
                "check": "垃圾关键词惩罚",
                "result": "1个",
                "score_change": "-10",
                "new_score": score,
            })
        elif spam_count == 2:
            score -= 25.0
            debug_info["steps"].append({
                "check": "垃圾关键词惩罚",
                "result": "2个",
                "score_change": "-25",
                "new_score": score,
            })

        # 应用域名权重
        before_weight = score
        score *= domain_weight
        if domain_weight != 1.0:
            debug_info["steps"].append({
                "check": "域名权重",
                "result": f"x{domain_weight}",
                "score_change": f"{before_weight:.1f} -> {score:.1f}",
            })

        # 最终检查
        final_score = min(score, 100.0)
        debug_info["final_score"] = final_score

        if final_score < 30:
            is_spam = True
            spam_reason = "综合评分过低"
            debug_info["steps"].append({
                "check": "最终评分检查",
                "result": f"{final_score:.1f} < 30",
                "action": "过滤",
            })
        else:
            debug_info["steps"].append({
                "check": "最终评分检查",
                "result": f"{final_score:.1f}分",
                "action": "保留",
            })

        result.debug_info = debug_info
        return final_score, is_spam, spam_reason, debug_info

    def filter_and_score(self, results: List[SearchResult], debug: bool = False) -> Tuple[List[SearchResult], Dict]:
        scored = []
        spam_stats = {
            "total": len(results),
            "passed": 0,
            "filtered": 0,
            "reasons": {},
            "needs_param_update": False,
        }

        for result in results:
            score, is_spam, spam_reason, debug_info = self.score(result, debug)
            result.score = score
            result.is_spam = is_spam
            result.spam_reason = spam_reason

            if is_spam:
                spam_stats["filtered"] += 1
                if spam_reason:
                    spam_stats["reasons"][spam_reason] = spam_stats["reasons"].get(spam_reason, 0) + 1
            else:
                spam_stats["passed"] += 1
                scored.append(result)

        # 检查是否需要更新参数
        if spam_stats["filtered"] > spam_stats["total"] * 0.5:
            spam_stats["needs_param_update"] = True
            spam_stats["update_suggestion"] = "过滤比例超过50%，建议检查垃圾关键词或URL模式是否过严"
        elif spam_stats["filtered"] == 0 and len(results) >= 3:
            spam_stats["needs_param_update"] = True
            spam_stats["update_suggestion"] = "未过滤任何结果，建议检查垃圾关键词是否过松"

        scored.sort(key=lambda x: x.score, reverse=True)
        return scored, spam_stats
