"""Platform payload translators."""
from src.orchestration.translators.base import PlatformTranslator
from src.orchestration.translators.meta import MetaTranslator
from src.orchestration.translators.tiktok import TikTokTranslator
from src.orchestration.translators.google import GoogleTranslator


def get_translator(platform_name: str) -> PlatformTranslator:
    """
    Get the appropriate translator for a platform.
    
    Args:
        platform_name: Platform name (meta/tiktok)
        
    Returns:
        PlatformTranslator instance
        
    Raises:
        ValueError: If platform is not supported
    """
    platform_name = platform_name.lower()
    
    if platform_name == "meta":
        return MetaTranslator()
    elif platform_name == "tiktok":
        return TikTokTranslator()
    elif platform_name == "google" or platform_name == "google ads":
        return GoogleTranslator()
    else:
        raise ValueError(f"Unsupported platform: {platform_name}")


__all__ = ["PlatformTranslator", "MetaTranslator", "TikTokTranslator", "GoogleTranslator", "get_translator"]
