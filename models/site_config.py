from dataclasses import dataclass
from typing import List, Optional
import yaml
import re


@dataclass
class SitePatterns:
    include: List[str]
    exclude: List[str]


@dataclass
class QualitySite:
    domain: str
    name: str
    weight: float
    type: str
    trust_level: str
    url_patterns: Optional[SitePatterns] = None


class SiteConfig:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.quality_sites: List[QualitySite] = []
        self.spam_keywords: List[str] = []
        self.good_url_patterns: List[str] = []
        self.bad_url_patterns: List[str] = []
        self._load_config()

    def _load_config(self):
        with open(self.config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        for site_data in data.get("quality_sites", []):
            patterns = None
            if "url_patterns" in site_data:
                patterns = SitePatterns(
                    include=site_data["url_patterns"].get("include", []),
                    exclude=site_data["url_patterns"].get("exclude", []),
                )
            site = QualitySite(
                domain=site_data["domain"],
                name=site_data["name"],
                weight=site_data["weight"],
                type=site_data["type"],
                trust_level=site_data["trust_level"],
                url_patterns=patterns,
            )
            self.quality_sites.append(site)

        self.spam_keywords = data.get("spam_keywords", [])
        self.good_url_patterns = data.get("good_url_patterns", [])
        self.bad_url_patterns = data.get("bad_url_patterns", [])

    def get_quality_site(self, domain: str) -> Optional[QualitySite]:
        for site in self.quality_sites:
            if site.domain in domain:
                return site
        return None

    def is_quality_domain(self, domain: str) -> bool:
        return self.get_quality_site(domain) is not None

    def get_domain_weight(self, domain: str) -> float:
        site = self.get_quality_site(domain)
        return site.weight if site else 1.0

    def matches_good_url_pattern(self, url: str) -> bool:
        for pattern in self.good_url_patterns:
            if re.search(pattern, url):
                return True
        return False

    def matches_bad_url_pattern(self, url: str) -> bool:
        for pattern in self.bad_url_patterns:
            if re.search(pattern, url):
                return True
        site = self.get_quality_site(url)
        if site and site.url_patterns:
            for pattern in site.url_patterns.exclude:
                if re.search(pattern, url):
                    return True
        return False

    def count_spam_keywords(self, text: str) -> int:
        count = 0
        for keyword in self.spam_keywords:
            if keyword in text:
                count += 1
        return count
