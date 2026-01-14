#!/usr/bin/env python3
"""
Compare validation results across different LLM models.

This script helps test if the enhanced manifest format works
across different model capabilities (premium vs non-premium).
"""

import json
from pathlib import Path
from datetime import datetime

def compare_model_results(results_dir: Path):
    """Compare results from different model runs."""
    results_dir = Path(results_dir)
    
    # Look for results files
    baseline_file = results_dir / "baseline_results.json"
    enhanced_file = results_dir / "enhanced_results.json"
    
    if not baseline_file.exists() or not enhanced_file.exists():
        print("❌ Results files not found. Run validation tests first.")
        return
    
    baseline = json.load(open(baseline_file))
    enhanced = json.load(open(enhanced_file))
    
    print("=" * 70)
    print("Model Comparison Summary")
    print("=" * 70)
    print(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Calculate metrics
    baseline_acc = sum(r.get('accuracy', 0) for r in baseline) / len(baseline) if baseline else 0
    enhanced_acc = sum(r.get('accuracy', 0) for r in enhanced) / len(enhanced) if enhanced else 0
    
    baseline_conf = sum(r.get('confidence', 0) for r in baseline) / len(baseline) if baseline else 0
    enhanced_conf = sum(r.get('confidence', 0) for r in enhanced) / len(enhanced) if enhanced else 0
    
    baseline_std = calculate_std([r.get('accuracy', 0) for r in baseline]) if baseline else 0
    enhanced_std = calculate_std([r.get('accuracy', 0) for r in enhanced]) if enhanced else 0
    
    print("BASELINE FORMAT:")
    print(f"  Accuracy: {baseline_acc:.2f}% (±{baseline_std:.2f}%)")
    print(f"  Confidence: {baseline_conf:.2f}%")
    print(f"  Tests: {len(baseline)}")
    
    print("\nENHANCED FORMAT:")
    print(f"  Accuracy: {enhanced_acc:.2f}% (±{enhanced_std:.2f}%)")
    print(f"  Confidence: {enhanced_conf:.2f}%")
    print(f"  Tests: {len(enhanced)}")
    
    print("\nIMPROVEMENT:")
    print(f"  Accuracy: {enhanced_acc - baseline_acc:+.2f}%")
    print(f"  Confidence: {enhanced_conf - baseline_conf:+.2f}%")
    print(f"  Consistency: {baseline_std - enhanced_std:+.2f}% (lower is better)")
    
    # Success criteria
    print("\n" + "=" * 70)
    print("SUCCESS CRITERIA:")
    print("=" * 70)
    print(f"  Accuracy ≥98%: {'✓ PASS' if enhanced_acc >= 98 else '✗ FAIL'} ({enhanced_acc:.2f}%)")
    print(f"  Confidence ≥98%: {'✓ PASS' if enhanced_conf >= 98 else '✗ FAIL'} ({enhanced_conf:.2f}%)")
    print(f"  Enhanced > Baseline: {'✓ PASS' if enhanced_acc > baseline_acc else '✗ FAIL'}")
    
    # Model info (if available in results)
    if baseline:
        sample = baseline[0]
        if 'model' in sample:
            print(f"\nModel Used: {sample.get('model', 'Unknown')}")
    
    print("\n" + "=" * 70)

def calculate_std(values):
    """Calculate standard deviation."""
    if not values or len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    return variance ** 0.5

if __name__ == "__main__":
    validation_dir = Path(__file__).parent
    results_dir = validation_dir / "results"
    compare_model_results(results_dir)

