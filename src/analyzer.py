"""
News Analyzer using GitHub Copilot SDK for market sentiment analysis.

This module analyzes news items and provides:
- Market sentiment score (1-10)
- Positive/negative classification
- Market impact assessment
"""

import logging
import re
from typing import Optional

from .config import config
from .models import NewsItem, AnalysisResult


logger = logging.getLogger(__name__)


class CopilotAnalyzer:
    """
    Analyzer using GitHub Copilot SDK for AI-powered news analysis.
    
    This analyzer uses the GitHub Copilot SDK to analyze financial news
    and provide market sentiment ratings.
    """
    
    def __init__(self, github_token: Optional[str] = None):
        """
        Initialize the Copilot analyzer.
        
        Args:
            github_token: GitHub token with Copilot access
        """
        self._token = github_token or config.github_token
        self._session = None
        self._initialize_sdk()
    
    def _initialize_sdk(self) -> None:
        """Initialize the Copilot SDK session."""
        if not self._token:
            logger.warning("No GitHub token provided. Analyzer will use fallback mode.")
            return
        
        try:
            # Try to import and initialize the Copilot SDK
            from github_copilot_sdk import CopilotAgentSession
            self._session = CopilotAgentSession()
            logger.info("GitHub Copilot SDK initialized successfully")
        except ImportError:
            logger.warning(
                "github-copilot-sdk not installed. "
                "Install it with: pip install github-copilot-sdk"
            )
        except Exception as e:
            logger.warning(f"Failed to initialize Copilot SDK: {e}")
    
    def _build_analysis_prompt(self, news: NewsItem) -> str:
        """
        Build the analysis prompt for the AI.
        
        Args:
            news: The news item to analyze
            
        Returns:
            The formatted prompt string
        """
        stocks_str = ", ".join(news.stocks) if news.stocks else "无"
        subjects_str = ", ".join(news.subjects) if news.subjects else "无"
        
        prompt = f"""请分析以下财经新闻的市场影响，并给出1-10分的市场热度评分（10分为最高，代表极具市场影响力）。

新闻内容：
{news.content}

相关股票：{stocks_str}
相关主题：{subjects_str}
发布时间：{news.display_time}

请按以下格式回复：
评分：[1-10的整数]
影响：[利好/利空/中性]
分析：[简短分析，不超过100字]
市场影响：[对市场的具体影响描述]

注意：
- 只有重大政策变化、行业突破性进展、重要经济数据等才能给9-10分
- 普通行业新闻给4-6分
- 无实质性影响的新闻给1-3分
"""
        return prompt
    
    def analyze(self, news: NewsItem) -> Optional[AnalysisResult]:
        """
        Analyze a news item using Copilot.
        
        Args:
            news: The news item to analyze
            
        Returns:
            AnalysisResult or None if analysis fails
        """
        if self._session:
            return self._analyze_with_copilot(news)
        else:
            return self._analyze_fallback(news)
    
    def _analyze_with_copilot(self, news: NewsItem) -> Optional[AnalysisResult]:
        """
        Analyze using the Copilot SDK.
        
        Args:
            news: The news item to analyze
            
        Returns:
            AnalysisResult or None if analysis fails
        """
        try:
            prompt = self._build_analysis_prompt(news)
            response = self._session.ask(prompt)
            
            # Parse the response
            return self._parse_analysis_response(news.id, response.text)
            
        except Exception as e:
            logger.error(f"Copilot analysis failed: {e}")
            return self._analyze_fallback(news)
    
    def _parse_analysis_response(self, news_id: str, response_text: str) -> Optional[AnalysisResult]:
        """
        Parse the AI response into an AnalysisResult.
        
        Args:
            news_id: The ID of the analyzed news
            response_text: The raw response from the AI
            
        Returns:
            AnalysisResult or None if parsing fails
        """
        try:
            # Extract score
            score_match = re.search(r"评分[：:]\s*(\d+)", response_text)
            score = int(score_match.group(1)) if score_match else 5
            score = max(1, min(10, score))  # Clamp to 1-10
            
            # Extract impact direction
            is_positive = "利好" in response_text
            
            # Extract market impact
            impact_match = re.search(r"市场影响[：:]\s*(.+?)(?:\n|$)", response_text)
            market_impact = impact_match.group(1).strip() if impact_match else "暂无详细分析"
            
            # Extract analysis
            analysis_match = re.search(r"分析[：:]\s*(.+?)(?:\n|$)", response_text)
            analysis = analysis_match.group(1).strip() if analysis_match else response_text[:200]
            
            return AnalysisResult(
                news_id=news_id,
                score=score,
                analysis=analysis,
                is_positive=is_positive,
                market_impact=market_impact,
            )
            
        except Exception as e:
            logger.error(f"Failed to parse analysis response: {e}")
            return None
    
    def _analyze_fallback(self, news: NewsItem) -> AnalysisResult:
        """
        Fallback analysis using keyword-based heuristics.
        
        This is used when Copilot SDK is not available.
        
        Args:
            news: The news item to analyze
            
        Returns:
            AnalysisResult based on keyword analysis
        """
        content = news.content.lower()
        
        # Positive keywords
        positive_keywords = [
            "增长", "上涨", "突破", "利好", "支持", "加速", "扩大",
            "创新", "盈利", "超预期", "回升", "反弹", "新高",
        ]
        
        # Negative keywords
        negative_keywords = [
            "下跌", "下降", "亏损", "利空", "风险", "警告", "暴跌",
            "收缩", "萎缩", "不及预期", "暂停", "终止", "处罚",
        ]
        
        # High impact keywords
        high_impact_keywords = [
            "央行", "政策", "降息", "加息", "财政", "重大", "突发",
            "并购", "重组", "退市", "上市", "国务院", "发改委",
        ]
        
        # Calculate scores
        positive_score = sum(1 for kw in positive_keywords if kw in content)
        negative_score = sum(1 for kw in negative_keywords if kw in content)
        impact_score = sum(2 for kw in high_impact_keywords if kw in content)
        
        # Determine sentiment
        is_positive = positive_score > negative_score
        
        # Calculate final score (1-10)
        base_score = 5
        sentiment_modifier = positive_score - negative_score
        score = base_score + sentiment_modifier + impact_score
        score = max(1, min(10, score))
        
        # Generate analysis
        if is_positive:
            sentiment = "利好"
            market_impact = "可能对相关板块形成正面刺激"
        else:
            sentiment = "利空" if negative_score > 0 else "中性"
            market_impact = "可能对相关板块形成负面影响" if negative_score > 0 else "影响有限"
        
        analysis = f"基于关键词分析，该新闻{sentiment}信号明显" if (positive_score + negative_score) > 0 else "该新闻影响较为中性"
        
        return AnalysisResult(
            news_id=news.id,
            score=score,
            analysis=analysis,
            is_positive=is_positive,
            market_impact=market_impact,
        )


class NewsAnalyzer:
    """
    Main analyzer class that provides a unified interface.
    
    Uses CopilotAnalyzer internally but can be extended to support
    multiple analysis backends.
    """
    
    def __init__(self, github_token: Optional[str] = None):
        """
        Initialize the news analyzer.
        
        Args:
            github_token: GitHub token for Copilot access
        """
        self._copilot = CopilotAnalyzer(github_token)
    
    def analyze(self, news: NewsItem) -> Optional[AnalysisResult]:
        """
        Analyze a news item.
        
        Args:
            news: The news item to analyze
            
        Returns:
            AnalysisResult or None if analysis fails
        """
        logger.info(f"Analyzing news: {news.id}")
        result = self._copilot.analyze(news)
        
        if result:
            logger.info(f"Analysis complete: {result}")
        
        return result
