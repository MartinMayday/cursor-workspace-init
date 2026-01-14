# Local Models for Mac Studio M1 Max

## Overview

For running validation tests locally on your Mac Studio M1 Max, you can use local models via Ollama, LM Studio, or similar tools. This is **completely free** and runs entirely on your hardware.

## Recommended Local Models for M1 Max

### Option 1: Ollama (Recommended)

**Installation:**
```bash
# Install Ollama
brew install ollama
# or download from https://ollama.ai

# Start Ollama service
ollama serve
```

**Recommended Models for Validation:**

#### 1. **Qwen2.5 Coder 7B** (Best Balance)
```bash
ollama pull qwen2.5-coder:7b
```
- **Size:** ~4.5GB
- **Performance:** Excellent for code-related tasks
- **Speed:** Fast on M1 Max
- **Expected:** Similar to cloud qwen2.5-coder-7b (100% accuracy with enhanced format)

#### 2. **Llama 3.2 3B** (Fastest)
```bash
ollama pull llama3.2:3b
```
- **Size:** ~2GB
- **Performance:** Good, fast inference
- **Speed:** Very fast on M1 Max
- **Expected:** Similar to cloud llama-3.2-3b (91.67% accuracy with enhanced format)

#### 3. **Mistral 7B** (Good Quality)
```bash
ollama pull mistral:7b
```
- **Size:** ~4.1GB
- **Performance:** High quality
- **Speed:** Fast on M1 Max
- **Expected:** Good results with enhanced format

#### 4. **DeepSeek Coder 6.7B** (Code-Focused)
```bash
ollama pull deepseek-coder:6.7b
```
- **Size:** ~3.8GB
- **Performance:** Excellent for code
- **Speed:** Fast on M1 Max
- **Expected:** Very good with enhanced format

### Option 2: LM Studio

**Installation:**
- Download from https://lmstudio.ai
- GUI-based, easy to use
- Supports same models as Ollama

**Usage:**
1. Download model in LM Studio
2. Start local server
3. Use API endpoint in validation config

## Configuration for Local Models

### Using Ollama with Validation Tool

1. **Start Ollama:**
```bash
ollama serve
```

2. **Update `.env` file:**
```bash
# Use OpenAI-compatible API (Ollama provides this)
LLM_PROVIDER=openai
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_API_KEY=ollama  # Ollama doesn't require real key
OPENAI_MODEL=qwen2.5-coder:7b  # or your chosen model
```

3. **Test connection:**
```bash
python3 tests/validation/test_config.py
```

### Using LM Studio

1. **Start LM Studio server:**
   - Open LM Studio
   - Load your model
   - Start local server (usually port 1234)

2. **Update `.env` file:**
```bash
LLM_PROVIDER=openai
OPENAI_BASE_URL=http://localhost:1234/v1
OPENAI_API_KEY=lm-studio  # LM Studio doesn't require real key
OPENAI_MODEL=your-model-name
```

## Model Recommendations by Use Case

### For Best Accuracy (Recommended)
- **Qwen2.5 Coder 7B** - Best balance of quality and speed
- **DeepSeek Coder 6.7B** - Excellent for code-related tasks

### For Fast Testing
- **Llama 3.2 3B** - Fastest, good enough for quick tests
- **Mistral 7B** - Fast and high quality

### For Maximum Quality
- **Llama 3.1 8B** - Higher quality, slower
- **Qwen2.5 14B** - Best quality, requires more RAM

## Performance on M1 Max

### Expected Speeds (approximate)

| Model | Size | Inference Speed | RAM Usage |
|-------|------|----------------|-----------|
| Llama 3.2 3B | 2GB | ~50-100 tokens/s | ~4GB |
| Qwen2.5 Coder 7B | 4.5GB | ~30-60 tokens/s | ~8GB |
| Mistral 7B | 4.1GB | ~30-60 tokens/s | ~8GB |
| DeepSeek Coder 6.7B | 3.8GB | ~35-70 tokens/s | ~7GB |

**Note:** M1 Max has 32GB or 64GB unified memory, so all these models will run comfortably.

## Cost Comparison

| Option | Cost | Speed | Quality |
|--------|------|-------|---------|
| **Local (Ollama)** | **FREE** | Fast (no network) | High |
| Cloud (OpenRouter) | $0.01-$2.00/1M tokens | Depends on network | High |

**Local is completely free** - no API costs, no rate limits, unlimited usage!

## Setup Instructions

### Quick Start with Ollama

```bash
# 1. Install Ollama
brew install ollama

# 2. Start Ollama service
ollama serve

# 3. Pull a model (in another terminal
ollama pull qwen2.5-coder:7b

# 4. Update validation .env
cd tests/validation
cat > .env.local <<EOF
LLM_PROVIDER=openai
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_API_KEY=ollama
OPENAI_MODEL=qwen2.5-coder:7b
LLM_TEMPERATURE=0.1
EOF

# 5. Test
python3 test_config.py
```

### Running Validation with Local Model

```bash
# Use the local config
export $(cat tests/validation/.env.local | xargs)

# Run validation
python3 tests/validation/run_validation.py
```

## Advantages of Local Models

1. **Free** - No API costs
2. **Fast** - No network latency
3. **Private** - Data never leaves your machine
4. **Unlimited** - No rate limits
5. **Offline** - Works without internet

## Disadvantages

1. **RAM Usage** - Models use 4-8GB RAM
2. **Initial Download** - Models are 2-8GB to download
3. **Setup Required** - Need to install Ollama/LM Studio

## Expected Results with Local Models

Based on cloud testing, local models should perform similarly:

- **Qwen2.5 Coder 7B:** ~100% accuracy with enhanced format
- **Llama 3.2 3B:** ~91% accuracy with enhanced format
- **Mistral 7B:** ~95-100% accuracy with enhanced format

## Troubleshooting

### Model Not Found
```bash
# List available models
ollama list

# Pull the model
ollama pull model-name
```

### Connection Refused
```bash
# Make sure Ollama is running
ollama serve

# Check if port is correct
curl http://localhost:11434/api/tags
```

### Out of Memory
- Use smaller model (3B instead of 7B)
- Close other applications
- M1 Max should handle up to 14B models comfortably

## Next Steps

1. **Install Ollama:** `brew install ollama`
2. **Pull a model:** `ollama pull qwen2.5-coder:7b`
3. **Configure validation tool** to use local endpoint
4. **Run validation tests** - completely free!

---

*Local models are perfect for development, testing, and unlimited validation runs without any API costs!*

