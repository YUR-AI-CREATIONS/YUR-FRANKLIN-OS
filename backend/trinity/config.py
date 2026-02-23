import os
from functools import lru_cache


class TrinityConfig:
    """Centralized environment configuration for Trinity AI.

    Loads keys once; exposes helper to list missing keys for diagnostics.
    """
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

    def missing_keys(self):
        missing = []
        if not self.gemini_api_key:
            missing.append("GEMINI_API_KEY")
        if not self.openai_api_key:
            missing.append("OPENAI_API_KEY")
        if not self.anthropic_api_key:
            missing.append("ANTHROPIC_API_KEY")
        return missing


@lru_cache()
def get_config():
    return TrinityConfig()
