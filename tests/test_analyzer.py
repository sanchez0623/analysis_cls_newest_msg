"""
Tests for the analyzer module.
"""

import unittest
from unittest.mock import patch, MagicMock

from src.analyzer import NewsAnalyzer, CopilotAnalyzer
from src.models import NewsItem, AnalysisResult


class TestCopilotAnalyzer(unittest.TestCase):
    """Test cases for CopilotAnalyzer."""
    
    def test_parse_analysis_response(self):
        """Test parsing of AI response."""
        analyzer = CopilotAnalyzer()
        
        response_text = """
评分：8
影响：利好
分析：重大政策利好，对市场有积极影响
市场影响：可能推动相关板块上涨
"""
        
        result = analyzer._parse_analysis_response("test-id", response_text)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.news_id, "test-id")
        self.assertEqual(result.score, 8)
        self.assertTrue(result.is_positive)
        self.assertIn("相关板块", result.market_impact)
    
    def test_parse_analysis_response_invalid_score(self):
        """Test handling of invalid score values."""
        analyzer = CopilotAnalyzer()
        
        response_text = """
评分：15
影响：利好
分析：测试
市场影响：测试
"""
        
        result = analyzer._parse_analysis_response("test-id", response_text)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.score, 10)  # Should be clamped to max
    
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


if __name__ == "__main__":
    unittest.main()
