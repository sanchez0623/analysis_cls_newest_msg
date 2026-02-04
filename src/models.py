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
    
    @property
    def has_specific_stocks(self) -> bool:
        """Check if the news item mentions specific stocks."""
        return bool(self.stocks)
    
    @property
    def is_industry_event(self) -> bool:
        """
        Check if the news is an industry-level event.
        
        Returns True if:
        - No specific stocks are mentioned, OR
        - The subjects/content suggest industry-wide impact
        """
        return not self.stocks or bool(self.subjects)
    
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
class StockRating:
    """Rating for a specific stock affected by the news."""
    
    stock_name: str
    is_positive: bool  # True for good, False for bad
    score: int  # 1-10 rating
    reason: str  # Brief explanation of the rating
    
    def __str__(self) -> str:
        """String representation of stock rating."""
        sentiment = "利好" if self.is_positive else "利空"
        return f"{self.stock_name}: {sentiment} {self.score}/10 - {self.reason}"


@dataclass
class IndustryRating:
    """Rating for an industry affected by the news."""
    
    industry_name: str
    is_positive: bool  # True for good, False for bad
    score: int  # 1-10 rating
    leader_stocks: List[str]  # Industry leader stocks (first principles analysis)
    reason: str  # Brief explanation based on first principles
    
    def __str__(self) -> str:
        """String representation of industry rating."""
        sentiment = "利好" if self.is_positive else "利空"
        leaders = ", ".join(self.leader_stocks) if self.leader_stocks else "暂无"
        return f"{self.industry_name}: {sentiment} {self.score}/10 | 龙头: {leaders}"


@dataclass
class AnalysisResult:
    """Analysis result for a news item."""
    
    news_id: str
    score: int  # 1-10 rating (overall)
    analysis: str
    is_positive: bool
    market_impact: str
    # Enhanced analysis fields
    stock_ratings: List[StockRating] = field(default_factory=list)
    industry_ratings: List[IndustryRating] = field(default_factory=list)
    analyzed_at: datetime = field(default_factory=datetime.now)
    
    def __str__(self) -> str:
        """String representation of analysis result."""
        sentiment = "利好" if self.is_positive else "利空"
        return f"评分: {self.score}/10 | {sentiment} | {self.market_impact}"
    
    @property
    def has_stock_ratings(self) -> bool:
        """Check if there are stock-specific ratings."""
        return bool(self.stock_ratings)
    
    @property
    def has_industry_ratings(self) -> bool:
        """Check if there are industry-specific ratings."""
        return bool(self.industry_ratings)
