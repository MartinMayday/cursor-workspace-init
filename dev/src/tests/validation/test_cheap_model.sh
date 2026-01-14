#!/bin/bash
# Script to test with a cheaper/non-premium model
# This helps validate if the enhanced manifest format works across different model capabilities

echo "================================================================================
Testing with Non-Premium Model
================================================================================
"

VALIDATION_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$VALIDATION_DIR/.env"

# Backup current config
if [ -f "$ENV_FILE" ]; then
    cp "$ENV_FILE" "$ENV_FILE.backup"
    echo "✅ Backed up current .env to .env.backup"
fi

# Suggested cheap models (in order of quality/price balance)
echo "Suggested non-premium models:"
echo "1. qwen/qwen-2-7b-instruct (very cheap, ~$0.01/1M tokens)"
echo "2. mistralai/mistral-7b-instruct (cheap, ~$0.10/1M tokens)"
echo "3. deepseek/deepseek-chat (good quality, ~$0.14/1M tokens)"
echo "4. google/gemini-2.0-flash-exp (good quality, ~$0.35/1M tokens)"
echo ""
read -p "Enter model number (1-4) or custom model name: " model_choice

case $model_choice in
    1)
        MODEL="qwen/qwen-2-7b-instruct"
        ;;
    2)
        MODEL="mistralai/mistral-7b-instruct"
        ;;
    3)
        MODEL="deepseek/deepseek-chat"
        ;;
    4)
        MODEL="google/gemini-2.0-flash-exp"
        ;;
    *)
        MODEL="$model_choice"
        ;;
esac

echo ""
echo "Selected model: $MODEL"
echo "Updating .env file..."

# Update .env file
if [ -f "$ENV_FILE" ]; then
    # Update or add OPENROUTER_MODEL
    if grep -q "OPENROUTER_MODEL=" "$ENV_FILE"; then
        sed -i.bak "s|OPENROUTER_MODEL=.*|OPENROUTER_MODEL=$MODEL|" "$ENV_FILE"
    else
        echo "OPENROUTER_MODEL=$MODEL" >> "$ENV_FILE"
    fi
    
    # Update or add LLM_MODEL
    if grep -q "LLM_MODEL=" "$ENV_FILE"; then
        sed -i.bak "s|LLM_MODEL=.*|LLM_MODEL=$MODEL|" "$ENV_FILE"
    else
        echo "LLM_MODEL=$MODEL" >> "$ENV_FILE"
    fi
    
    echo "✅ Updated .env with model: $MODEL"
else
    echo "❌ .env file not found. Please create it from env.example first."
    exit 1
fi

echo ""
echo "================================================================================
Ready to run validation tests
================================================================================
"
echo "Run the validation with:"
echo "  cd $(dirname "$VALIDATION_DIR")/.."
echo "  python3 tests/validation/run_validation.py"
echo ""
echo "When prompted, enter '1' for quick test (40 tests, ~5-10 min)"
echo "or '10' for full test (400 tests, ~20-60 min)"
echo ""
read -p "Run validation now? (y/n): " run_now

if [ "$run_now" = "y" ] || [ "$run_now" = "Y" ]; then
    cd "$(dirname "$VALIDATION_DIR")/.."
    python3 tests/validation/run_validation.py
fi

