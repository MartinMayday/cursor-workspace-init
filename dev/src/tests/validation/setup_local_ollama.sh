#!/bin/bash
# Quick setup script for local Ollama models on M1 Max

echo "================================================================================
Local Ollama Setup for Mac Studio M1 Max
================================================================================
"

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama not found. Install with:"
    echo "   brew install ollama"
    echo "   or download from https://ollama.ai"
    exit 1
fi

echo "✅ Ollama found"

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  Ollama not running. Starting..."
    echo "   Run 'ollama serve' in another terminal, then press Enter"
    read
fi

echo ""
echo "Available models:"
ollama list

echo ""
echo "Recommended models for validation:"
echo "  1. qwen2.5-coder:7b  (Best balance - ~4.5GB)"
echo "  2. llama3.2:3b      (Fastest - ~2GB)"
echo "  3. mistral:7b       (High quality - ~4.1GB)"
echo "  4. deepseek-coder:6.7b (Code-focused - ~3.8GB)"
echo ""

read -p "Enter model name to pull (or press Enter to skip): " model_name

if [ -n "$model_name" ]; then
    echo "Pulling $model_name..."
    ollama pull "$model_name"
    echo "✅ Model pulled"
fi

echo ""
echo "Creating local .env file..."

cat > .env.local <<ENVEOF
# Local Ollama Configuration
LLM_PROVIDER=openai
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_API_KEY=ollama
OPENAI_MODEL=${model_name:-qwen2.5-coder:7b}
LLM_TEMPERATURE=0.1
API_TIMEOUT=120
MAX_RETRIES=3
ENVEOF

echo "✅ Created .env.local"
echo ""
echo "To use local model:"
echo "  1. Copy .env.local to .env: cp .env.local .env"
echo "  2. Make sure Ollama is running: ollama serve"
echo "  3. Run validation: python3 run_validation.py"
