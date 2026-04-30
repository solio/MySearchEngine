from typing import List, Tuple
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

    def score(self, result: SearchResult) -> Tuple[float, bool, str]:
        score = 50.0
        spam_reason = None
        is_spam = False

        domain = self.extract_domain(result.url)
        result.domain = domain

        if self.config.matches_bad_url_pattern(result.url):
            return 0.0, True, "匹配垃圾URL模式"

        spam_count = self.config.count_spam_keywords(result.title + " " + result.content)
        if spam_count >= 3:
            return 0.0, True, f"垃圾关键词过多({spam_count}个)"

        if self.config.is_quality_domain(domain):
            score += 40.0
            result.is_quality = True

        if self.config.matches_good_url_pattern(result.url):
            score += 20.0

        title_len = len(result.title)
        if 20 <= title_len <= 80:
            score += 10.0

        if spam_count == 0:
            score += 15.0
        elif spam_count == 1:
            score -= 10.0
        elif spam_count == 2:
            score -= 25.0

        domain_weight = self.config.get_domain_weight(domain)
        score *= domain_weight

        if score < 30:
            is_spam = True
            spam_reason = "综合评分过低"

        return min(score, 100.0), is_spam, spam_reason

    def filter_and_score(self, results: List[SearchResult]) -> List[SearchResult]:
        scored = []
        for result in results:
            score, is_spam, spam_reason = self.score(result)
            result.score = score
            result.is_spam = is_spam
            result.spam_reason = spam_reason
            if not is_spam:
                scored.append(result)

        scored.sort(key=lambda x: x.score, reverse=True)
        return scored
