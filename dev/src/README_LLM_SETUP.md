# LLM Setup for Semantic Codebase Analysis

The `init-cursorworkspace` tool uses LLM/AI to semantically understand your codebase, not just parse files. This enables it to generate accurate, context-aware Cursor workspace files.

## Quick Setup

1. **Copy the example configuration:**
   ```bash
   cd dev/src
   cp .env.example .env
   ```

2. **Edit `.env` and add your API key:**
   ```bash
   LLM_PROVIDER=openai
   OPENAI_API_KEY=sk-your-actual-api-key-here
   OPENAI_MODEL=gpt-4
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Supported Providers

### OpenAI
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4
```

### Anthropic (Claude)
```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

### OpenRouter
```bash
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_MODEL=openai/gpt-4
```

### Local Models (Ollama, LM Studio)
```bash
LLM_PROVIDER=openai
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_API_KEY=ollama
OPENAI_MODEL=qwen2.5-coder:7b
```

## What LLM Analysis Does

The LLM-powered semantic analyzer:

1. **Understands code purpose** - Not just what files exist, but what the code actually does
2. **Identifies architecture** - Recognizes design patterns and architectural decisions
3. **Extracts domain knowledge** - Understands business logic and domain concepts
4. **Detects patterns** - Identifies coding patterns and conventions
5. **Generates context** - Creates rich projectFile.md with semantic understanding

## Fallback Behavior

If no LLM is configured, the tool will:
- Still work using static analyzers (file parsing, regex, AST)
- Show a warning that LLM analysis was skipped
- Generate workspace files based on static analysis only

## Cost Considerations

- **OpenAI GPT-4**: ~$0.03-0.06 per analysis (depends on codebase size)
- **Anthropic Claude**: ~$0.015-0.03 per analysis
- **OpenRouter**: Varies by model
- **Local Models**: Free, runs on your hardware

For most codebases, one analysis is sufficient as the results are cached in `projectFile.md`.
