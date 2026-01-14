"""
Results analyzer for validation testing.

Calculates metrics, compares baseline vs enhanced formats, and performs statistical analysis.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import json
import statistics

# Optional: scipy for statistical tests
try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


class ResultsAnalyzer:
    """Analyzes validation test results."""
    
    def __init__(self, results_dir: Path, ground_truth_dir: Path):
        """
        Initialize results analyzer.
        
        Args:
            results_dir: Directory containing test results
            ground_truth_dir: Directory containing ground truth validations
        """
        self.results_dir = results_dir
        self.ground_truth_dir = ground_truth_dir
        
    def load_results(self, format_type: str) -> List[Dict[str, Any]]:
        """
        Load test results for a format type.
        
        Args:
            format_type: 'baseline' or 'enhanced'
            
        Returns:
            List of test results
        """
        results_path = self.results_dir / f"{format_type}_results.json"
        if not results_path.exists():
            return []
        
        with open(results_path, 'r') as f:
            return json.load(f)
    
    def load_ground_truth(self) -> Dict[str, List[str]]:
        """
        Load ground truth file selections.
        
        Returns:
            Dictionary mapping scenario_id to expected files
        """
        ground_truth_path = self.ground_truth_dir / "expert_validations.json"
        
        if ground_truth_path.exists():
            with open(ground_truth_path, 'r') as f:
                consolidated = json.load(f)
                return {
                    scenario_id: data["ground_truth_files"]
                    for scenario_id, data in consolidated.items()
                }
        
        # Fallback: use expected_files from scenarios
        scenarios_path = self.results_dir.parent / "test_scenarios.json"
        if scenarios_path.exists():
            with open(scenarios_path, 'r') as f:
                data = json.load(f)
                scenarios = data.get("scenarios", [])
                return {
                    scenario["scenario_id"]: scenario.get("expected_files", [])
                    for scenario in scenarios
                }
        
        return {}
    
    def calculate_accuracy(self, selected_files: List[str], expected_files: List[str]) -> float:
        """
        Calculate accuracy as percentage of correct file selections.
        
        Args:
            selected_files: Files selected by AI
            expected_files: Expected files (ground truth)
            
        Returns:
            Accuracy percentage (0-100)
        """
        if not expected_files:
            return 0.0
        
        selected_set = set(selected_files)
        expected_set = set(expected_files)
        
        correct = len(selected_set.intersection(expected_set))
        total = len(expected_set)
        
        return (correct / total * 100) if total > 0 else 0.0
    
    def calculate_metrics(self, results: List[Dict[str, Any]], 
                         ground_truth: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Calculate metrics for a set of results.
        
        Args:
            results: List of test results
            ground_truth: Ground truth file selections
            
        Returns:
            Metrics dictionary
        """
        if not results:
            return {
                "total_tests": 0,
                "accuracy_mean": 0.0,
                "accuracy_std": 0.0,
                "confidence_mean": 0.0,
                "confidence_std": 0.0,
                "clarification_requests": 0,
                "decision_time_mean": 0.0,
                "decision_time_std": 0.0
            }
        
        accuracies = []
        confidences = []
        clarification_requests = 0
        decision_times = []
        
        for result in results:
            scenario_id = result["scenario_id"]
            expected_files = ground_truth.get(scenario_id, result.get("expected_files", []))
            
            accuracy = self.calculate_accuracy(
                result.get("selected_files", []),
                expected_files
            )
            accuracies.append(accuracy)
            
            confidences.append(result.get("confidence", 0))
            
            if result.get("clarification_needed", False):
                clarification_requests += 1
            
            decision_times.append(result.get("decision_time", 0))
        
        return {
            "total_tests": len(results),
            "accuracy_mean": statistics.mean(accuracies) if accuracies else 0.0,
            "accuracy_std": statistics.stdev(accuracies) if len(accuracies) > 1 else 0.0,
            "accuracy_min": min(accuracies) if accuracies else 0.0,
            "accuracy_max": max(accuracies) if accuracies else 0.0,
            "confidence_mean": statistics.mean(confidences) if confidences else 0.0,
            "confidence_std": statistics.stdev(confidences) if len(confidences) > 1 else 0.0,
            "confidence_min": min(confidences) if confidences else 0.0,
            "confidence_max": max(confidences) if confidences else 0.0,
            "clarification_requests": clarification_requests,
            "clarification_rate": clarification_requests / len(results) * 100 if results else 0.0,
            "decision_time_mean": statistics.mean(decision_times) if decision_times else 0.0,
            "decision_time_std": statistics.stdev(decision_times) if len(decision_times) > 1 else 0.0,
            "decision_time_min": min(decision_times) if decision_times else 0.0,
            "decision_time_max": max(decision_times) if decision_times else 0.0
        }
    
    def compare_formats(self) -> Dict[str, Any]:
        """
        Compare baseline vs enhanced format results.
        
        Returns:
            Comparison dictionary
        """
        ground_truth = self.load_ground_truth()
        
        baseline_results = self.load_results("baseline")
        enhanced_results = self.load_results("enhanced")
        
        baseline_metrics = self.calculate_metrics(baseline_results, ground_truth)
        enhanced_metrics = self.calculate_metrics(enhanced_results, ground_truth)
        
        # Calculate improvements
        accuracy_improvement = enhanced_metrics["accuracy_mean"] - baseline_metrics["accuracy_mean"]
        confidence_improvement = enhanced_metrics["confidence_mean"] - baseline_metrics["confidence_mean"]
        clarification_reduction = baseline_metrics["clarification_requests"] - enhanced_metrics["clarification_requests"]
        time_change = enhanced_metrics["decision_time_mean"] - baseline_metrics["decision_time_mean"]
        
        comparison = {
            "baseline": baseline_metrics,
            "enhanced": enhanced_metrics,
            "improvements": {
                "accuracy_improvement": accuracy_improvement,
                "confidence_improvement": confidence_improvement,
                "clarification_reduction": clarification_reduction,
                "clarification_reduction_percent": (clarification_reduction / baseline_metrics["clarification_requests"] * 100) if baseline_metrics["clarification_requests"] > 0 else 0.0,
                "time_change": time_change,
                "time_change_percent": (time_change / baseline_metrics["decision_time_mean"] * 100) if baseline_metrics["decision_time_mean"] > 0 else 0.0
            }
        }
        
        # Statistical significance test (t-test)
        if baseline_results and enhanced_results:
            baseline_accuracies = [
                self.calculate_accuracy(
                    r.get("selected_files", []),
                    ground_truth.get(r["scenario_id"], r.get("expected_files", []))
                )
                for r in baseline_results
            ]
            enhanced_accuracies = [
                self.calculate_accuracy(
                    r.get("selected_files", []),
                    ground_truth.get(r["scenario_id"], r.get("expected_files", []))
                )
                for r in enhanced_results
            ]
            
            if len(baseline_accuracies) > 1 and len(enhanced_accuracies) > 1:
                if SCIPY_AVAILABLE:
                    try:
                        t_stat, p_value = stats.ttest_ind(baseline_accuracies, enhanced_accuracies)
                        comparison["statistical_test"] = {
                            "t_statistic": float(t_stat),
                            "p_value": float(p_value),
                            "significant": p_value < 0.05,
                            "interpretation": "Statistically significant" if p_value < 0.05 else "Not statistically significant"
                        }
                    except Exception as e:
                        comparison["statistical_test"] = {
                            "error": str(e)
                        }
                else:
                    comparison["statistical_test"] = {
                        "note": "scipy not available - statistical test skipped",
                        "baseline_mean": statistics.mean(baseline_accuracies),
                        "enhanced_mean": statistics.mean(enhanced_accuracies),
                        "difference": statistics.mean(enhanced_accuracies) - statistics.mean(baseline_accuracies)
                    }
        
        return comparison
    
    def analyze_by_complexity(self) -> Dict[str, Any]:
        """
        Analyze results grouped by scenario complexity.
        
        Returns:
            Analysis dictionary grouped by complexity
        """
        ground_truth = self.load_ground_truth()
        
        # Load scenarios to get complexity
        scenarios_path = self.results_dir.parent / "test_scenarios.json"
        scenarios = {}
        if scenarios_path.exists():
            with open(scenarios_path, 'r') as f:
                data = json.load(f)
                for scenario in data.get("scenarios", []):
                    scenarios[scenario["scenario_id"]] = scenario.get("complexity", "unknown")
        
        baseline_results = self.load_results("baseline")
        enhanced_results = self.load_results("enhanced")
        
        complexity_groups = {
            "simple": {"baseline": [], "enhanced": []},
            "medium": {"baseline": [], "enhanced": []},
            "complex": {"baseline": [], "enhanced": []},
            "edge_case": {"baseline": [], "enhanced": []}
        }
        
        # Group results by complexity
        for result in baseline_results:
            complexity = scenarios.get(result["scenario_id"], "unknown")
            if complexity in complexity_groups:
                complexity_groups[complexity]["baseline"].append(result)
        
        for result in enhanced_results:
            complexity = scenarios.get(result["scenario_id"], "unknown")
            if complexity in complexity_groups:
                complexity_groups[complexity]["enhanced"].append(result)
        
        # Calculate metrics for each complexity group
        analysis = {}
        for complexity, groups in complexity_groups.items():
            analysis[complexity] = {
                "baseline": self.calculate_metrics(groups["baseline"], ground_truth),
                "enhanced": self.calculate_metrics(groups["enhanced"], ground_truth)
            }
        
        return analysis
    
    def generate_comparison_report(self) -> str:
        """
        Generate a text report comparing baseline vs enhanced formats.
        
        Returns:
            Report string
        """
        comparison = self.compare_formats()
        
        report = f"""
Validation Results Comparison Report
{'='*80}

BASELINE FORMAT METRICS:
  Total Tests: {comparison['baseline']['total_tests']}
  Accuracy: {comparison['baseline']['accuracy_mean']:.2f}% (±{comparison['baseline']['accuracy_std']:.2f}%)
  Confidence: {comparison['baseline']['confidence_mean']:.2f}% (±{comparison['baseline']['confidence_std']:.2f}%)
  Clarification Requests: {comparison['baseline']['clarification_requests']} ({comparison['baseline']['clarification_rate']:.2f}%)
  Decision Time: {comparison['baseline']['decision_time_mean']:.3f}s (±{comparison['baseline']['decision_time_std']:.3f}s)

ENHANCED FORMAT METRICS:
  Total Tests: {comparison['enhanced']['total_tests']}
  Accuracy: {comparison['enhanced']['accuracy_mean']:.2f}% (±{comparison['enhanced']['accuracy_std']:.2f}%)
  Confidence: {comparison['enhanced']['confidence_mean']:.2f}% (±{comparison['enhanced']['confidence_std']:.2f}%)
  Clarification Requests: {comparison['enhanced']['clarification_requests']} ({comparison['enhanced']['clarification_rate']:.2f}%)
  Decision Time: {comparison['enhanced']['decision_time_mean']:.3f}s (±{comparison['enhanced']['decision_time_std']:.3f}s)

IMPROVEMENTS:
  Accuracy Improvement: {comparison['improvements']['accuracy_improvement']:+.2f}%
  Confidence Improvement: {comparison['improvements']['confidence_improvement']:+.2f}%
  Clarification Reduction: {comparison['improvements']['clarification_reduction']} ({comparison['improvements']['clarification_reduction_percent']:+.2f}%)
  Time Change: {comparison['improvements']['time_change']:+.3f}s ({comparison['improvements']['time_change_percent']:+.2f}%)

"""
        
        if "statistical_test" in comparison:
            stat_test = comparison["statistical_test"]
            if "error" not in stat_test and "note" not in stat_test:
                report += f"""
STATISTICAL ANALYSIS:
  T-Statistic: {stat_test.get('t_statistic', 0):.4f}
  P-Value: {stat_test.get('p_value', 1):.4f}
  Significance: {stat_test.get('interpretation', 'N/A')}
"""
            elif "note" in stat_test:
                report += f"""
STATISTICAL ANALYSIS:
  Note: {stat_test.get('note', 'N/A')}
  Baseline Mean: {stat_test.get('baseline_mean', 0):.2f}%
  Enhanced Mean: {stat_test.get('enhanced_mean', 0):.2f}%
  Difference: {stat_test.get('difference', 0):+.2f}%
"""
        
        # Success criteria check
        enhanced = comparison['enhanced']
        report += f"""
SUCCESS CRITERIA CHECK:
  Accuracy ≥98%: {'✓' if enhanced['accuracy_mean'] >= 98 else '✗'} ({enhanced['accuracy_mean']:.2f}%)
  Confidence ≥98%: {'✓' if enhanced['confidence_mean'] >= 98 else '✗'} ({enhanced['confidence_mean']:.2f}%)
  Zero Clarifications: {'✓' if enhanced['clarification_requests'] == 0 else '✗'} ({enhanced['clarification_requests']} requests)
  Speed Maintained: {'✓' if comparison['improvements']['time_change'] <= 0 else '✗'} ({comparison['improvements']['time_change']:+.3f}s)
"""
        
        return report
    
    def save_comparison(self, output_path: Optional[Path] = None):
        """
        Save comparison results to JSON file.
        
        Args:
            output_path: Optional path to save comparison. Defaults to results_dir/comparison.json
        """
        if output_path is None:
            output_path = self.results_dir / "comparison.json"
        
        comparison = self.compare_formats()
        
        with open(output_path, 'w') as f:
            json.dump(comparison, f, indent=2)
        
        print(f"Saved comparison to {output_path}")


if __name__ == "__main__":
    # Get paths
    validation_dir = Path(__file__).parent
    results_dir = validation_dir / "results"
    ground_truth_dir = validation_dir / "ground_truth"
    
    # Create analyzer
    analyzer = ResultsAnalyzer(results_dir, ground_truth_dir)
    
    # Generate comparison
    comparison = analyzer.compare_formats()
    print(analyzer.generate_comparison_report())
    
    # Save comparison
    analyzer.save_comparison()

