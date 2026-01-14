# Configuration Guide

## Quick Start

1. **Copy the example configuration:**
   ```bash
   cd tests/validation
   cp env.example .env
   ```

2. **Edit `.env` and add your API key:**
   ```bash
   LLM_PROVIDER=openai
   OPENAI_API_KEY=sk-your-actual-api-key-here
   OPENAI_MODEL=gpt-4
   ```

3. **Install required packages:**
   ```bash
   pip install openai python-dotenv  # For OpenAI
   # or
   pip install anthropic python-dotenv  # For Anthropic
   ```

## Configuration Files

### Location
- **Example config**: `tests/validation/env.example`
- **Your config**: `tests/validation/.env` (create from env.example)
- **Config module**: `tests/validation/config.py`

### Environment Variables

The configuration system looks for these variables (in order of priority):
1. Environment variables (set in shell)
2. `.env` file in `tests/validation/` directory
3. `.env` file in project root (`dev/src/`)

## Configuration Options

### Required

- **`LLM_PROVIDER`**: Choose "openai" or "anthropic"
- **API Key**: Either `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` (depending on provider)

### Optional

- **`LLM_MODEL`**: Default model name (e.g., "gpt-4", "claude-3-5-sonnet-20241022")
- **`OPENAI_MODEL`**: OpenAI-specific model override
- **`ANTHROPIC_MODEL`**: Anthropic-specific model override
- **`OPENAI_BASE_URL`**: Custom OpenAI-compatible endpoint
- **`API_TIMEOUT`**: Request timeout in seconds (default: 60)
- **`MAX_RETRIES`**: Maximum retry attempts (default: 3)
- **`LLM_TEMPERATURE`**: Temperature for responses (default: 0.0 for consistency)

## Example Configurations

### OpenAI
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4
LLM_TEMPERATURE=0.0
```

### Anthropic
```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
LLM_TEMPERATURE=0.0
```

### Custom OpenAI Endpoint
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4
OPENAI_BASE_URL=https://api.custom-endpoint.com/v1
```

## Verification

Test your configuration:

```python
from tests.validation.config import validate_config

is_valid, missing = validate_config()
if is_valid:
    print("✅ Configuration is valid!")
else:
    print(f"❌ Missing: {', '.join(missing)}")
```

## Security Notes

- **Never commit `.env` files** to version control
- The `.env` file is already in `.gitignore`
- Use environment variables in CI/CD pipelines
- Rotate API keys regularly

