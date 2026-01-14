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
    
    Looks for .env in:
    1. Tool root directory (where cursor-workspace-init is installed)
    2. Current working directory (project being analyzed)
    3. dev/src directory relative to tool root
    
    Returns:
        Configuration dictionary
    """
    # Get tool root from environment variable (set by init-cursorworkspace.sh)
    tool_root = os.getenv("CURSOR_INIT_TOOL_ROOT")
    if tool_root:
        tool_root = Path(tool_root).resolve()
    else:
        # Fallback: try to find tool root by looking for dev/src
        current_file = Path(__file__).resolve()
        # If we're in dev/src/analyzers/, go up 3 levels
        if "dev" in current_file.parts and "src" in current_file.parts:
            tool_root = current_file.parent.parent.parent
        else:
            tool_root = None
    
    project_root = Path.cwd()
    
    # Build list of .env file locations to check (in priority order)
    env_files = []
    
    # 1. Tool root dev/src/.env (highest priority - tool's config)
    if tool_root:
        env_files.append(tool_root / "dev" / "src" / ".env")
        env_files.append(tool_root / ".env")
    
    # 2. Current file's directory (if running from tool directory)
    env_files.append(Path(__file__).parent.parent.parent / ".env")
    env_files.append(Path(__file__).parent.parent.parent / "dev" / "src" / ".env")
    
    # 3. Project root (target project being analyzed)
    env_files.append(project_root / ".env")
    env_files.append(project_root / "dev" / "src" / ".env")
    
    # Remove duplicates while preserving order
    seen = set()
    unique_env_files = []
    for env_file in env_files:
        if env_file not in seen:
            seen.add(env_file)
            unique_env_files.append(env_file)
    
    # Load first existing .env file
    for env_file in unique_env_files:
        if env_file.exists():
            if DOTENV_AVAILABLE:
                load_dotenv(env_file, override=False)  # Don't override existing env vars
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
    
    # If custom base URL is set, prefer OpenAI API key for compatibility
    if config.get("openai_base_url") and config.get("openai_api_key"):
        return config["openai_api_key"]
    
    if provider == "openai" or provider in ["zai", "custom"]:
        return config["openai_api_key"]
    elif provider == "anthropic":
        return config["anthropic_api_key"]
    elif provider == "openrouter":
        return config["openrouter_api_key"]
    
    # Fallback to OpenAI key if available
    return config.get("openai_api_key")


def get_model(provider: str) -> str:
    """Get model name for provider."""
    config = load_llm_config()
    provider = provider.lower()
    
    # If custom base URL is set, use OpenAI model setting
    if config.get("openai_base_url"):
        return config.get("openai_model") or config["default_model"]
    
    if provider == "openai" or provider in ["zai", "custom"]:
        return config["openai_model"]
    elif provider == "anthropic":
        return config["anthropic_model"]
    elif provider == "openrouter":
        return config.get("openrouter_model") or config["default_model"]
    
    # Fallback to default model
    return config["default_model"]


def call_llm(prompt: str, provider: Optional[str] = None, model: Optional[str] = None) -> Dict[str, Any]:
    """
    Call LLM API with prompt.
    
    Args:
        prompt: The prompt to send
        provider: LLM provider ("openai", "anthropic", "openrouter", or any OpenAI-compatible)
        model: Model name (optional, uses default if not provided)
        
    Returns:
        Dictionary with 'content', 'reasoning', 'raw_response'
    """
    config = load_llm_config()
    provider = (provider or config["default_provider"]).lower()
    model = model or get_model(provider)
    
    # Check for OpenAI-compatible endpoint (custom providers)
    openai_base_url = config.get("openai_base_url")
    openai_api_key = config.get("openai_api_key")
    
    # If custom base URL is set, use OpenAI-compatible API regardless of provider name
    if openai_base_url and openai_api_key:
        return _call_openai_compatible(prompt, model, openai_api_key, "openai", config)
    
    # Otherwise, use standard provider logic
    api_key = get_api_key(provider)
    
    if not api_key:
        return {
            "content": "",
            "reasoning": f"Error: No API key found for provider '{provider}'. Set {provider.upper()}_API_KEY environment variable.",
            "raw_response": "",
            "error": "missing_api_key"
        }
    
    try:
        if provider == "openai" or provider == "openrouter" or provider in ["zai", "custom"]:
            return _call_openai_compatible(prompt, model, api_key, provider, config)
        elif provider == "anthropic":
            return _call_anthropic(prompt, model, api_key, config)
        else:
            # Try OpenAI-compatible for unknown providers if we have OpenAI config
            if openai_api_key:
                return _call_openai_compatible(prompt, model, openai_api_key, provider, config)
            return {
                "content": "",
                "reasoning": f"Error: Unknown provider '{provider}'. Supported: openai, anthropic, openrouter, or use OPENAI_BASE_URL for custom endpoints.",
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
    """Call OpenAI-compatible API (OpenAI, OpenRouter, or custom endpoints)."""
    try:
        import openai
    except ImportError:
        return {
            "content": "",
            "reasoning": "Error: openai package not installed. Install with: pip install openai",
            "raw_response": "",
            "error": "missing_package"
        }
    
    # Determine base URL
    base_url = config.get("openai_base_url")
    if provider == "openrouter" and not base_url:
        base_url = config.get("openrouter_base_url", "https://openrouter.ai/api/v1")
    elif not base_url:
        base_url = "https://api.openai.com/v1"  # Default OpenAI endpoint
    
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
