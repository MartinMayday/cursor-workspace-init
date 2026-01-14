# How to Verify the Validation Tool is Working

## Quick Verification Steps

### 1. Check Results Are Being Generated

While tests are running, check if results are being saved:

```bash
cd /Volumes/uss/cloudworkspace/0_operator/1_Inbox/taskholder/th_cursor-workspace-init/dev/src/tests/validation

# Check if results directory exists and has files
ls -la results/

# Watch results being written (in another terminal)
watch -n 2 'ls -lh results/*.json 2>/dev/null | tail -5'
```

### 2. Inspect a Single Test Result

After at least one scenario completes, check a result file:

```bash
# Check baseline results (if any exist)
cat results/baseline_results.json | python3 -m json.tool | head -50

# Or check enhanced results
cat results/enhanced_results.json | python3 -m json.tool | head -50
```

**What to look for:**
- ✅ `scenario_id`: Should match test scenario
- ✅ `selected_files`: Array of files AI selected
- ✅ `expected_files`: Array of expected files
- ✅ `accuracy`: Percentage (0-100)
- ✅ `confidence`: AI's confidence level (0-100)
- ✅ `reasoning`: AI's explanation
- ✅ `raw_response`: Full AI response

### 3. Verify API Calls Are Real

Check if actual API calls are being made:

```bash
# Check the raw_response field - should contain actual AI responses
cat results/baseline_results.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
if data:
    first = data[0]
    print('Scenario:', first.get('scenario_id'))
    print('Raw Response Length:', len(first.get('raw_response', '')))
    print('Raw Response Preview:', first.get('raw_response', '')[:200])
    print('Selected Files:', first.get('selected_files', []))
    print('Accuracy:', first.get('accuracy', 0))
"
```

**What to look for:**
- ✅ `raw_response` should be substantial (not just "Placeholder response")
- ✅ `selected_files` should contain actual file names
- ✅ `reasoning` should explain the decision
- ✅ `confidence` should be a number between 0-100

### 4. Compare Baseline vs Enhanced

After both formats complete, compare:

```bash
python3 -c "
import json
from pathlib import Path

results_dir = Path('results')
baseline = json.load(open(results_dir / 'baseline_results.json')) if (results_dir / 'baseline_results.json').exists() else []
enhanced = json.load(open(results_dir / 'enhanced_results.json')) if (results_dir / 'enhanced_results.json').exists() else []

if baseline and enhanced:
    baseline_acc = sum(r.get('accuracy', 0) for r in baseline) / len(baseline)
    enhanced_acc = sum(r.get('accuracy', 0) for r in enhanced) / len(enhanced)
    
    print(f'Baseline Average Accuracy: {baseline_acc:.2f}%')
    print(f'Enhanced Average Accuracy: {enhanced_acc:.2f}%')
    print(f'Difference: {enhanced_acc - baseline_acc:+.2f}%')
    print(f'\nBaseline Tests: {len(baseline)}')
    print(f'Enhanced Tests: {len(enhanced)}')
else:
    print('Results not complete yet')
    print(f'Baseline: {len(baseline)} results')
    print(f'Enhanced: {len(enhanced)} results')
"
```

### 5. Verify Test Logic is Correct

Check that the tool is actually comparing correctly:

```bash
python3 -c "
import json
from pathlib import Path

# Load a test scenario
scenario = json.load(open('test_scenarios.json'))['scenarios'][0]
print('Test Scenario:', scenario['scenario_id'])
print('Expected Files:', scenario['expected_files'])

# Load corresponding manifest
baseline_manifest = json.load(open(f'baseline_manifests/{scenario[\"scenario_id\"]}.json'))
enhanced_manifest = json.load(open(f'enhanced_manifests/{scenario[\"scenario_id\"]}.json'))

print('\nBaseline Manifest Rules:', len(baseline_manifest.get('rules', [])))
print('Enhanced Manifest Rules:', len(enhanced_manifest.get('rules', [])))
print('\nBaseline has semantic_meaning?', any('semantic_meaning' in str(r) for r in baseline_manifest.get('rules', [])))
print('Enhanced has semantic_meaning?', any('semantic_meaning' in str(r) for r in enhanced_manifest.get('rules', [])))
"
```

## Signs It's Working Correctly

### ✅ Good Signs

1. **Results are being written**
   - Files appear in `results/` directory
   - Files grow over time
   - JSON is valid

2. **AI responses are real**
   - `raw_response` contains actual JSON from AI
   - `selected_files` contains file names
   - `reasoning` explains decisions
   - `confidence` is a reasonable number

3. **Comparisons make sense**
   - Baseline and enhanced results differ
   - Accuracy varies by scenario
   - Confidence levels are reasonable

4. **Test progression**
   - Scenarios complete in order
   - Both formats are tested
   - Multiple runs per scenario

### ❌ Warning Signs

1. **All results identical**
   - Same accuracy for all scenarios
   - Same confidence for all
   - Indicates caching or no real API calls

2. **Placeholder responses**
   - `raw_response` says "Placeholder response"
   - `selected_files` is always empty
   - API not actually being called

3. **Errors in results**
   - JSON parsing errors
   - Missing fields
   - Invalid data types

4. **No results generated**
   - Empty results directory
   - No files being created
   - Tests not actually running

## Manual Verification Test

Run a single test manually to verify:

```python
from pathlib import Path
from tests.validation.validation_runner import ValidationRunner
import json

# Setup
vd = Path('tests/validation')
runner = ValidationRunner(
    vd / 'test_scenarios.json',
    vd / 'baseline_manifests',
    vd / 'enhanced_manifests',
    vd / 'results'
)

# Load first scenario
scenarios = runner.load_scenarios()
scenario = scenarios[0]

# Run single test
print("Running single test...")
result = runner.run_single_test(scenario, "baseline", 1)

# Verify result structure
print("\nResult Structure:")
print(f"  Scenario ID: {result['scenario_id']}")
print(f"  Selected Files: {result['selected_files']}")
print(f"  Expected Files: {result['expected_files']}")
print(f"  Accuracy: {result['accuracy']:.2f}%")
print(f"  Confidence: {result['confidence']}")
print(f"  Decision Time: {result['decision_time']:.3f}s")
print(f"  Raw Response Length: {len(result['raw_response'])} chars")
print(f"  Raw Response Preview: {result['raw_response'][:200]}...")

# Check if it's a real response
if "Placeholder" in result['raw_response']:
    print("\n⚠️  WARNING: Placeholder response detected!")
else:
    print("\n✅ Real API response detected")
```

## Expected Behavior

### During Execution

1. **Progress indicators**
   - "Testing scenario_XX... ✓" messages
   - Progress through all 20 scenarios
   - Both baseline and enhanced formats

2. **Time per test**
   - Each test takes 2-10 seconds (API call time)
   - 400 tests = ~20-60 minutes total
   - Faster if API is quick

3. **Results accumulation**
   - Files grow as tests complete
   - JSON remains valid
   - No errors in output

### After Completion

1. **Result files exist**
   - `baseline_results.json` (200 results)
   - `enhanced_results.json` (200 results)
   - Both are valid JSON

2. **Results have variety**
   - Different accuracies per scenario
   - Different confidence levels
   - Different file selections

3. **Comparisons show differences**
   - Baseline vs enhanced differ
   - Enhanced should show improvement (if format works)
   - Statistical analysis possible

## Quick Check Script

Save this as `check_results.py`:

```python
#!/usr/bin/env python3
"""Quick check if validation is working."""

import json
from pathlib import Path

results_dir = Path('tests/validation/results')

print("=" * 60)
print("Validation Results Check")
print("=" * 60)

# Check files exist
baseline_file = results_dir / 'baseline_results.json'
enhanced_file = results_dir / 'enhanced_results.json'

for name, file in [("Baseline", baseline_file), ("Enhanced", enhanced_file)]:
    if file.exists():
        data = json.load(open(file))
        print(f"\n{name} Results:")
        print(f"  ✅ File exists: {len(data)} results")
        if data:
            avg_acc = sum(r.get('accuracy', 0) for r in data) / len(data)
            avg_conf = sum(r.get('confidence', 0) for r in data) / len(data)
            print(f"  Average Accuracy: {avg_acc:.2f}%")
            print(f"  Average Confidence: {avg_conf:.2f}%")
            
            # Check for real responses
            placeholder_count = sum(1 for r in data if "Placeholder" in r.get('raw_response', ''))
            if placeholder_count > 0:
                print(f"  ⚠️  WARNING: {placeholder_count} placeholder responses")
            else:
                print(f"  ✅ All responses appear real")
    else:
        print(f"\n{name} Results:")
        print(f"  ❌ File not found")

# Compare if both exist
if baseline_file.exists() and enhanced_file.exists():
    baseline = json.load(open(baseline_file))
    enhanced = json.load(open(enhanced_file))
    
    if baseline and enhanced:
        baseline_acc = sum(r.get('accuracy', 0) for r in baseline) / len(baseline)
        enhanced_acc = sum(r.get('accuracy', 0) for r in enhanced) / len(enhanced)
        
        print(f"\n{'=' * 60}")
        print("Comparison:")
        print(f"  Baseline: {baseline_acc:.2f}% accuracy")
        print(f"  Enhanced: {enhanced_acc:.2f}% accuracy")
        print(f"  Difference: {enhanced_acc - baseline_acc:+.2f}%")
        print(f"{'=' * 60}")
```

Run it:
```bash
cd /Volumes/uss/cloudworkspace/0_operator/1_Inbox/taskholder/th_cursor-workspace-init/dev/src
python3 tests/validation/check_results.py
```

