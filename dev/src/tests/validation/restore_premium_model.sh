#!/bin/bash
# Restore the premium model configuration

VALIDATION_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$VALIDATION_DIR/.env"
BACKUP_FILE="$VALIDATION_DIR/.env.premium_backup"

if [ -f "$BACKUP_FILE" ]; then
    cp "$BACKUP_FILE" "$ENV_FILE"
    echo "✅ Restored premium model configuration"
    echo "Model: openai/gpt-oss-120b:exacto"
else
    echo "❌ Backup file not found: $BACKUP_FILE"
    echo "Manually update .env with:"
    echo "  OPENROUTER_MODEL=openai/gpt-oss-120b:exacto"
    echo "  LLM_MODEL=openai/gpt-oss-120b:exacto"
fi

