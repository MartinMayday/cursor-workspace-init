#!/usr/bin/env python3
"""
Monitor validation tests in real-time.

Run this in a separate terminal to watch test progress.
"""

import json
import time
from pathlib import Path
from datetime import datetime

def monitor_results():
    """Monitor validation results as they're generated."""
    results_dir = Path(__file__).parent / 'results'
    baseline_file = results_dir / 'baseline_results.json'
    enhanced_file = results_dir / 'enhanced_results.json'
    
    print("=" * 70)
    print("Validation Test Monitor")
    print("=" * 70)
    print("Watching for results... (Press Ctrl+C to stop)\n")
    
    last_baseline_count = 0
    last_enhanced_count = 0
    
    try:
        while True:
            # Check baseline
            if baseline_file.exists():
                try:
                    baseline = json.load(open(baseline_file))
                    if len(baseline) > last_baseline_count:
                        new_count = len(baseline) - last_baseline_count
                        last_baseline_count = len(baseline)
                        
                        # Calculate stats
                        avg_acc = sum(r.get('accuracy', 0) for r in baseline) / len(baseline)
                        avg_conf = sum(r.get('confidence', 0) for r in baseline) / len(baseline)
                        
                        # Check for real responses
                        placeholder_count = sum(1 for r in baseline if "Placeholder" in str(r.get('raw_response', '')))
                        
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] Baseline: {len(baseline)} tests")
                        print(f"  Avg Accuracy: {avg_acc:.2f}% | Avg Confidence: {avg_conf:.2f}%")
                        if placeholder_count > 0:
                            print(f"  ⚠️  {placeholder_count} placeholder responses")
                        else:
                            print(f"  ✅ All real API responses")
                        print()
                except (json.JSONDecodeError, Exception) as e:
                    pass  # File might be incomplete
            
            # Check enhanced
            if enhanced_file.exists():
                try:
                    enhanced = json.load(open(enhanced_file))
                    if len(enhanced) > last_enhanced_count:
                        new_count = len(enhanced) - last_enhanced_count
                        last_enhanced_count = len(enhanced)
                        
                        # Calculate stats
                        avg_acc = sum(r.get('accuracy', 0) for r in enhanced) / len(enhanced)
                        avg_conf = sum(r.get('confidence', 0) for r in enhanced) / len(enhanced)
                        
                        # Check for real responses
                        placeholder_count = sum(1 for r in enhanced if "Placeholder" in str(r.get('raw_response', '')))
                        
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] Enhanced: {len(enhanced)} tests")
                        print(f"  Avg Accuracy: {avg_acc:.2f}% | Avg Confidence: {avg_conf:.2f}%")
                        if placeholder_count > 0:
                            print(f"  ⚠️  {placeholder_count} placeholder responses")
                        else:
                            print(f"  ✅ All real API responses")
                        print()
                except (json.JSONDecodeError, Exception) as e:
                    pass  # File might be incomplete
            
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
                        
                        print(f"{'=' * 70}")
                        print(f"Comparison (Baseline vs Enhanced):")
                        print(f"  Accuracy: {baseline_acc:.2f}% → {enhanced_acc:.2f}% ({enhanced_acc - baseline_acc:+.2f}%)")
                        print(f"  Confidence: {baseline_conf:.2f}% → {enhanced_conf:.2f}% ({enhanced_conf - baseline_conf:+.2f}%)")
                        print(f"{'=' * 70}\n")
                except Exception:
                    pass
            
            time.sleep(2)  # Check every 2 seconds
            
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")

if __name__ == "__main__":
    monitor_results()

