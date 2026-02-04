"""
Tests for the CLS scraper module.
"""

import hashlib
import time
import unittest
from unittest.mock import patch, MagicMock

from src.scraper import CLSScraper
from src.models import NewsItem


class TestCLSScraper(unittest.TestCase):
    """Test cases for CLSScraper."""
    
    def test_generate_sign(self):
        """Test signature generation."""
        # Test with a known input
        params_str = "app=CailianpressWeb&last_time=1234567890&os=web&rn=1&sv=7.2.2"
        
        # Calculate expected signature
        sha1_hash = hashlib.sha1(params_str.encode("utf-8")).hexdigest()
        expected_sign = hashlib.md5(sha1_hash.encode("utf-8")).hexdigest()
        
        # Get actual signature
        actual_sign = CLSScraper._generate_sign(params_str)
        
        self.assertEqual(actual_sign, expected_sign)
    
    def test_build_api_url_contains_required_params(self):
        """Test that the API URL contains all required parameters."""
        scraper = CLSScraper()
        
        url = scraper._build_api_url(last_time=1234567890)
        
        self.assertIn("app=CailianpressWeb", url)
        self.assertIn("last_time=1234567890", url)
        self.assertIn("os=web", url)
        self.assertIn("sv=7.2.2", url)
        self.assertIn("sign=", url)
        
        scraper.close()
    
    def test_user_agent_rotation(self):
        """Test that user agents are rotated."""
        scraper = CLSScraper()
        
        # Get multiple user agents
        agents = set()
        for _ in range(50):
            agent = scraper._get_random_user_agent()
            agents.add(agent)
        
        # Should have more than 1 unique agent
        self.assertGreater(len(agents), 1)
        
        scraper.close()
    
    def test_build_api_url_with_count(self):
        """Test that the API URL is built correctly with custom count."""
        scraper = CLSScraper()
        
        url = scraper._build_api_url(last_time=1234567890, count=20)
        
        # Should contain rn=20
        self.assertIn("rn=20", url)
        
        # Verify signature is correct for count=20
        import hashlib
        params_str = "app=CailianpressWeb&last_time=1234567890&os=web&rn=20&sv=7.2.2"
        sha1 = hashlib.sha1(params_str.encode("utf-8")).hexdigest()
        expected_sign = hashlib.md5(sha1.encode("utf-8")).hexdigest()
        
        self.assertIn(f"sign={expected_sign}", url)
        
        scraper.close()

    @patch("requests.Session.get")
    def test_fetch_latest_news_success(self, mock_get):
        """Test successful news fetch."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "errno": 0,
            "data": {
                "roll_data": [
                    {
                        "id": "12345",
                        "title": "Test News",
                        "content": "Test content",
                        "ctime": int(time.time()),
                        "stocks": [{"name": "TEST"}],
                        "subjects": [{"name": "测试"}],
                    }
                ]
            }
        }
        mock_get.return_value = mock_response
        
        scraper = CLSScraper()
        news = scraper.fetch_latest_news()
        
        self.assertIsNotNone(news)
        self.assertEqual(news.id, "12345")
        self.assertEqual(news.title, "Test News")
        
        scraper.close()
    
    @patch("requests.Session.get")
    def test_fetch_latest_news_duplicate_detection(self, mock_get):
        """Test that duplicate news items are detected."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "errno": 0,
            "data": {
                "roll_data": [
                    {
                        "id": "12345",
                        "title": "Test News",
                        "content": "Test content",
                        "ctime": int(time.time()),
                    }
                ]
            }
        }
        mock_get.return_value = mock_response
        
        scraper = CLSScraper()
        
        # First fetch should return the news
        news1 = scraper.fetch_latest_news()
        self.assertIsNotNone(news1)
        
        # Second fetch of same ID should return None
        news2 = scraper.fetch_latest_news()
        self.assertIsNone(news2)
        
        scraper.close()
    
    @patch("requests.Session.get")
    def test_fetch_latest_news_api_error(self, mock_get):
        """Test handling of API errors."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "errno": 1001,
            "errmsg": "Test error",
        }
        mock_get.return_value = mock_response
        
        scraper = CLSScraper()
        news = scraper.fetch_latest_news()
        
        self.assertIsNone(news)
        
        scraper.close()


class TestNewsItem(unittest.TestCase):
    """Test cases for NewsItem model."""
    
    def test_from_api_response(self):
        """Test creating NewsItem from API response."""
        data = {
            "id": "12345",
            "title": "Test Title",
            "content": "Test Content",
            "ctime": 1704067200,  # 2024-01-01 00:00:00
            "stocks": [{"name": "AAPL"}],
            "subjects": [{"name": "Tech"}],
        }
        
        news = NewsItem.from_api_response(data)
        
        self.assertEqual(news.id, "12345")
        self.assertEqual(news.title, "Test Title")
        self.assertEqual(news.content, "Test Content")
        self.assertEqual(news.stocks, ["AAPL"])
        self.assertEqual(news.subjects, ["Tech"])
    
    def test_from_api_response_missing_fields(self):
        """Test handling of missing fields."""
        data = {
            "id": "12345",
        }
        
        news = NewsItem.from_api_response(data)
        
        self.assertEqual(news.id, "12345")
        self.assertEqual(news.title, "")
        self.assertEqual(news.content, "")
        self.assertEqual(news.stocks, [])
        self.assertEqual(news.subjects, [])


if __name__ == "__main__":
    unittest.main()
