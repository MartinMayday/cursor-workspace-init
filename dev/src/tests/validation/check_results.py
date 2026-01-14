#!/usr/bin/env python3
"""Quick check if validation is working."""

import json
from pathlib import Path

results_dir = Path(__file__).parent / 'results'

print("=" * 60)
print("Validation Results Check")
print("=" * 60)

# Check files exist
baseline_file = results_dir / 'baseline_results.json'
enhanced_file = results_dir / 'enhanced_results.json'

for name, file in [("Baseline", baseline_file), ("Enhanced", enhanced_file)]:
    if file.exists():
        try:
            data = json.load(open(file))
            print(f"\n{name} Results:")
            print(f"  ✅ File exists: {len(data)} results")
            if data:
                avg_acc = sum(r.get('accuracy', 0) for r in data) / len(data)
                avg_conf = sum(r.get('confidence', 0) for r in data) / len(data)
                print(f"  Average Accuracy: {avg_acc:.2f}%")
                print(f"  Average Confidence: {avg_conf:.2f}%")
                
                # Check for real responses
                placeholder_count = sum(1 for r in data if "Placeholder" in str(r.get('raw_response', '')))
                if placeholder_count > 0:
                    print(f"  ⚠️  WARNING: {placeholder_count} placeholder responses")
                else:
                    print(f"  ✅ All responses appear real")
                
                # Show sample result
                if data:
                    sample = data[0]
                    print(f"\n  Sample Result:")
                    print(f"    Scenario: {sample.get('scenario_id', 'N/A')}")
                    print(f"    Selected: {sample.get('selected_files', [])}")
                    print(f"    Expected: {sample.get('expected_files', [])}")
                    print(f"    Accuracy: {sample.get('accuracy', 0):.2f}%")
                    print(f"    Confidence: {sample.get('confidence', 0)}")
                    print(f"    Response Length: {len(str(sample.get('raw_response', '')))} chars")
        except Exception as e:
            print(f"  ❌ Error reading file: {e}")
    else:
        print(f"\n{name} Results:")
        print(f"  ❌ File not found (tests may still be running)")

# Compare if both exist
if baseline_file.exists() and enhanced_file.exists():
    try:
        baseline = json.load(open(baseline_file))
        enhanced = json.load(open(enhanced_file))
        
        if baseline and enhanced:
            baseline_acc = sum(r.get('accuracy', 0) for r in baseline) / len(baseline)
            enhanced_acc = sum(r.get('accuracy', 0) for r in enhanced) / len(enhanced)
            
            baseline_conf = sum(r.get('confidence', 0) for r in baseline) / len(baseline)
            enhanced_conf = sum(r.get('confidence', 0) for r in enhanced) / len(enhanced)
            
            print(f"\n{'=' * 60}")
            print("Comparison:")
            print(f"  Baseline: {baseline_acc:.2f}% accuracy, {baseline_conf:.2f}% confidence")
            print(f"  Enhanced: {enhanced_acc:.2f}% accuracy, {enhanced_conf:.2f}% confidence")
            print(f"  Accuracy Difference: {enhanced_acc - baseline_acc:+.2f}%")
            print(f"  Confidence Difference: {enhanced_conf - baseline_conf:+.2f}%")
            print(f"{'=' * 60}")
    except Exception as e:
        print(f"\nError comparing: {e}")

