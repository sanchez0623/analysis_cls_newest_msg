"""
Base AI Provider interface.

This module defines the abstract base class for AI providers.
"""

from abc import ABC, abstractmethod
from typing import Optional


class AIProvider(ABC):
    """
    Abstract base class for AI service providers.
    
    All AI providers must implement this interface to ensure
    consistent behavior across different services.
    """
    
    @abstractmethod
    def analyze(self, prompt: str) -> Optional[str]:
        """
        Send a prompt to the AI service and get a response.
        
        Args:
            prompt: The analysis prompt to send
            
        Returns:
            The AI response text, or None if the request fails
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the AI provider is available and properly configured.
        
        Returns:
            True if the provider is ready to use, False otherwise
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        Get the name of the AI provider.
        
        Returns:
            The provider name string
        """
        pass
