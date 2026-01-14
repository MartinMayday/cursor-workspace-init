# Manifest Format Validation Testing

## Overview

This directory contains the validation testing infrastructure for comparing baseline (current) and enhanced (proposed) manifest formats. The enhanced format includes additional fields (`semantic_meaning`, `use_when`, `conditions`, `triggers`) to enable AI agents to make context block decisions with higher certainty.

## Quick Start

### 1. Configure API Keys

Copy the example environment file and fill in your API keys:

```bash
cd tests/validation
cp env.example .env
# Edit .env with your API keys
```

### 2. Run Validation Tests

```bash
# From the dev/src directory
python3 tests/validation/run_validation.py
```

When prompted, enter the number of runs per scenario:
- **1** for quick test (40 total tests, ~5-10 minutes)
- **10** for full validation (400 total tests, ~20-60 minutes)

### 3. Analyze Results

```bash
python3 tests/validation/results_analyzer.py
```

### 4. Generate Reports

```bash
python3 tests/validation/report_generator.py
```

Reports will be saved to `tests/validation/reports/`:
- `validation_report.md` - Markdown report
- `validation_report.json` - JSON report

## Important: Use `python3`

**Always use `python3` instead of `python`** to ensure you're using Python 3.x:

```bash
# ✅ Correct
python3 tests/validation/run_validation.py

# ❌ May fail (could be Python 2.x)
python tests/validation/run_validation.py
```

## Directory Structure

```
tests/validation/
├── __init__.py
├── config.py                    # Configuration loader
├── validation_runner.py          # Main test runner
├── results_analyzer.py            # Results analysis
├── report_generator.py            # Report generation
├── manifest_generator.py          # Manifest file generator
├── test_scenarios.json            # Test scenarios
├── test_scenario_schema.json      # Schema for scenarios
├── baseline_manifests/            # Baseline format manifests
├── enhanced_manifests/            # Enhanced format manifests
├── results/                       # Test results (JSON)
│   ├── baseline_results.json
│   ├── enhanced_results.json
│   └── comparison.json
├── reports/                       # Generated reports
│   ├── validation_report.md
│   └── validation_report.json
├── ground_truth/                  # Expert validations (optional)
├── env.example                     # Example environment file
├── .env                           # Your API keys (create from env.example)
├── check_results.py               # Quick results checker
├── monitor_tests.py               # Real-time test monitor
├── test_config.py                 # Configuration tester
├── run_validation.py              # Interactive test runner
├── HOW_TO_VERIFY.md               # Verification guide
├── VERIFY_IT_WORKS.md             # Detailed verification steps
├── WHAT_IT_DOES.md                # Purpose and methodology
├── CONFIGURATION.md                # Configuration guide
└── CREDIBILITY.md                  # Tool transparency
```

## Configuration

### Supported LLM Providers

- **OpenAI**: Set `OPENAI_API_KEY` and `OPENAI_MODEL`
- **Anthropic**: Set `ANTHROPIC_API_KEY` and `ANTHROPIC_MODEL`
- **OpenRouter**: Set `OPENROUTER_API_KEY` and `OPENROUTER_MODEL`

### Environment Variables

See `env.example` for all available configuration options:

```bash
# Provider selection
LLM_PROVIDER=openrouter  # or "openai" or "anthropic"
LLM_MODEL=openai/gpt-oss-120b:exacto

# API Keys
OPENROUTER_API_KEY=your_key_here
# ... other provider keys
```

## Test Scenarios

The validation uses 20 diverse test scenarios:

- **Simple (5)**: Single project type, single language
- **Medium (7)**: Multiple frameworks, deployment types
- **Complex (5)**: Missing context, partial information
- **Edge Cases (3)**: Unknown project types, missing languages

## Success Criteria

**Primary Criteria:**
- Enhanced format achieves ≥98% accuracy in file selection
- Enhanced format achieves ≥98% confidence level from AI agents
- Enhanced format reduces clarification requests to zero
- Enhanced format maintains or improves decision speed

## Monitoring Tests

### Real-Time Monitoring

In a separate terminal, run:

```bash
python3 tests/validation/monitor_tests.py
```

This shows:
- Test count updates in real-time
- Average accuracy and confidence
- Comparison between baseline and enhanced
- Warnings if placeholder responses detected

### Check Current Status

```bash
python3 tests/validation/check_results.py
```

## Results Interpretation

### Key Metrics

- **Accuracy**: Percentage of correct file selections
- **Confidence**: AI agent's confidence level (0-100)
- **Clarification Requests**: Number of times AI asked for clarification
- **Decision Time**: Time taken for AI to make decision

### What Good Results Look Like

✅ **Good Signs:**
- Enhanced format shows higher accuracy than baseline
- Enhanced format shows higher confidence than baseline
- Zero clarification requests
- Consistent results (low standard deviation)

❌ **Warning Signs:**
- All results identical (possible caching)
- "Placeholder response" in raw_response (API not working)
- No results files (tests not running)

## Troubleshooting

### "KeyError: 't_statistic'"

This error occurs when scipy is not available. The tool will still work but will skip statistical tests. Install scipy if needed:

```bash
pip3 install scipy numpy
```

### "No API key configured"

Make sure you've created `.env` from `env.example` and filled in your API keys.

### "ModuleNotFoundError"

Install required dependencies:

```bash
pip3 install openai python-dotenv
```

Optional (for statistical tests):
```bash
pip3 install scipy numpy
```

## Understanding the Results

### Example Output

```
Baseline Results:
  ✅ File exists: 20 results
  Average Accuracy: 98.33%
  Average Confidence: 96.70%

Enhanced Results:
  ✅ File exists: 20 results
  Average Accuracy: 100.00%
  Average Confidence: 98.70%

Comparison:
  Baseline: 98.33% accuracy, 96.70% confidence
  Enhanced: 100.00% accuracy, 98.70% confidence
  Accuracy Difference: +1.67%
  Confidence Difference: +2.00%
```

### Report Files

- **validation_report.md**: Human-readable Markdown report
- **validation_report.json**: Machine-readable JSON report
- **comparison.json**: Detailed comparison data

## Next Steps

After validation completes:

1. Review the generated reports in `reports/`
2. Check if enhanced format meets success criteria
3. If successful, consider adopting enhanced format
4. If not, refine manifest format based on results

## Additional Resources

- `WHAT_IT_DOES.md` - Detailed explanation of purpose and methodology
- `HOW_TO_VERIFY.md` - How to verify the tool is working correctly
- `VERIFY_IT_WORKS.md` - Comprehensive verification guide
- `CONFIGURATION.md` - Configuration reference
- `CREDIBILITY.md` - Tool transparency and methodology
