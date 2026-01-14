# Quick Start Guide

## Run Validation Tests

You're already configured! Here's how to run the tests:

### Option 1: Interactive Script (Recommended)

```bash
cd /Volumes/uss/cloudworkspace/0_operator/1_Inbox/taskholder/th_cursor-workspace-init/dev/src
python3 tests/validation/run_validation.py
```

This will:
- ✅ Validate your configuration
- ✅ Ask how many runs per scenario (start with 1 for quick test)
- ✅ Run all tests automatically
- ✅ Save results to `results/` directory

### Option 2: Direct Python Command

```bash
cd /Volumes/uss/cloudworkspace/0_operator/1_Inbox/taskholder/th_cursor-workspace-init/dev/src
python3 -c "
from tests.validation.validation_runner import ValidationRunner
from pathlib import Path

vd = Path('tests/validation')
runner = ValidationRunner(
    vd / 'test_scenarios.json',
    vd / 'baseline_manifests',
    vd / 'enhanced_manifests',
    vd / 'results'
)
runner.run_all_tests(num_runs=1)  # Start with 1 run
"
```

### Option 3: Python Script

Create a file `run_tests.py`:

```python
from tests.validation.validation_runner import ValidationRunner
from pathlib import Path

vd = Path('tests/validation')
runner = ValidationRunner(
    vd / 'test_scenarios.json',
    vd / 'baseline_manifests',
    vd / 'enhanced_manifests',
    vd / 'results'
)
runner.run_all_tests(num_runs=1)  # Change to 10 for full validation
```

Then run:
```bash
python3 run_tests.py
```

## Test Configuration

- **Quick Test**: `num_runs=1` → 40 total tests (20 baseline + 20 enhanced)
- **Full Validation**: `num_runs=10` → 400 total tests (200 baseline + 200 enhanced)

## After Running Tests

1. **Analyze Results**:
   ```bash
   python3 tests/validation/results_analyzer.py
   ```

2. **Generate Reports**:
   ```bash
   python3 tests/validation/report_generator.py
   ```

3. **View Reports**:
   - Markdown: `tests/validation/reports/validation_report.md`
   - JSON: `tests/validation/reports/validation_report.json`

## Current Configuration

✅ Provider: openrouter  
✅ Model: openai/gpt-oss-120b:exacto  
✅ API Key: Configured  
✅ Ready to run!

