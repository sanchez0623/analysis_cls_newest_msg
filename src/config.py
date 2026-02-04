"""
Configuration management for CLS News Scraper and Analyzer.
"""

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


@dataclass
class Config:
    """Application configuration."""
    
    # GitHub Copilot settings
    github_token: Optional[str] = None
    
    # Scraper settings
    scrape_interval: int = 5  # seconds
    fetch_count: int = 1
    request_timeout: int = 10
    max_retries: int = 3
    
    # Logging
    log_level: str = "INFO"
    
    # CLS API settings
    cls_api_url: str = "https://www.cls.cn/nodeapi/telegraphList"
    cls_app: str = "CailianpressWeb"
    cls_os: str = "web"
    cls_sv: str = "7.2.2"
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        load_dotenv()
        
        return cls(
            github_token=os.getenv("GITHUB_TOKEN"),
            scrape_interval=int(os.getenv("SCRAPE_INTERVAL", "5")),
            fetch_count=int(os.getenv("FETCH_COUNT", "1")),
            request_timeout=int(os.getenv("REQUEST_TIMEOUT", "10")),
            max_retries=int(os.getenv("MAX_RETRIES", "3")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )


# Global configuration instance
config = Config.from_env()
