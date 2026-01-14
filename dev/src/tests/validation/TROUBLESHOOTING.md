# Troubleshooting Guide

## Common Issues

### Issue: 0% Accuracy, 0 Files Selected

**Symptoms:**
- Tests complete very quickly (seconds)
- All results show 0% accuracy, 0% confidence, 0 files
- Raw response contains error messages

**Causes & Solutions:**

#### 1. OpenRouter Data Policy Error

**Error Message:**
```
API error: Error code: 404 - {'error': {'message': 'No endpoints found matching your data policy (Paid model training). Configure: https://openrouter.ai/settings/privacy', 'code': 404}}
```

**Solution:**
- Visit https://openrouter.ai/settings/privacy
- Enable "Paid model training" or adjust your data policy settings
- Some models require specific data policy configurations

**Alternative:** Use a model that doesn't require special settings:
- `google/gemini-2.0-flash-exp` (recommended)
- `mistralai/mistral-7b-instruct`
- `qwen/qwen-2-7b-instruct`

#### 2. Invalid API Key

**Error Message:**
```
API error: Error code: 401 - Unauthorized
```

**Solution:**
- Check your `.env` file has correct `OPENROUTER_API_KEY`
- Verify the key is active on OpenRouter
- Regenerate key if needed

#### 3. Model Not Available

**Error Message:**
```
API error: Error code: 404 - Model not found
```

**Solution:**
- Check model name is correct (case-sensitive)
- Verify model is available on OpenRouter
- Try a different model

#### 4. Rate Limiting

**Error Message:**
```
API error: Error code: 429 - Rate limit exceeded
```

**Solution:**
- Wait a few minutes and retry
- Reduce number of runs per scenario
- Upgrade OpenRouter plan if needed

### Issue: Tests Take Too Long

**Symptoms:**
- Tests running for hours
- Very slow API responses

**Solutions:**
- Use faster models (e.g., `google/gemini-2.0-flash-exp`)
- Reduce runs per scenario (use 1 instead of 10)
- Check network connection
- Verify API endpoint is accessible

### Issue: Inconsistent Results

**Symptoms:**
- Results vary significantly between runs
- High standard deviation

**Solutions:**
- Increase number of runs per scenario (10+)
- Use more capable models
- Check if model supports deterministic responses
- Verify temperature setting (should be low, e.g., 0.0-0.1)

### Issue: JSON Parsing Errors

**Symptoms:**
- Errors in parsing AI responses
- Invalid JSON in raw_response

**Solutions:**
- Model may not be following JSON format requirement
- Try a different model
- Check raw_response field for actual response
- May need to adjust prompt to be more explicit about JSON format

## Debugging Steps

### 1. Check Raw API Response

```bash
python3 -c "
import json
from pathlib import Path

results_file = Path('tests/validation/results/baseline_results.json')
if results_file.exists():
    data = json.load(open(results_file))
    if data:
        print('Raw Response:', data[0].get('raw_response', '')[:500])
"
```

### 2. Test API Connection

```bash
python3 tests/validation/test_config.py
```

### 3. Verify Configuration

```bash
cd tests/validation
cat .env | grep -E "LLM_PROVIDER|LLM_MODEL|OPENROUTER"
```

### 4. Test Single API Call

```python
from tests.validation.validation_runner import ValidationRunner
from pathlib import Path
import json

vd = Path('tests/validation')
runner = ValidationRunner(
    vd / 'test_scenarios.json',
    vd / 'baseline_manifests',
    vd / 'enhanced_manifests',
    vd / 'results'
)

scenarios = runner.load_scenarios()
result = runner.run_single_test(scenarios[0], 'baseline', 1)
print(json.dumps(result, indent=2))
```

## Model Recommendations

### For Testing (Cheap & Fast)
- `google/gemini-2.0-flash-exp` - Good quality, fast, ~$0.35/1M tokens
- `mistralai/mistral-7b-instruct` - Cheap, ~$0.10/1M tokens
- `qwen/qwen-2-7b-instruct` - Very cheap, ~$0.01/1M tokens

### For Production Validation (High Quality)
- `openai/gpt-oss-120b:exacto` - Premium, high quality
- `anthropic/claude-3-5-sonnet` - Premium, excellent reasoning
- `google/gemini-2.0-flash-exp` - Good balance of quality/price

## Getting Help

1. Check raw_response field in results for actual error messages
2. Verify OpenRouter account settings at https://openrouter.ai/settings
3. Review model availability at https://openrouter.ai/models
4. Check OpenRouter documentation for API requirements

