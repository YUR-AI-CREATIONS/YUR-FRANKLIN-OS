"""
Shared LLM provider module
"""

from llm_providers import HybridLLMProvider, LLMConfig, LLMMode

# Global LLM Provider - supports cloud/local switching
llm_provider = None

def get_default_llm_config() -> LLMConfig:
    """Create default LLM configuration"""
    return LLMConfig(
        mode=LLMMode.CLOUD,  # Default to cloud
        cloud_provider="anthropic",
        cloud_model="claude-sonnet-4-5-20250929",
        emergent_key=None,  # Set from env
        local_url="http://localhost:11434",
        local_model="llama3.1:8b",
        fallback_to_cloud=True,
        max_retries=3
    )

async def initialize_llm_provider():
    """Initialize the global LLM provider"""
    global llm_provider
    config = get_default_llm_config()
    llm_provider = HybridLLMProvider(config)
    await llm_provider.initialize()
    
    # If local is not available and mode is local-only, auto-switch to hybrid
    if not llm_provider.local_available and config.mode == LLMMode.LOCAL:
        import logging
        logging.warning("Local LLM unavailable, switching to hybrid mode with cloud fallback")
        llm_provider.config.mode = LLMMode.HYBRID
        llm_provider.config.fallback_to_cloud = True
    
    import logging
    logging.info(f"LLM Provider initialized: mode={llm_provider.config.mode.value}, local_available={llm_provider.local_available}")

async def get_llm_provider() -> HybridLLMProvider:
    """Get the global LLM provider, initializing if needed"""
    global llm_provider
    if llm_provider is None:
        await initialize_llm_provider()
    return llm_provider