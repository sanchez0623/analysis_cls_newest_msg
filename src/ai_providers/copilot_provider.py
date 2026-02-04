"""
GitHub Copilot AI Provider.

This module provides AI analysis using the GitHub Copilot SDK.
"""

import logging
from typing import Optional

from .base import AIProvider


logger = logging.getLogger(__name__)


class GitHubCopilotProvider(AIProvider):
    """
    AI Provider using GitHub Copilot SDK.
    
    This provider uses the GitHub Copilot SDK to perform
    AI-powered news analysis.
    """
    
    def __init__(self, github_token: Optional[str] = None):
        """
        Initialize the GitHub Copilot provider.
        
        Args:
            github_token: GitHub token with Copilot access
        """
        self._token = github_token
        self._session = None
        self._initialize_sdk()
    
    def _initialize_sdk(self) -> None:
        """Initialize the Copilot SDK session."""
        if not self._token:
            logger.warning("No GitHub token provided for Copilot provider.")
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
    
    def analyze(self, prompt: str) -> Optional[str]:
        """
        Send a prompt to GitHub Copilot and get a response.
        
        Args:
            prompt: The analysis prompt to send
            
        Returns:
            The AI response text, or None if the request fails
        """
        if not self._session:
            logger.warning("Copilot session not available")
            return None
        
        try:
            response = self._session.ask(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Copilot analysis failed: {e}")
            return None
    
    def is_available(self) -> bool:
        """
        Check if the GitHub Copilot provider is available.
        
        Returns:
            True if Copilot SDK is initialized, False otherwise
        """
        return self._session is not None
    
    @property
    def name(self) -> str:
        """Get the provider name."""
        return "GitHub Copilot"
