"""
News Analyzer using AI providers for market sentiment analysis.

This module analyzes news items and provides:
- Market sentiment score (1-10)
- Positive/negative classification
- Market impact assessment
- Stock-specific ratings (if stocks are mentioned)
- Industry analysis with first-principles approach (for industry events)
"""

import logging
import re
from typing import Optional, List

from .config import config
from .models import NewsItem, AnalysisResult, StockRating, IndustryRating
from .ai_providers import AIProvider, create_ai_provider


logger = logging.getLogger(__name__)


class EnhancedAnalyzer:
    """
    Analyzer using AI providers for enhanced news analysis.
    
    This analyzer uses configurable AI providers to analyze financial news
    and provides:
    - Stock-specific impact ratings (good/bad + 1-10 score)
    - Industry analysis with first-principles approach to identify leaders
    """
    
    def __init__(self, ai_provider: Optional[AIProvider] = None):
        """
        Initialize the enhanced analyzer.
        
        Args:
            ai_provider: AI provider instance (uses config default if not provided)
        """
        self._provider = ai_provider or self._create_default_provider()
    
    def _create_default_provider(self) -> AIProvider:
        """Create the default AI provider from configuration."""
        return create_ai_provider(
            provider_name=config.ai_provider,
            github_token=config.github_token,
            qiniu_access_key=config.qiniu_access_key,
            qiniu_secret_key=config.qiniu_secret_key,
            qiniu_api_endpoint=config.qiniu_api_endpoint,
        )
    
    def _build_analysis_prompt(self, news: NewsItem) -> str:
        """
        Build the enhanced analysis prompt for the AI.
        
        Args:
            news: The news item to analyze
            
        Returns:
            The formatted prompt string
        """
        stocks_str = ", ".join(news.stocks) if news.stocks else "无"
        subjects_str = ", ".join(news.subjects) if news.subjects else "无"
        
        # Determine analysis type based on content
        if news.has_specific_stocks:
            stock_analysis_section = f"""
## 个股影响分析
由于新闻涉及具体个股 ({stocks_str})，请针对每只股票分析：
- 股票名称
- 影响方向：利好 或 利空
- 评分：1-10分（10分为极大影响）
- 原因：简短说明（不超过50字）

格式：
个股评级：
- [股票名称]: [利好/利空] [分数]/10 | [原因]
"""
        else:
            stock_analysis_section = ""
        
        if news.is_industry_event or subjects_str != "无":
            industry_analysis_section = f"""
## 行业影响分析（第一性原理）
请运用马斯克的"第一性原理"思维，分析该事件对相关行业的本质影响：
1. 识别该事件涉及的核心行业
2. 从行业基本面出发，分析事件的本质影响
3. 找出该行业的龙头企业（最受益或最受影响的领头羊）
4. 给出行业评级

格式：
行业评级：
- 行业名称: [行业名]
- 影响方向: [利好/利空]
- 评分: [分数]/10
- 龙头股票: [股票1, 股票2, ...]
- 第一性原理分析: [从本质出发的分析，不超过100字]
"""
        else:
            industry_analysis_section = ""
        
        prompt = f"""请分析以下财经新闻的市场影响，并给出详细评估。

## 新闻内容
{news.content}

## 相关信息
- 相关股票：{stocks_str}
- 相关主题：{subjects_str}
- 发布时间：{news.display_time}

## 整体评估
请给出：
- 评分：1-10分的市场热度评分（10分为最高）
- 影响：利好/利空/中性
- 分析：简短分析（不超过100字）
- 市场影响：对市场的具体影响描述
{stock_analysis_section}{industry_analysis_section}

## 评分标准
- 9-10分：重大政策变化、行业突破性进展、重要经济数据
- 7-8分：较大影响的行业新闻、重要企业事件
- 5-6分：普通行业新闻、一般公司公告
- 3-4分：较小影响的新闻
- 1-2分：无实质性市场影响

请严格按照上述格式回复。
"""
        return prompt
    
    def analyze(self, news: NewsItem) -> Optional[AnalysisResult]:
        """
        Analyze a news item using the AI provider.
        
        Args:
            news: The news item to analyze
            
        Returns:
            AnalysisResult or None if analysis fails
        """
        if self._provider.is_available():
            return self._analyze_with_ai(news)
        else:
            return self._analyze_fallback(news)
    
    def _analyze_with_ai(self, news: NewsItem) -> Optional[AnalysisResult]:
        """
        Analyze using the AI provider.
        
        Args:
            news: The news item to analyze
            
        Returns:
            AnalysisResult or None if analysis fails
        """
        try:
            prompt = self._build_analysis_prompt(news)
            response = self._provider.analyze(prompt)
            
            if response:
                return self._parse_analysis_response(news, response)
            else:
                return self._analyze_fallback(news)
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return self._analyze_fallback(news)
    
    def _parse_analysis_response(
        self, news: NewsItem, response_text: str
    ) -> Optional[AnalysisResult]:
        """
        Parse the AI response into an AnalysisResult.
        
        Args:
            news: The original news item
            response_text: The raw response from the AI
            
        Returns:
            AnalysisResult or None if parsing fails
        """
        try:
            # Extract overall score
            score_match = re.search(r"评分[：:]\s*(\d+)", response_text)
            score = int(score_match.group(1)) if score_match else 5
            score = max(1, min(10, score))
            
            # Extract impact direction
            is_positive = "利好" in response_text and "利空" not in response_text[:100]
            
            # Extract market impact
            impact_match = re.search(
                r"市场影响[：:]\s*(.+?)(?:\n|$|##)", response_text, re.DOTALL
            )
            market_impact = (
                impact_match.group(1).strip()[:200] if impact_match else "暂无详细分析"
            )
            
            # Extract analysis
            analysis_match = re.search(
                r"分析[：:]\s*(.+?)(?:\n|$|##)", response_text, re.DOTALL
            )
            analysis = (
                analysis_match.group(1).strip()[:200] if analysis_match else response_text[:200]
            )
            
            # Parse stock ratings
            stock_ratings = self._parse_stock_ratings(response_text)
            
            # Parse industry ratings
            industry_ratings = self._parse_industry_ratings(response_text)
            
            return AnalysisResult(
                news_id=news.id,
                score=score,
                analysis=analysis,
                is_positive=is_positive,
                market_impact=market_impact,
                stock_ratings=stock_ratings,
                industry_ratings=industry_ratings,
            )
            
        except Exception as e:
            logger.error(f"Failed to parse analysis response: {e}")
            return None
    
    def _parse_stock_ratings(self, response_text: str) -> List[StockRating]:
        """
        Parse stock-specific ratings from the AI response.
        
        Args:
            response_text: The AI response text
            
        Returns:
            List of StockRating objects
        """
        ratings = []
        
        # Pattern: [股票名称]: [利好/利空] [分数]/10 | [原因]
        pattern = r"-\s*([^:：]+)[：:]\s*(利好|利空)\s*(\d+)/10\s*\|\s*(.+?)(?:\n|$)"
        matches = re.findall(pattern, response_text)
        
        for match in matches:
            stock_name, sentiment, score_str, reason = match
            try:
                score = max(1, min(10, int(score_str)))
                ratings.append(StockRating(
                    stock_name=stock_name.strip(),
                    is_positive=(sentiment == "利好"),
                    score=score,
                    reason=reason.strip()[:100],
                ))
            except (ValueError, IndexError):
                continue
        
        return ratings
    
    def _parse_industry_ratings(self, response_text: str) -> List[IndustryRating]:
        """
        Parse industry ratings from the AI response.
        
        Args:
            response_text: The AI response text
            
        Returns:
            List of IndustryRating objects
        """
        ratings = []
        
        # Look for industry analysis section
        if "行业评级" not in response_text and "行业名称" not in response_text:
            return ratings
        
        try:
            # Extract industry name
            name_match = re.search(r"行业名称[：:]\s*(.+?)(?:\n|$)", response_text)
            industry_name = name_match.group(1).strip() if name_match else "未知行业"
            
            # Extract impact direction
            direction_match = re.search(r"影响方向[：:]\s*(利好|利空)", response_text)
            is_positive = (
                direction_match.group(1) == "利好" if direction_match else True
            )
            
            # Extract score
            industry_score_match = re.search(
                r"评分[：:]\s*(\d+)/10", response_text[response_text.find("行业"):]
            )
            score = (
                int(industry_score_match.group(1)) if industry_score_match else 5
            )
            score = max(1, min(10, score))
            
            # Extract leader stocks
            leaders_match = re.search(r"龙头股票[：:]\s*(.+?)(?:\n|$)", response_text)
            leader_stocks = []
            if leaders_match:
                leaders_str = leaders_match.group(1).strip()
                # Parse comma or Chinese comma separated list
                leader_stocks = [
                    s.strip() for s in re.split(r"[,，、]", leaders_str) if s.strip()
                ]
            
            # Extract first principles analysis
            fp_match = re.search(
                r"第一性原理分析[：:]\s*(.+?)(?:\n\n|$)", response_text, re.DOTALL
            )
            reason = fp_match.group(1).strip()[:200] if fp_match else "基于行业基本面分析"
            
            if industry_name != "未知行业":
                ratings.append(IndustryRating(
                    industry_name=industry_name,
                    is_positive=is_positive,
                    score=score,
                    leader_stocks=leader_stocks[:5],  # Limit to top 5 leaders
                    reason=reason,
                ))
        except Exception as e:
            logger.debug(f"Failed to parse industry rating: {e}")
        
        return ratings
    
    def _analyze_fallback(self, news: NewsItem) -> AnalysisResult:
        """
        Fallback analysis using keyword-based heuristics.
        
        This is used when the AI provider is not available.
        
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
        
        # Industry keywords for first-principles analysis
        industry_keywords = {
            "新能源": ["宁德时代", "比亚迪", "隆基绿能"],
            "半导体": ["中芯国际", "韦尔股份", "北方华创"],
            "人工智能": ["科大讯飞", "商汤科技", "寒武纪"],
            "银行": ["工商银行", "建设银行", "招商银行"],
            "白酒": ["贵州茅台", "五粮液", "泸州老窖"],
            "医药": ["恒瑞医药", "药明康德", "迈瑞医疗"],
            "地产": ["万科A", "保利发展", "招商蛇口"],
        }
        
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
        
        # Generate stock ratings for mentioned stocks
        stock_ratings = []
        for stock in news.stocks:
            stock_ratings.append(StockRating(
                stock_name=stock,
                is_positive=is_positive,
                score=score,
                reason="基于关键词分析" if (positive_score + negative_score) > 0 else "影响中性"
            ))
        
        # Generate industry ratings using first-principles approach
        industry_ratings = []
        for industry, leaders in industry_keywords.items():
            if industry in content or any(kw in content for kw in [industry]):
                industry_ratings.append(IndustryRating(
                    industry_name=industry,
                    is_positive=is_positive,
                    score=score,
                    leader_stocks=leaders,
                    reason=f"基于第一性原理，{industry}行业的核心价值在于技术壁垒和市场份额"
                ))
        
        # Generate analysis
        if is_positive:
            sentiment = "利好"
            market_impact = "可能对相关板块形成正面刺激"
        else:
            sentiment = "利空" if negative_score > 0 else "中性"
            market_impact = (
                "可能对相关板块形成负面影响" if negative_score > 0 else "影响有限"
            )
        
        analysis = (
            f"基于关键词分析，该新闻{sentiment}信号明显"
            if (positive_score + negative_score) > 0
            else "该新闻影响较为中性"
        )
        
        return AnalysisResult(
            news_id=news.id,
            score=score,
            analysis=analysis,
            is_positive=is_positive,
            market_impact=market_impact,
            stock_ratings=stock_ratings,
            industry_ratings=industry_ratings,
        )


# Keep CopilotAnalyzer for backward compatibility
class CopilotAnalyzer(EnhancedAnalyzer):
    """
    Legacy analyzer class for backward compatibility.
    
    This class wraps the EnhancedAnalyzer with GitHub Copilot as the provider.
    """
    
    def __init__(self, github_token: Optional[str] = None):
        """
        Initialize the Copilot analyzer.
        
        Args:
            github_token: GitHub token with Copilot access
        """
        from .ai_providers import GitHubCopilotProvider
        provider = GitHubCopilotProvider(github_token=github_token or config.github_token)
        super().__init__(ai_provider=provider)


class NewsAnalyzer:
    """
    Main analyzer class that provides a unified interface.
    
    Uses EnhancedAnalyzer internally with configurable AI providers.
    """
    
    def __init__(
        self,
        github_token: Optional[str] = None,
        ai_provider: Optional[AIProvider] = None,
    ):
        """
        Initialize the news analyzer.
        
        Args:
            github_token: GitHub token for Copilot access (legacy parameter)
            ai_provider: Custom AI provider instance
        """
        if ai_provider:
            self._analyzer = EnhancedAnalyzer(ai_provider=ai_provider)
        else:
            # Use configuration to create the appropriate provider
            self._analyzer = EnhancedAnalyzer()
    
    def analyze(self, news: NewsItem) -> Optional[AnalysisResult]:
        """
        Analyze a news item.
        
        Args:
            news: The news item to analyze
            
        Returns:
            AnalysisResult or None if analysis fails
        """
        logger.info(f"Analyzing news: {news.id}")
        result = self._analyzer.analyze(news)
        
        if result:
            logger.info(f"Analysis complete: {result}")
        
        return result
