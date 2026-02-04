"""
AI Provider abstraction layer.

This module provides a unified interface for different AI service providers,
allowing easy switching between GitHub Copilot, Qiniu Cloud, and other services.
"""

from .base import AIProvider
from .copilot_provider import GitHubCopilotProvider
from .qiniu_provider import QiniuCloudProvider
from .factory import create_ai_provider

__all__ = [
    "AIProvider",
    "GitHubCopilotProvider",
    "QiniuCloudProvider",
    "create_ai_provider",
]
