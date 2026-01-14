# Model Comparison Testing

## Purpose

Test the enhanced manifest format with non-premium/cheaper models to validate that the format works across different model capabilities, not just premium frontier models.

## Current Model

**Premium Model (Previous Test):**
- Model: `openai/gpt-oss-120b:exacto`
- Results: 100% accuracy, 98.70% confidence
- Cost: Higher (premium model)

## Suggested Non-Premium Models

### Option 1: Very Cheap (Recommended for Cost Testing)
- **Model**: `qwen/qwen-2-7b-instruct`
- **Cost**: ~$0.01 per 1M tokens
- **Quality**: Lower but functional
- **Use Case**: Test if format works with minimal capability models

### Option 2: Cheap & Balanced
- **Model**: `mistralai/mistral-7b-instruct`
- **Cost**: ~$0.10 per 1M tokens
- **Quality**: Good for its price
- **Use Case**: Test with mid-tier model

### Option 3: Good Quality & Still Cheap
- **Model**: `deepseek/deepseek-chat`
- **Cost**: ~$0.14 per 1M tokens
- **Quality**: Very good, competitive with premium
- **Use Case**: Test with high-quality but affordable model

### Option 4: Premium-Like but Cheaper
- **Model**: `google/gemini-2.0-flash-exp`
- **Cost**: ~$0.35 per 1M tokens
- **Quality**: Excellent, near-premium
- **Use Case**: Test with high-quality but lower-cost model

## Quick Test Setup

### Method 1: Use the Script

```bash
cd /Volumes/uss/cloudworkspace/0_operator/1_Inbox/taskholder/th_cursor-workspace-init/dev/src
./tests/validation/test_cheap_model.sh
```

### Method 2: Manual Update

Edit `tests/validation/.env`:

```bash
# Change these lines:
OPENROUTER_MODEL=qwen/qwen-2-7b-instruct  # or your chosen model
LLM_MODEL=qwen/qwen-2-7b-instruct
```

## Running the Test

```bash
cd /Volumes/uss/cloudworkspace/0_operator/1_Inbox/taskholder/th_cursor-workspace-init/dev/src
python3 tests/validation/run_validation.py
# When prompted, enter: 1  (for quick test with 1 run per scenario)
```

## Expected Outcomes

### If Enhanced Format is Robust:
- ✅ Non-premium model should still achieve >90% accuracy
- ✅ Enhanced format should outperform baseline even with cheaper model
- ✅ Results may be slightly lower but still demonstrate format value

### If Results are Much Worse:
- ⚠️ May indicate format relies too heavily on model capabilities
- ⚠️ May need to simplify format or add more explicit guidance
- ⚠️ Consider format refinements for broader model compatibility

## Comparing Results

After running with the cheaper model, compare:

```bash
# View current results
python3 tests/validation/check_results.py

# Compare with previous premium model results
python3 tests/validation/compare_models.py
```

## Success Criteria for Non-Premium Model

**Minimum Acceptable:**
- Enhanced format accuracy ≥90% (vs baseline)
- Enhanced format confidence ≥85%
- Enhanced format still outperforms baseline

**Ideal:**
- Enhanced format accuracy ≥95%
- Enhanced format confidence ≥90%
- Clear improvement over baseline (even if lower than premium model)

## Cost Comparison

For 400 tests (20 scenarios × 10 runs × 2 formats):

| Model | Cost per 1M tokens | Estimated Cost |
|-------|---------------------|----------------|
| Premium (gpt-oss-120b) | ~$2.00 | ~$0.50-1.00 |
| Gemini 2.0 Flash | ~$0.35 | ~$0.10-0.20 |
| DeepSeek Chat | ~$0.14 | ~$0.03-0.05 |
| Mistral 7B | ~$0.10 | ~$0.02-0.04 |
| Qwen 2 7B | ~$0.01 | ~$0.002-0.005 |

## Restoring Original Model

To restore the premium model:

```bash
cd /Volumes/uss/cloudworkspace/0_operator/1_Inbox/taskholder/th_cursor-workspace-init/dev/src/tests/validation
cp .env.backup .env
```

Or manually edit `.env` and change back to:
```
OPENROUTER_MODEL=openai/gpt-oss-120b:exacto
LLM_MODEL=openai/gpt-oss-120b:exacto
```

