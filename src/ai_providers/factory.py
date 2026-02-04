"""
AI Provider Factory.

This module provides a factory function to create AI providers
based on configuration settings.
"""

import logging
from typing import Optional

from .base import AIProvider
from .copilot_provider import GitHubCopilotProvider
from .qiniu_provider import QiniuCloudProvider


logger = logging.getLogger(__name__)


# Supported AI providers
AI_PROVIDER_COPILOT = "copilot"
AI_PROVIDER_QINIU = "qiniu"


def create_ai_provider(
    provider_name: str,
    github_token: Optional[str] = None,
    qiniu_access_key: Optional[str] = None,
    qiniu_secret_key: Optional[str] = None,
    qiniu_api_endpoint: Optional[str] = None,
) -> AIProvider:
    """
    Create an AI provider based on the specified provider name.
    
    Args:
        provider_name: The name of the AI provider to use
            ("copilot" or "qiniu")
        github_token: GitHub token for Copilot provider
        qiniu_access_key: Qiniu Cloud access key
        qiniu_secret_key: Qiniu Cloud secret key
        qiniu_api_endpoint: Qiniu Cloud API endpoint
        
    Returns:
        An instance of the specified AI provider
        
    Raises:
        ValueError: If an unknown provider name is specified
    """
    provider_name = provider_name.lower().strip()
    
    if provider_name == AI_PROVIDER_COPILOT:
        logger.info("Creating GitHub Copilot AI provider")
        return GitHubCopilotProvider(github_token=github_token)
    
    elif provider_name == AI_PROVIDER_QINIU:
        logger.info("Creating Qiniu Cloud AI provider")
        return QiniuCloudProvider(
            access_key=qiniu_access_key,
            secret_key=qiniu_secret_key,
            api_endpoint=qiniu_api_endpoint,
        )
    
    else:
        raise ValueError(
            f"Unknown AI provider: {provider_name}. "
            f"Supported providers: {AI_PROVIDER_COPILOT}, {AI_PROVIDER_QINIU}"
        )
