#!/usr/bin/env python3
"""
Test script to verify configuration and API connectivity.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tests.validation.config import load_config, validate_config, get_api_key, get_model

def test_config():
    """Test configuration loading and validation."""
    print("=" * 60)
    print("Configuration Test")
    print("=" * 60)
    
    # Load config
    config = load_config()
    print(f"\n✓ Configuration loaded")
    print(f"  Provider: {config['default_provider']}")
    print(f"  Default Model: {config['default_model']}")
    
    # Check provider-specific config
    provider = config['default_provider'].lower()
    if provider == 'openrouter':
        print(f"  OpenRouter Base URL: {config.get('openrouter_base_url', 'not set')}")
        print(f"  OpenRouter Model: {config.get('openrouter_model', 'not set')}")
        print(f"  OpenRouter API Key: {'SET' if config.get('openrouter_api_key') else 'NOT SET'}")
    elif provider == 'openai':
        print(f"  OpenAI Base URL: {config.get('openai_base_url', 'default')}")
        print(f"  OpenAI Model: {config.get('openai_model', 'not set')}")
        print(f"  OpenAI API Key: {'SET' if config.get('openai_api_key') else 'NOT SET'}")
    elif provider == 'anthropic':
        print(f"  Anthropic Model: {config.get('anthropic_model', 'not set')}")
        print(f"  Anthropic API Key: {'SET' if config.get('anthropic_api_key') else 'NOT SET'}")
    
    # Validate
    print(f"\n✓ Validating configuration...")
    is_valid, missing = validate_config()
    
    if is_valid:
        print(f"  ✅ Configuration is VALID")
        print(f"\n✓ Testing API key retrieval...")
        api_key = get_api_key(provider)
        model = get_model(provider)
        print(f"  API Key: {'SET' if api_key else 'NOT SET'}")
        print(f"  Model: {model}")
        
        # Test API call
        print(f"\n✓ Testing API connectivity...")
        test_api_call(provider, api_key, model)
    else:
        print(f"  ❌ Configuration is INVALID")
        print(f"  Missing: {', '.join(missing)}")
        print(f"\nTo fix:")
        print(f"  1. Create .env file: cp env.example .env")
        print(f"  2. Edit .env and set your API keys")
        print(f"  3. Or set environment variables")
        return False
    
    return True

def test_api_call(provider, api_key, model):
    """Test making an actual API call."""
    try:
        if provider == 'openrouter':
            import openai
            base_url = "https://openrouter.ai/api/v1"
            client = openai.OpenAI(api_key=api_key, base_url=base_url)
            
            print(f"  Calling OpenRouter API...")
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Say 'test' in JSON format: {\"test\": \"success\"}"}],
                response_format={"type": "json_object"},
                max_tokens=50
            )
            result = response.choices[0].message.content
            print(f"  ✅ API call successful!")
            print(f"  Response: {result[:100]}...")
            return True
            
        elif provider == 'openai':
            import openai
            client = openai.OpenAI(api_key=api_key)
            
            print(f"  Calling OpenAI API...")
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Say 'test'"}],
                max_tokens=10
            )
            result = response.choices[0].message.content
            print(f"  ✅ API call successful!")
            print(f"  Response: {result}")
            return True
            
        elif provider == 'anthropic':
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            
            print(f"  Calling Anthropic API...")
            response = client.messages.create(
                model=model,
                max_tokens=50,
                messages=[{"role": "user", "content": "Say 'test'"}]
            )
            result = response.content[0].text
            print(f"  ✅ API call successful!")
            print(f"  Response: {result}")
            return True
            
    except ImportError as e:
        print(f"  ❌ Missing package: {e}")
        print(f"  Install with: pip install openai  # or anthropic")
        return False
    except Exception as e:
        print(f"  ❌ API call failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_config()
    sys.exit(0 if success else 1)

