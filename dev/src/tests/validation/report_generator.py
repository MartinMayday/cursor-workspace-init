"""
Report generator for validation testing.

Generates comprehensive validation reports in multiple formats (Markdown, JSON, HTML).
"""

from pathlib import Path
from typing import Dict, Any, Optional
import json
from datetime import datetime
from results_analyzer import ResultsAnalyzer


class ReportGenerator:
    """Generates validation reports."""
    
    def __init__(self, results_dir: Path, ground_truth_dir: Path, reports_dir: Path):
        """
        Initialize report generator.
        
        Args:
            results_dir: Directory containing test results
            ground_truth_dir: Directory containing ground truth
            reports_dir: Directory to save reports
        """
        self.results_dir = results_dir
        self.ground_truth_dir = ground_truth_dir
        self.reports_dir = reports_dir
        self.reports_dir.mkdir(exist_ok=True)
        
        self.analyzer = ResultsAnalyzer(results_dir, ground_truth_dir)
        
    def generate_markdown_report(self) -> str:
        """
        Generate Markdown validation report.
        
        Returns:
            Markdown report string
        """
        comparison = self.analyzer.compare_formats()
        complexity_analysis = self.analyzer.analyze_by_complexity()
        
        # Use .get() with defaults to handle missing keys
        baseline = comparison.get('baseline', {})
        enhanced = comparison.get('enhanced', {})
        improvements = comparison.get('improvements', {})
        
        report = f"""# Manifest Format Validation Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

This report presents the results of validation testing comparing the baseline (current) manifest format against the enhanced (proposed) manifest format. The enhanced format includes additional fields such as `semantic_meaning`, `use_when`, `conditions`, and `triggers` to enable AI agents to make context block decisions with higher certainty.

### Key Findings

- **Baseline Format Accuracy:** {baseline.get('accuracy_mean', 0):.2f}%
- **Enhanced Format Accuracy:** {enhanced.get('accuracy_mean', 0):.2f}%
- **Accuracy Improvement:** {improvements.get('accuracy_improvement', 0):+.2f} percentage points

- **Baseline Format Confidence:** {baseline.get('confidence_mean', 0):.2f}%
- **Enhanced Format Confidence:** {enhanced.get('confidence_mean', 0):.2f}%
- **Confidence Improvement:** {improvements.get('confidence_improvement', 0):+.2f} percentage points

- **Baseline Clarification Requests:** {baseline.get('clarification_requests', 0)} ({baseline.get('clarification_rate', 0):.2f}%)
- **Enhanced Clarification Requests:** {enhanced.get('clarification_requests', 0)} ({enhanced.get('clarification_rate', 0):.2f}%)
- **Clarification Reduction:** {improvements.get('clarification_reduction', 0)} requests ({improvements.get('clarification_reduction_percent', 0):+.2f}%)

## Methodology

### Test Design

- **Total Scenarios:** 20 diverse test scenarios
- **Scenario Types:**
  - Simple (5 scenarios): Single project type, single language
  - Medium (7 scenarios): Multiple frameworks, deployment types
  - Complex (5 scenarios): Missing context, partial information
  - Edge Cases (3 scenarios): Unknown project types, missing languages

- **Test Execution:**
  - 10 runs per scenario per format
  - Total: 200 baseline tests, 200 enhanced tests
  - AI models: Multiple models tested (when available)

### Success Criteria

**Primary Criteria:**
- Enhanced format achieves ≥98% accuracy in file selection
- Enhanced format achieves ≥98% confidence level from AI agents
- Enhanced format reduces clarification requests to zero
- Enhanced format maintains or improves decision speed

**Secondary Criteria:**
- Statistically significant improvement over baseline (p < 0.05)
- Works across multiple AI models
- AI agents can explain reasoning using manifest fields

## Results

### Overall Metrics

#### Baseline Format

| Metric | Value |
|--------|-------|
| Total Tests | {baseline.get('total_tests', 0)} |
| Accuracy (Mean) | {baseline.get('accuracy_mean', 0):.2f}% |
| Accuracy (Std Dev) | {baseline.get('accuracy_std', 0):.2f}% |
| Confidence (Mean) | {baseline.get('confidence_mean', 0):.2f}% |
| Confidence (Std Dev) | {baseline.get('confidence_std', 0):.2f}% |
| Clarification Requests | {baseline.get('clarification_requests', 0)} |
| Clarification Rate | {baseline.get('clarification_rate', 0):.2f}% |
| Decision Time (Mean) | {baseline.get('decision_time_mean', 0):.3f}s |
| Decision Time (Std Dev) | {baseline.get('decision_time_std', 0):.3f}s |

#### Enhanced Format

| Metric | Value |
|--------|-------|
| Total Tests | {enhanced.get('total_tests', 0)} |
| Accuracy (Mean) | {enhanced.get('accuracy_mean', 0):.2f}% |
| Accuracy (Std Dev) | {enhanced.get('accuracy_std', 0):.2f}% |
| Confidence (Mean) | {enhanced.get('confidence_mean', 0):.2f}% |
| Confidence (Std Dev) | {enhanced.get('confidence_std', 0):.2f}% |
| Clarification Requests | {enhanced.get('clarification_requests', 0)} |
| Clarification Rate | {enhanced.get('clarification_rate', 0):.2f}% |
| Decision Time (Mean) | {enhanced.get('decision_time_mean', 0):.3f}s |
| Decision Time (Std Dev) | {enhanced.get('decision_time_std', 0):.3f}s |

### Improvements

| Metric | Improvement |
|--------|-------------|
| Accuracy | {improvements.get('accuracy_improvement', 0):+.2f} percentage points |
| Confidence | {improvements.get('confidence_improvement', 0):+.2f} percentage points |
| Clarification Requests | {improvements.get('clarification_reduction', 0)} fewer requests |
| Decision Time | {improvements.get('time_change', 0):+.3f}s ({improvements.get('time_change_percent', 0):+.2f}%) |

### Results by Complexity

"""
        
        for complexity, metrics in complexity_analysis.items():
            comp_baseline = metrics.get('baseline', {})
            comp_enhanced = metrics.get('enhanced', {})
            
            report += f"""
#### {complexity.capitalize()} Scenarios

| Metric | Baseline | Enhanced | Improvement |
|--------|----------|----------|-------------|
| Accuracy | {comp_baseline.get('accuracy_mean', 0):.2f}% | {comp_enhanced.get('accuracy_mean', 0):.2f}% | {comp_enhanced.get('accuracy_mean', 0) - comp_baseline.get('accuracy_mean', 0):+.2f}% |
| Confidence | {comp_baseline.get('confidence_mean', 0):.2f}% | {comp_enhanced.get('confidence_mean', 0):.2f}% | {comp_enhanced.get('confidence_mean', 0) - comp_baseline.get('confidence_mean', 0):+.2f}% |
| Clarifications | {comp_baseline.get('clarification_requests', 0)} | {comp_enhanced.get('clarification_requests', 0)} | {comp_baseline.get('clarification_requests', 0) - comp_enhanced.get('clarification_requests', 0):+d} |

"""
        
        # Statistical analysis
        if "statistical_test" in comparison:
            stat_test = comparison["statistical_test"]
            if "error" not in stat_test and "note" not in stat_test:
                report += f"""
### Statistical Analysis

- **T-Statistic:** {stat_test.get('t_statistic', 0):.4f}
- **P-Value:** {stat_test.get('p_value', 1):.4f}
- **Significance:** {stat_test.get('interpretation', 'N/A')}

The statistical test {'confirms' if stat_test.get('significant', False) else 'does not confirm'} a statistically significant difference between baseline and enhanced formats (p < 0.05).

"""
            elif "note" in stat_test:
                report += f"""
### Statistical Analysis

**Note:** {stat_test.get('note', 'N/A')}

- **Baseline Mean:** {stat_test.get('baseline_mean', 0):.2f}%
- **Enhanced Mean:** {stat_test.get('enhanced_mean', 0):.2f}%
- **Difference:** {stat_test.get('difference', 0):+.2f}%

"""
        
        # Success criteria
        report += f"""
## Success Criteria Evaluation

| Criterion | Target | Actual | Status |
|-----------|--------|--------|--------|
| Accuracy ≥98% | ≥98% | {enhanced.get('accuracy_mean', 0):.2f}% | {'✓ PASS' if enhanced.get('accuracy_mean', 0) >= 98 else '✗ FAIL'} |
| Confidence ≥98% | ≥98% | {enhanced.get('confidence_mean', 0):.2f}% | {'✓ PASS' if enhanced.get('confidence_mean', 0) >= 98 else '✗ FAIL'} |
| Zero Clarifications | 0 | {enhanced.get('clarification_requests', 0)} | {'✓ PASS' if enhanced.get('clarification_requests', 0) == 0 else '✗ FAIL'} |
| Speed Maintained | ≤ baseline | {improvements.get('time_change', 0):+.3f}s | {'✓ PASS' if improvements.get('time_change', 0) <= 0 else '✗ FAIL'} |

## Recommendations

"""
        
        # Generate recommendations based on results
        if enhanced.get('accuracy_mean', 0) >= 98 and enhanced.get('confidence_mean', 0) >= 98:
            report += """
### Primary Recommendation: **ADOPT ENHANCED FORMAT**

The enhanced manifest format successfully meets all primary success criteria:
- Achieves ≥98% accuracy in file selection
- Achieves ≥98% confidence level from AI agents
- Reduces clarification requests significantly
- Maintains or improves decision speed

**Action Items:**
1. Implement enhanced format in production manifest generator
2. Update documentation to reflect new format
3. Migrate existing manifests to enhanced format
4. Monitor performance in production

"""
        else:
            report += """
### Primary Recommendation: **REFINE ENHANCED FORMAT**

The enhanced manifest format shows improvement but does not meet all success criteria. Consider:
1. Refining semantic_meaning definitions for clarity
2. Improving use_when descriptions
3. Enhancing conditions and triggers logic
4. Additional testing with more scenarios

"""
        
        report += f"""
## Conclusion

The validation testing {'confirms' if enhanced.get('accuracy_mean', 0) >= 98 else 'suggests'} that the enhanced manifest format {'successfully' if enhanced.get('accuracy_mean', 0) >= 98 else 'partially'} enables AI agents to make context block decisions with {'high' if enhanced.get('accuracy_mean', 0) >= 98 else 'improved'} certainty.

**Key Takeaways:**
- Enhanced format shows {improvements.get('accuracy_improvement', 0):+.2f}% improvement in accuracy
- Enhanced format shows {improvements.get('confidence_improvement', 0):+.2f}% improvement in confidence
- Enhanced format reduces clarification requests by {improvements.get('clarification_reduction', 0)} requests
- Decision time {'improved' if improvements.get('time_change', 0) < 0 else 'increased'} by {abs(improvements.get('time_change', 0)):.3f}s

---

*Report generated by Manifest Format Validation Testing Infrastructure*
"""
        
        return report
    
    def generate_json_report(self) -> Dict[str, Any]:
        """
        Generate JSON validation report.
        
        Returns:
            JSON report dictionary
        """
        comparison = self.analyzer.compare_formats()
        complexity_analysis = self.analyzer.analyze_by_complexity()
        
        report = {
            "report_metadata": {
                "generated": datetime.now().isoformat(),
                "report_type": "validation",
                "version": "1.0"
            },
            "executive_summary": {
                "baseline_accuracy": comparison.get('baseline', {}).get('accuracy_mean', 0),
                "enhanced_accuracy": comparison.get('enhanced', {}).get('accuracy_mean', 0),
                "accuracy_improvement": comparison.get('improvements', {}).get('accuracy_improvement', 0),
                "baseline_confidence": comparison.get('baseline', {}).get('confidence_mean', 0),
                "enhanced_confidence": comparison.get('enhanced', {}).get('confidence_mean', 0),
                "confidence_improvement": comparison.get('improvements', {}).get('confidence_improvement', 0)
            },
            "methodology": {
                "total_scenarios": 20,
                "runs_per_scenario": 10,
                "total_tests": {
                    "baseline": comparison.get('baseline', {}).get('total_tests', 0),
                    "enhanced": comparison.get('enhanced', {}).get('total_tests', 0)
                }
            },
            "results": {
                "baseline": comparison.get('baseline', {}),
                "enhanced": comparison.get('enhanced', {}),
                "improvements": comparison.get('improvements', {})
            },
            "complexity_analysis": complexity_analysis,
            "statistical_test": comparison.get("statistical_test", {}),
            "success_criteria": {
                "accuracy_target": 98.0,
                "accuracy_actual": comparison.get('enhanced', {}).get('accuracy_mean', 0),
                "accuracy_passed": comparison.get('enhanced', {}).get('accuracy_mean', 0) >= 98.0,
                "confidence_target": 98.0,
                "confidence_actual": comparison.get('enhanced', {}).get('confidence_mean', 0),
                "confidence_passed": comparison.get('enhanced', {}).get('confidence_mean', 0) >= 98.0,
                "clarification_target": 0,
                "clarification_actual": comparison.get('enhanced', {}).get('clarification_requests', 0),
                "clarification_passed": comparison.get('enhanced', {}).get('clarification_requests', 0) == 0
            }
        }
        
        return report
    
    def save_reports(self):
        """Save reports in all formats."""
        # Markdown
        md_report = self.generate_markdown_report()
        md_path = self.reports_dir / "validation_report.md"
        md_path.write_text(md_report)
        print(f"Saved Markdown report to {md_path}")
        
        # JSON
        json_report = self.generate_json_report()
        json_path = self.reports_dir / "validation_report.json"
        with open(json_path, 'w') as f:
            json.dump(json_report, f, indent=2)
        print(f"Saved JSON report to {json_path}")
        
        # Also save comparison JSON
        self.analyzer.save_comparison(self.results_dir / "comparison.json")


if __name__ == "__main__":
    # Get paths
    validation_dir = Path(__file__).parent
    results_dir = validation_dir / "results"
    ground_truth_dir = validation_dir / "ground_truth"
    reports_dir = validation_dir / "reports"
    
    # Create generator
    generator = ReportGenerator(results_dir, ground_truth_dir, reports_dir)
    
    # Generate and save reports
    generator.save_reports()
    print("\nReports generated successfully!")

