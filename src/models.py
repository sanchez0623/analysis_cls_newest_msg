"""
Data models for the CLS News Scraper and Analyzer.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class NewsItem:
    """Represents a single news item from CLS."""
    
    id: str
    title: str
    content: str
    ctime: int  # Unix timestamp
    subjects: List[str] = field(default_factory=list)
    stocks: List[str] = field(default_factory=list)
    
    @property
    def publish_time(self) -> datetime:
        """Convert Unix timestamp to datetime."""
        return datetime.fromtimestamp(self.ctime)
    
    @property
    def display_time(self) -> str:
        """Format time for display."""
        return self.publish_time.strftime("%Y-%m-%d %H:%M:%S")
    
    @classmethod
    def from_api_response(cls, data: dict) -> "NewsItem":
        """Create NewsItem from API response data."""
        # Extract stock codes from the response
        stocks = []
        if "stocks" in data and data["stocks"]:
            for stock in data["stocks"]:
                if isinstance(stock, dict) and "name" in stock:
                    stocks.append(stock["name"])
                elif isinstance(stock, str):
                    stocks.append(stock)
        
        # Extract subjects/tags
        subjects = []
        if "subjects" in data and data["subjects"]:
            for subject in data["subjects"]:
                if isinstance(subject, dict) and "name" in subject:
                    subjects.append(subject["name"])
                elif isinstance(subject, str):
                    subjects.append(subject)
        
        return cls(
            id=str(data.get("id", "")),
            title=data.get("title", ""),
            content=data.get("content", data.get("digest", "")),
            ctime=data.get("ctime", 0),
            subjects=subjects,
            stocks=stocks,
        )
    
    def __str__(self) -> str:
        """String representation of the news item."""
        return f"[{self.display_time}] {self.title or self.content[:50]}"


@dataclass
class AnalysisResult:
    """Analysis result for a news item."""
    
    news_id: str
    score: int  # 1-10 rating
    analysis: str
    is_positive: bool
    market_impact: str
    analyzed_at: datetime = field(default_factory=datetime.now)
    
    def __str__(self) -> str:
        """String representation of analysis result."""
        sentiment = "利好" if self.is_positive else "利空"
        return f"评分: {self.score}/10 | {sentiment} | {self.market_impact}"
