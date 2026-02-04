"""
Tests for the AI providers module.
"""

import unittest
from unittest.mock import patch, MagicMock

from src.ai_providers import (
    AIProvider,
    GitHubCopilotProvider,
    QiniuCloudProvider,
    create_ai_provider,
)
from src.ai_providers.factory import AI_PROVIDER_COPILOT, AI_PROVIDER_QINIU


class TestAIProviderFactory(unittest.TestCase):
    """Test cases for AI provider factory."""
    
    def test_create_copilot_provider(self):
        """Test creating GitHub Copilot provider."""
        provider = create_ai_provider(
            provider_name="copilot",
            github_token="test-token",
        )
        
        self.assertIsInstance(provider, GitHubCopilotProvider)
        self.assertEqual(provider.name, "GitHub Copilot")
    
    def test_create_qiniu_provider(self):
        """Test creating Qiniu Cloud provider."""
        provider = create_ai_provider(
            provider_name="qiniu",
            qiniu_access_key="test-key",
            qiniu_secret_key="test-secret",
        )
        
        self.assertIsInstance(provider, QiniuCloudProvider)
        self.assertEqual(provider.name, "Qiniu Cloud")
    
    def test_create_provider_case_insensitive(self):
        """Test that provider name is case insensitive."""
        provider1 = create_ai_provider("COPILOT")
        provider2 = create_ai_provider("Copilot")
        provider3 = create_ai_provider("copilot")
        
        self.assertIsInstance(provider1, GitHubCopilotProvider)
        self.assertIsInstance(provider2, GitHubCopilotProvider)
        self.assertIsInstance(provider3, GitHubCopilotProvider)
    
    def test_create_unknown_provider_raises_error(self):
        """Test that unknown provider name raises ValueError."""
        with self.assertRaises(ValueError) as context:
            create_ai_provider("unknown_provider")
        
        self.assertIn("Unknown AI provider", str(context.exception))


class TestGitHubCopilotProvider(unittest.TestCase):
    """Test cases for GitHub Copilot provider."""
    
    def test_name_property(self):
        """Test name property."""
        provider = GitHubCopilotProvider()
        self.assertEqual(provider.name, "GitHub Copilot")
    
    def test_not_available_without_token(self):
        """Test that provider is not available without token."""
        provider = GitHubCopilotProvider(github_token=None)
        # Without SDK installed, it won't be available
        self.assertFalse(provider.is_available())
    
    def test_analyze_returns_none_without_session(self):
        """Test that analyze returns None when session is not available."""
        provider = GitHubCopilotProvider()
        result = provider.analyze("test prompt")
        self.assertIsNone(result)


class TestQiniuCloudProvider(unittest.TestCase):
    """Test cases for Qiniu Cloud provider."""
    
    def test_name_property(self):
        """Test name property."""
        provider = QiniuCloudProvider()
        self.assertEqual(provider.name, "Qiniu Cloud")
    
    def test_not_available_without_credentials(self):
        """Test that provider is not available without credentials."""
        provider = QiniuCloudProvider()
        self.assertFalse(provider.is_available())
    
    def test_analyze_returns_none_without_credentials(self):
        """Test that analyze returns None when not initialized."""
        provider = QiniuCloudProvider()
        result = provider.analyze("test prompt")
        self.assertIsNone(result)
    
    def test_initialization_with_credentials(self):
        """Test that provider initializes with credentials."""
        provider = QiniuCloudProvider(
            access_key="test-key",
            secret_key="test-secret",
        )
        self.assertTrue(provider.is_available())
    
    @patch("requests.Session.post")
    def test_analyze_with_credentials(self, mock_post):
        """Test analyze call with credentials."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "Test AI response"
                    }
                }
            ]
        }
        mock_post.return_value = mock_response
        
        provider = QiniuCloudProvider(
            access_key="test-key",
            secret_key="test-secret",
        )
        
        result = provider.analyze("test prompt")
        
        self.assertEqual(result, "Test AI response")
        mock_post.assert_called_once()


class TestAIProviderInterface(unittest.TestCase):
    """Test cases for AIProvider abstract interface."""
    
    def test_providers_implement_interface(self):
        """Test that all providers implement the AIProvider interface."""
        providers = [
            GitHubCopilotProvider(),
            QiniuCloudProvider(),
        ]
        
        for provider in providers:
            self.assertIsInstance(provider, AIProvider)
            self.assertTrue(hasattr(provider, "analyze"))
            self.assertTrue(hasattr(provider, "is_available"))
            self.assertTrue(hasattr(provider, "name"))


if __name__ == "__main__":
    unittest.main()
