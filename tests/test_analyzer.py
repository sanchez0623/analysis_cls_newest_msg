"""
Tests for the analyzer module.
"""

import unittest
from unittest.mock import patch, MagicMock

from src.analyzer import NewsAnalyzer, CopilotAnalyzer, EnhancedAnalyzer
from src.models import NewsItem, AnalysisResult, StockRating, IndustryRating


class TestEnhancedAnalyzer(unittest.TestCase):
    """Test cases for EnhancedAnalyzer."""
    
    def test_parse_stock_ratings(self):
        """Test parsing of stock-specific ratings from AI response."""
        analyzer = EnhancedAnalyzer()
        
        response_text = """
评分：8
影响：利好
分析：重大政策利好

个股评级：
- 工商银行: 利好 8/10 | 降息利好银行净息差
- 建设银行: 利好 7/10 | 宽松政策提振信贷需求
"""
        
        ratings = analyzer._parse_stock_ratings(response_text)
        
        self.assertEqual(len(ratings), 2)
        self.assertEqual(ratings[0].stock_name, "工商银行")
        self.assertTrue(ratings[0].is_positive)
        self.assertEqual(ratings[0].score, 8)
        self.assertIn("净息差", ratings[0].reason)
    
    def test_parse_industry_ratings(self):
        """Test parsing of industry ratings from AI response."""
        analyzer = EnhancedAnalyzer()
        
        response_text = """
行业评级：
- 行业名称: 银行
- 影响方向: 利好
- 评分: 8/10
- 龙头股票: 工商银行, 建设银行, 招商银行
- 第一性原理分析: 银行业核心价值在于息差收入，降息影响存贷差
"""
        
        ratings = analyzer._parse_industry_ratings(response_text)
        
        self.assertEqual(len(ratings), 1)
        self.assertEqual(ratings[0].industry_name, "银行")
        self.assertTrue(ratings[0].is_positive)
        self.assertEqual(ratings[0].score, 8)
        self.assertIn("工商银行", ratings[0].leader_stocks)
        # Verify that the reason contains first-principles analysis content
        self.assertIn("息差", ratings[0].reason)
    
    def test_fallback_analysis_with_stocks(self):
        """Test fallback analysis generates stock ratings when stocks are present."""
        analyzer = EnhancedAnalyzer()
        
        news = NewsItem(
            id="test-id",
            title="重大利好",
            content="央行降息支持经济增长，市场反弹创新高",
            ctime=1704067200,
            stocks=["工商银行", "建设银行"],
        )
        
        result = analyzer._analyze_fallback(news)
        
        self.assertIsNotNone(result)
        self.assertTrue(result.is_positive)
        self.assertEqual(len(result.stock_ratings), 2)
        self.assertEqual(result.stock_ratings[0].stock_name, "工商银行")
    
    def test_fallback_analysis_with_industry(self):
        """Test fallback analysis generates industry ratings for industry events."""
        analyzer = EnhancedAnalyzer()
        
        news = NewsItem(
            id="test-id",
            title="银行业利好",
            content="央行政策利好银行业，预计银行盈利将增长",
            ctime=1704067200,
            subjects=["银行", "央行"],
        )
        
        result = analyzer._analyze_fallback(news)
        
        self.assertIsNotNone(result)
        self.assertTrue(result.is_positive)
        self.assertTrue(len(result.industry_ratings) > 0)


class TestCopilotAnalyzer(unittest.TestCase):
    """Test cases for CopilotAnalyzer (backward compatibility)."""
    
    def test_copilot_analyzer_inherits_enhanced(self):
        """Test that CopilotAnalyzer inherits from EnhancedAnalyzer."""
        analyzer = CopilotAnalyzer()
        self.assertIsInstance(analyzer, EnhancedAnalyzer)
    
    def test_fallback_analysis_positive(self):
        """Test fallback analysis with positive keywords."""
        analyzer = CopilotAnalyzer()
        
        news = NewsItem(
            id="test-id",
            title="重大利好",
            content="央行降息支持经济增长，市场反弹创新高",
            ctime=1704067200,
        )
        
        result = analyzer._analyze_fallback(news)
        
        self.assertIsNotNone(result)
        self.assertTrue(result.is_positive)
        self.assertGreater(result.score, 5)
    
    def test_fallback_analysis_negative(self):
        """Test fallback analysis with negative keywords."""
        analyzer = CopilotAnalyzer()
        
        news = NewsItem(
            id="test-id",
            title="风险警告",
            content="市场暴跌，亏损加剧，不及预期",
            ctime=1704067200,
        )
        
        result = analyzer._analyze_fallback(news)
        
        self.assertIsNotNone(result)
        self.assertFalse(result.is_positive)
        self.assertLess(result.score, 5)
    
    def test_fallback_analysis_neutral(self):
        """Test fallback analysis with neutral content."""
        analyzer = CopilotAnalyzer()
        
        news = NewsItem(
            id="test-id",
            title="普通新闻",
            content="今天天气不错",
            ctime=1704067200,
        )
        
        result = analyzer._analyze_fallback(news)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.score, 5)  # Should be base score


class TestNewsAnalyzer(unittest.TestCase):
    """Test cases for NewsAnalyzer."""
    
    def test_analyze_returns_result(self):
        """Test that analyze returns a result."""
        analyzer = NewsAnalyzer()
        
        news = NewsItem(
            id="test-id",
            title="Test",
            content="央行宣布降息，支持经济增长",
            ctime=1704067200,
        )
        
        result = analyzer.analyze(news)
        
        self.assertIsNotNone(result)
        self.assertIsInstance(result, AnalysisResult)
    
    def test_analyze_with_stocks_returns_stock_ratings(self):
        """Test that analysis with stocks returns stock ratings."""
        analyzer = NewsAnalyzer()
        
        news = NewsItem(
            id="test-id",
            title="Test",
            content="央行宣布降息，支持经济增长",
            ctime=1704067200,
            stocks=["工商银行"],
        )
        
        result = analyzer.analyze(news)
        
        self.assertIsNotNone(result)
        self.assertTrue(result.has_stock_ratings)


class TestStockRating(unittest.TestCase):
    """Test cases for StockRating model."""
    
    def test_str_representation(self):
        """Test string representation of stock rating."""
        rating = StockRating(
            stock_name="工商银行",
            is_positive=True,
            score=8,
            reason="降息利好银行净息差",
        )
        
        str_repr = str(rating)
        
        self.assertIn("工商银行", str_repr)
        self.assertIn("利好", str_repr)
        self.assertIn("8/10", str_repr)


class TestIndustryRating(unittest.TestCase):
    """Test cases for IndustryRating model."""
    
    def test_str_representation(self):
        """Test string representation of industry rating."""
        rating = IndustryRating(
            industry_name="银行",
            is_positive=True,
            score=8,
            leader_stocks=["工商银行", "建设银行"],
            reason="第一性原理分析：银行业核心价值在于息差收入",
        )
        
        str_repr = str(rating)
        
        self.assertIn("银行", str_repr)
        self.assertIn("利好", str_repr)
        self.assertIn("龙头", str_repr)


class TestAnalysisResult(unittest.TestCase):
    """Test cases for AnalysisResult model."""
    
    def test_str_representation(self):
        """Test string representation of analysis result."""
        result = AnalysisResult(
            news_id="test-id",
            score=8,
            analysis="Test analysis",
            is_positive=True,
            market_impact="Positive impact",
        )
        
        str_repr = str(result)
        
        self.assertIn("8/10", str_repr)
        self.assertIn("利好", str_repr)
    
    def test_has_stock_ratings(self):
        """Test has_stock_ratings property."""
        result = AnalysisResult(
            news_id="test-id",
            score=8,
            analysis="Test",
            is_positive=True,
            market_impact="Test",
            stock_ratings=[
                StockRating("Test", True, 8, "Test")
            ],
        )
        
        self.assertTrue(result.has_stock_ratings)
    
    def test_has_industry_ratings(self):
        """Test has_industry_ratings property."""
        result = AnalysisResult(
            news_id="test-id",
            score=8,
            analysis="Test",
            is_positive=True,
            market_impact="Test",
            industry_ratings=[
                IndustryRating("Test", True, 8, ["Test"], "Test")
            ],
        )
        
        self.assertTrue(result.has_industry_ratings)


if __name__ == "__main__":
    unittest.main()
