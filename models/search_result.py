from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict


@dataclass
class SearchResult:
    url: str
    title: str
    content: str
    domain: str
    score: float = 0.0
    is_quality: bool = False
    is_spam: bool = False
    spam_reason: Optional[str] = None
    extracted_text: Optional[str] = None
    search_time: datetime = field(default_factory=datetime.now)
    debug_info: Dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "url": self.url,
            "title": self.title,
            "content": self.content,
            "domain": self.domain,
            "score": self.score,
            "is_quality": self.is_quality,
            "is_spam": self.is_spam,
            "spam_reason": self.spam_reason,
            "extracted_text": self.extracted_text,
            "search_time": self.search_time.isoformat(),
            "debug_info": self.debug_info,
        }
