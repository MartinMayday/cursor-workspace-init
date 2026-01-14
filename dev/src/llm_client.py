"""
LLM client for semantic codebase analysis.

Supports OpenAI, Anthropic, and OpenRouter providers.
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path

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
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                if key not in os.environ:
                    os.environ[key] = value


def load_llm_config() -> Dict[str, Any]:
    """
    Load LLM configuration from environment variables or .env file.
    
    Returns:
        Configuration dictionary
    """
    # Try to load .env from project root or dev/src
    project_root = Path.cwd()
    env_files = [
        project_root / ".env",
        project_root / "dev" / "src" / ".env",
        Path(__file__).parent.parent.parent / ".env",
    ]
    
    for env_file in env_files:
        if env_file.exists():
            if DOTENV_AVAILABLE:
                load_dotenv(env_file)
            else:
                _load_env_file_manual(env_file)
            break
    
    config = {
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "openai_model": os.getenv("OPENAI_MODEL", "gpt-4"),
        "openai_base_url": os.getenv("OPENAI_BASE_URL"),
        
        "anthropic_api_key": os.getenv("ANTHROPIC_API_KEY"),
        "anthropic_model": os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
        
        "openrouter_api_key": os.getenv("OPENROUTER_API_KEY"),
        "openrouter_model": os.getenv("OPENROUTER_MODEL"),
        "openrouter_base_url": os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        
        "default_provider": os.getenv("LLM_PROVIDER", "openai"),
        "default_model": os.getenv("LLM_MODEL", "gpt-4"),
        
        "api_timeout": int(os.getenv("API_TIMEOUT", "120")),
        "max_retries": int(os.getenv("MAX_RETRIES", "3")),
        "temperature": float(os.getenv("LLM_TEMPERATURE", "0.1")),
    }
    
    return config


def get_api_key(provider: str) -> Optional[str]:
    """Get API key for provider."""
    config = load_llm_config()
    provider = provider.lower()
    
    if provider == "openai":
        return config["openai_api_key"]
    elif provider == "anthropic":
        return config["anthropic_api_key"]
    elif provider == "openrouter":
        return config["openrouter_api_key"]
    
    return None


def get_model(provider: str) -> str:
    """Get model name for provider."""
    config = load_llm_config()
    provider = provider.lower()
    
    if provider == "openai":
        return config["openai_model"]
    elif provider == "anthropic":
        return config["anthropic_model"]
    elif provider == "openrouter":
        return config.get("openrouter_model") or config["default_model"]
    
    return config["default_model"]


def call_llm(prompt: str, provider: Optional[str] = None, model: Optional[str] = None) -> Dict[str, Any]:
    """
    Call LLM API with prompt.
    
    Args:
        prompt: The prompt to send
        provider: LLM provider ("openai", "anthropic", "openrouter")
        model: Model name (optional, uses default if not provided)
        
    Returns:
        Dictionary with 'content', 'reasoning', 'raw_response'
    """
    config = load_llm_config()
    provider = (provider or config["default_provider"]).lower()
    model = model or get_model(provider)
    api_key = get_api_key(provider)
    
    if not api_key:
        return {
            "content": "",
            "reasoning": f"Error: No API key found for provider '{provider}'. Set {provider.upper()}_API_KEY environment variable.",
            "raw_response": "",
            "error": "missing_api_key"
        }
    
    try:
        if provider == "openai" or provider == "openrouter":
            return _call_openai_compatible(prompt, model, api_key, provider, config)
        elif provider == "anthropic":
            return _call_anthropic(prompt, model, api_key, config)
        else:
            return {
                "content": "",
                "reasoning": f"Error: Unknown provider '{provider}'",
                "raw_response": "",
                "error": "unknown_provider"
            }
    except Exception as e:
        return {
            "content": "",
            "reasoning": f"Error calling {provider} API: {str(e)}",
            "raw_response": "",
            "error": str(e)
        }


def _call_openai_compatible(prompt: str, model: str, api_key: str, provider: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Call OpenAI-compatible API (OpenAI or OpenRouter)."""
    try:
        import openai
    except ImportError:
        return {
            "content": "",
            "reasoning": "Error: openai package not installed. Install with: pip install openai",
            "raw_response": "",
            "error": "missing_package"
        }
    
    base_url = config.get("openai_base_url")
    if provider == "openrouter":
        base_url = config.get("openrouter_base_url", "https://openrouter.ai/api/v1")
    
    client = openai.OpenAI(
        api_key=api_key,
        base_url=base_url,
        timeout=config["api_timeout"]
    )
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert codebase analyzer. Analyze code and provide structured, accurate information."},
                {"role": "user", "content": prompt}
            ],
            temperature=config["temperature"],
            max_tokens=4000
        )
        
        content = response.choices[0].message.content
        return {
            "content": content or "",
            "reasoning": "Success",
            "raw_response": content or "",
            "error": None
        }
    except Exception as e:
        return {
            "content": "",
            "reasoning": f"Error calling {provider} API: {str(e)}",
            "raw_response": "",
            "error": str(e)
        }


def _call_anthropic(prompt: str, model: str, api_key: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Call Anthropic API."""
    try:
        import anthropic
    except ImportError:
        return {
            "content": "",
            "reasoning": "Error: anthropic package not installed. Install with: pip install anthropic",
            "raw_response": "",
            "error": "missing_package"
        }
    
    client = anthropic.Anthropic(api_key=api_key)
    
    try:
        response = client.messages.create(
            model=model,
            max_tokens=4000,
            temperature=config["temperature"],
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        content = response.content[0].text if response.content else ""
        return {
            "content": content,
            "reasoning": "Success",
            "raw_response": content,
            "error": None
        }
    except Exception as e:
        return {
            "content": "",
            "reasoning": f"Error calling Anthropic API: {str(e)}",
            "raw_response": "",
            "error": str(e)
        }
