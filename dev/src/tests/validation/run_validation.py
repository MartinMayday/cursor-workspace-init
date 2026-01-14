#!/usr/bin/env python3
"""
Run validation tests.

This script runs the full validation test suite.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tests.validation.validation_runner import ValidationRunner
from tests.validation.config import validate_config

def main():
    """Run validation tests."""
    print("=" * 80)
    print("Manifest Format Validation Testing")
    print("=" * 80)
    
    # Validate configuration first
    print("\n1. Validating configuration...")
    is_valid, missing = validate_config()
    if not is_valid:
        print(f"❌ Configuration Error:")
        print(f"   Missing: {', '.join(missing)}")
        print(f"\nPlease configure your API keys in .env file")
        return 1
    
    print("   ✅ Configuration valid")
    
    # Setup paths
    validation_dir = Path(__file__).parent
    scenarios_path = validation_dir / "test_scenarios.json"
    baseline_dir = validation_dir / "baseline_manifests"
    enhanced_dir = validation_dir / "enhanced_manifests"
    results_dir = validation_dir / "results"
    
    # Create runner
    print("\n2. Initializing validation runner...")
    runner = ValidationRunner(scenarios_path, baseline_dir, enhanced_dir, results_dir)
    print(f"   Provider: {runner.provider}")
    print(f"   Model: {runner.config.get('openrouter_model') or runner.config.get('default_model')}")
    
    # Ask for number of runs
    print("\n3. Test configuration:")
    try:
        num_runs = int(input("   Number of runs per scenario (default: 10, recommended: 1 for quick test): ") or "1")
    except (ValueError, KeyboardInterrupt):
        print("\n   Using default: 1 run per scenario")
        num_runs = 1
    
    total_tests = 20 * num_runs * 2  # 20 scenarios * num_runs * 2 formats
    print(f"\n   Will run {total_tests} total tests:")
    print(f"   - {20 * num_runs} baseline tests")
    print(f"   - {20 * num_runs} enhanced tests")
    
    # Confirm
    print("\n4. Starting validation tests...")
    print("   This may take a while depending on API response times.")
    print("   Press Ctrl+C to cancel.\n")
    
    try:
        # Run tests
        results = runner.run_all_tests(num_runs=num_runs)
        
        print("\n" + "=" * 80)
        print("✅ Validation tests completed!")
        print("=" * 80)
        print(f"\nResults saved to:")
        print(f"  - {results_dir / 'baseline_results.json'}")
        print(f"  - {results_dir / 'enhanced_results.json'}")
        print(f"\nNext steps:")
        print(f"  1. Analyze results: python tests/validation/results_analyzer.py")
        print(f"  2. Generate reports: python tests/validation/report_generator.py")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        print("Partial results may be saved in results/ directory")
        return 1
    except Exception as e:
        print(f"\n\n❌ Error running tests: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

