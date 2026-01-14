"""
Configuration management for validation testing.

Loads API keys and model configuration from environment variables or .env file.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any, Tuple, List

# Try to load python-dotenv if available
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


def _load_env_file_manual(env_file: Path):
    """Manually parse .env file if dotenv is not available."""
    if not env_file.exists():
        return
    
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            # Parse KEY=VALUE
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                # Remove quotes if present
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                # Only set if not already in environment
                if key not in os.environ:
                    os.environ[key] = value


def load_config() -> Dict[str, Any]:
    """
    Load configuration from environment variables or .env file.
    
    Returns:
        Configuration dictionary
    """
    # Load .env file
    validation_dir = Path(__file__).parent
    env_file = validation_dir / ".env"
    
    if DOTENV_AVAILABLE:
        if env_file.exists():
            load_dotenv(env_file)
        else:
            # Try parent directory
            parent_env = validation_dir.parent.parent / ".env"
            if parent_env.exists():
                load_dotenv(parent_env)
    else:
        # Manual parsing if dotenv not available
        if env_file.exists():
            _load_env_file_manual(env_file)
        else:
            # Try parent directory
            parent_env = validation_dir.parent.parent / ".env"
            if parent_env.exists():
                _load_env_file_manual(parent_env)
    
    config = {
        # OpenAI configuration
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "openai_model": os.getenv("OPENAI_MODEL", "gpt-4"),
        "openai_base_url": os.getenv("OPENAI_BASE_URL"),  # For custom endpoints
        
        # Anthropic configuration
        "anthropic_api_key": os.getenv("ANTHROPIC_API_KEY"),
        "anthropic_model": os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
        
        # OpenRouter configuration (OpenAI-compatible)
        "openrouter_api_key": os.getenv("OPENROUTER_API_KEY"),
        "openrouter_model": os.getenv("OPENROUTER_MODEL"),
        "openrouter_base_url": os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        
        # Default model provider
        "default_provider": os.getenv("LLM_PROVIDER", "openai"),  # "openai", "anthropic", or "openrouter"
        "default_model": os.getenv("LLM_MODEL", "gpt-4"),
        
        # API settings
        "api_timeout": int(os.getenv("API_TIMEOUT", "60")),
        "max_retries": int(os.getenv("MAX_RETRIES", "3")),
        "temperature": float(os.getenv("LLM_TEMPERATURE", "0.0")),  # Low temperature for consistent results
    }
    
    return config


def get_api_key(provider: str) -> Optional[str]:
    """
    Get API key for a specific provider.
    
    Args:
        provider: "openai", "anthropic", or "openrouter"
        
    Returns:
        API key or None
    """
    config = load_config()
    if provider.lower() == "openai":
        return config["openai_api_key"]
    elif provider.lower() == "anthropic":
        return config["anthropic_api_key"]
    elif provider.lower() == "openrouter":
        return config["openrouter_api_key"]
    return None


def get_model(provider: str) -> str:
    """
    Get model name for a specific provider.
    
    Args:
        provider: "openai", "anthropic", or "openrouter"
        
    Returns:
        Model name
    """
    config = load_config()
    if provider.lower() == "openai":
        return config["openai_model"]
    elif provider.lower() == "anthropic":
        return config["anthropic_model"]
    elif provider.lower() == "openrouter":
        return config["openrouter_model"] or config["default_model"]
    return config["default_model"]


def validate_config() -> Tuple[bool, List[str]]:
    """
    Validate that required configuration is present.
    
    Returns:
        Tuple of (is_valid, list_of_missing_keys)
    """
    config = load_config()
    missing = []
    
    provider = config["default_provider"]
    
    if provider.lower() == "openai":
        if not config["openai_api_key"]:
            missing.append("OPENAI_API_KEY")
    elif provider.lower() == "anthropic":
        if not config["anthropic_api_key"]:
            missing.append("ANTHROPIC_API_KEY")
    elif provider.lower() == "openrouter":
        if not config["openrouter_api_key"]:
            missing.append("OPENROUTER_API_KEY")
        if not config["openrouter_model"] and not config["default_model"]:
            missing.append("OPENROUTER_MODEL or LLM_MODEL")
    else:
        missing.append(f"API key for provider: {provider}")
    
    return len(missing) == 0, missing

