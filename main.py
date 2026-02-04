#!/usr/bin/env python3
"""
CLS News Scraper and Analyzer Main Application.

This application:
1. Scrapes the latest news from CLS Telegraph every 5 seconds
2. Analyzes news using GitHub Copilot API
3. Provides market sentiment ratings (1-10)
4. Skips duplicate news items

Usage:
    python main.py
    
Or with custom interval:
    SCRAPE_INTERVAL=10 python main.py
"""

import logging
import signal
import sys
import time
from datetime import datetime
from typing import Optional

from src.config import config
from src.scraper import CLSScraper
from src.analyzer import NewsAnalyzer
from src.models import NewsItem, AnalysisResult


# Set up logging
def setup_logging() -> None:
    """Configure application logging."""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper()),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )


logger = logging.getLogger(__name__)


class CLSNewsMonitor:
    """
    Main monitor class that orchestrates scraping and analysis.
    
    Features:
    - Continuous monitoring with configurable interval
    - Graceful shutdown handling
    - Error recovery
    - Statistics tracking
    """
    
    def __init__(self):
        """Initialize the monitor."""
        self._running = False
        self._scraper = CLSScraper()
        self._analyzer = NewsAnalyzer()
        
        # Statistics
        self._stats = {
            "total_fetches": 0,
            "new_items": 0,
            "duplicates": 0,
            "errors": 0,
            "start_time": None,
        }
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)
    
    def _handle_shutdown(self, signum: int, frame) -> None:
        """Handle shutdown signals gracefully."""
        logger.info("Received shutdown signal. Stopping monitor...")
        self._running = False
    
    def _display_result(self, news: NewsItem, result: AnalysisResult) -> None:
        """
        Display the analysis result in a formatted way.
        
        Args:
            news: The analyzed news item
            result: The analysis result
        """
        separator = "=" * 60
        
        print(f"\n{separator}")
        print(f"📰 新闻快讯 | {news.display_time}")
        print(separator)
        print(f"内容: {news.content}")
        
        if news.stocks:
            print(f"相关股票: {', '.join(news.stocks)}")
        if news.subjects:
            print(f"相关主题: {', '.join(news.subjects)}")
        
        print(separator)
        
        # Display score with visual indicator
        score_bar = "★" * result.score + "☆" * (10 - result.score)
        sentiment_emoji = "📈" if result.is_positive else "📉"
        
        print(f"📊 市场热度: {score_bar} ({result.score}/10)")
        print(f"{sentiment_emoji} 市场影响: {'利好' if result.is_positive else '利空/中性'}")
        print(f"💡 分析: {result.analysis}")
        print(f"🎯 市场影响: {result.market_impact}")
        print(separator)
    
    def _display_stats(self) -> None:
        """Display current statistics."""
        if self._stats["start_time"]:
            runtime = datetime.now() - self._stats["start_time"]
            print(f"\n📈 运行统计:")
            print(f"   运行时长: {runtime}")
            print(f"   总请求次数: {self._stats['total_fetches']}")
            print(f"   新消息数量: {self._stats['new_items']}")
            print(f"   重复消息数量: {self._stats['duplicates']}")
            print(f"   错误次数: {self._stats['errors']}")
    
    def run(self) -> None:
        """
        Start the monitoring loop.
        
        This method runs continuously until interrupted.
        """
        self._running = True
        self._stats["start_time"] = datetime.now()
        
        logger.info(f"Starting CLS News Monitor...")
        logger.info(f"Scrape interval: {config.scrape_interval} seconds")
        print("\n" + "=" * 60)
        print("🚀 CLS 财联社新闻监控已启动")
        print(f"⏱️  刷新间隔: {config.scrape_interval} 秒")
        print("💡 按 Ctrl+C 停止监控")
        print("=" * 60 + "\n")
        
        while self._running:
            try:
                self._process_cycle()
            except Exception as e:
                logger.error(f"Error in processing cycle: {e}")
                self._stats["errors"] += 1
            
            # Wait for next cycle
            if self._running:
                time.sleep(config.scrape_interval)
        
        # Cleanup
        self._shutdown()
    
    def _process_cycle(self) -> None:
        """Process a single fetch-analyze cycle."""
        self._stats["total_fetches"] += 1
        
        # Fetch latest news
        news = self._scraper.fetch_latest_news()
        
        if news is None:
            self._stats["duplicates"] += 1
            logger.debug("No new news item (duplicate or error)")
            return
        
        self._stats["new_items"] += 1
        
        # Analyze the news
        result = self._analyzer.analyze(news)
        
        if result:
            self._display_result(news, result)
        else:
            logger.warning(f"Analysis failed for news: {news.id}")
    
    def _shutdown(self) -> None:
        """Clean up resources on shutdown."""
        logger.info("Shutting down monitor...")
        self._scraper.close()
        self._display_stats()
        print("\n👋 监控已停止")


def main() -> None:
    """Main entry point."""
    setup_logging()
    
    monitor = CLSNewsMonitor()
    monitor.run()


if __name__ == "__main__":
    main()
