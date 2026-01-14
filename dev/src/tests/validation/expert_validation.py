"""
Expert validation tool for establishing ground truth.

Allows human experts to review scenarios and validate expected file selections.
"""

from pathlib import Path
from typing import Dict, Any, List
import json
from datetime import datetime


class ExpertValidator:
    """Tool for expert validation of test scenarios."""
    
    def __init__(self, scenarios_path: Path, ground_truth_dir: Path):
        """
        Initialize expert validator.
        
        Args:
            scenarios_path: Path to test_scenarios.json
            ground_truth_dir: Directory to save expert validations
        """
        self.scenarios_path = scenarios_path
        self.ground_truth_dir = ground_truth_dir
        self.ground_truth_dir.mkdir(exist_ok=True)
        
    def load_scenarios(self) -> List[Dict[str, Any]]:
        """Load test scenarios from JSON file."""
        with open(self.scenarios_path, 'r') as f:
            data = json.load(f)
            return data.get("scenarios", [])
    
    def display_scenario(self, scenario: Dict[str, Any]) -> str:
        """
        Format scenario for display.
        
        Args:
            scenario: Scenario dictionary
            
        Returns:
            Formatted string
        """
        context = scenario["context"]
        expected = scenario.get("expected_files", [])
        
        output = f"""
{'='*80}
Scenario: {scenario['scenario_name']} ({scenario['scenario_id']})
Complexity: {scenario['complexity']}
{'='*80}

Description: {scenario['description']}

CONTEXT:
  Project Name: {context.get('project_name', 'N/A')}
  Project Type: {context.get('project_type', 'N/A')}
  Primary Language: {context.get('primary_language', 'N/A')}
  Frameworks: {', '.join(context.get('frameworks', [])) or 'None'}
  Architecture: {context.get('architecture', 'N/A')}
  Deployment: {context.get('deployment_type', 'N/A')}
  Database: {context.get('database', 'N/A')}

CURRENT EXPECTED FILES:
  {', '.join(expected) if expected else 'None'}

NOTES:
  {scenario.get('notes', 'None')}
{'='*80}
"""
        return output
    
    def validate_scenario(self, scenario: Dict[str, Any], expert_name: str, 
                         validated_files: List[str], notes: str = "") -> Dict[str, Any]:
        """
        Record expert validation for a scenario.
        
        Args:
            scenario: Scenario dictionary
            expert_name: Name of expert
            validated_files: List of files expert believes should be loaded
            notes: Optional notes from expert
            
        Returns:
            Validation record dictionary
        """
        return {
            "scenario_id": scenario["scenario_id"],
            "expert_name": expert_name,
            "validated_files": validated_files,
            "notes": notes,
            "timestamp": datetime.now().isoformat(),
            "original_expected": scenario.get("expected_files", [])
        }
    
    def collect_expert_validations(self, expert_name: str, num_experts: int = 3):
        """
        Interactive tool to collect validations from experts.
        
        Args:
            expert_name: Name of current expert
            num_experts: Total number of experts (for tracking)
        """
        scenarios = self.load_scenarios()
        validations = []
        
        print(f"\n{'='*80}")
        print(f"Expert Validation Tool - {expert_name}")
        print(f"{'='*80}\n")
        print(f"Reviewing {len(scenarios)} scenarios")
        print("For each scenario, review the context and determine which files should be loaded.")
        print("Available files: level1-core.mdc, level2-architecture.mdc, level3-project-type.mdc, level4-language.mdc\n")
        
        for i, scenario in enumerate(scenarios, 1):
            print(self.display_scenario(scenario))
            
            # Get expert input
            print("Which files should be loaded? (comma-separated, e.g., level1-core.mdc,level2-architecture.mdc)")
            print("Or press Enter to accept current expected files.")
            user_input = input("Files: ").strip()
            
            if user_input:
                validated_files = [f.strip() for f in user_input.split(',')]
            else:
                validated_files = scenario.get("expected_files", [])
            
            print("\nAny notes? (optional)")
            notes = input("Notes: ").strip()
            
            validation = self.validate_scenario(scenario, expert_name, validated_files, notes)
            validations.append(validation)
            
            print(f"\n✓ Validated scenario {i}/{len(scenarios)}\n")
        
        # Save validations
        validation_file = self.ground_truth_dir / f"{expert_name}_validations.json"
        with open(validation_file, 'w') as f:
            json.dump(validations, f, indent=2)
        
        print(f"\n✓ Saved validations to {validation_file}")
        return validations
    
    def consolidate_validations(self) -> Dict[str, Any]:
        """
        Consolidate validations from multiple experts using majority consensus.
        
        Returns:
            Consolidated ground truth dictionary
        """
        validation_files = list(self.ground_truth_dir.glob("*_validations.json"))
        
        if not validation_files:
            print("No expert validation files found.")
            return {}
        
        # Load all validations
        all_validations = {}
        for val_file in validation_files:
            expert_name = val_file.stem.replace("_validations", "")
            with open(val_file, 'r') as f:
                validations = json.load(f)
                for val in validations:
                    scenario_id = val["scenario_id"]
                    if scenario_id not in all_validations:
                        all_validations[scenario_id] = []
                    all_validations[scenario_id].append({
                        "expert": expert_name,
                        "files": val["validated_files"],
                        "notes": val.get("notes", "")
                    })
        
        # Consolidate using majority consensus
        consolidated = {}
        for scenario_id, expert_vals in all_validations.items():
            # Count file occurrences
            file_counts = {}
            for expert_val in expert_vals:
                for file in expert_val["files"]:
                    file_counts[file] = file_counts.get(file, 0) + 1
            
            # Files selected by majority (>= 2 out of 3 experts)
            majority_threshold = len(expert_vals) / 2
            ground_truth_files = [
                file for file, count in file_counts.items() 
                if count > majority_threshold
            ]
            
            consolidated[scenario_id] = {
                "ground_truth_files": sorted(ground_truth_files),
                "expert_validations": expert_vals,
                "consensus_level": "majority" if len(expert_vals) >= 2 else "single"
            }
        
        # Save consolidated ground truth
        ground_truth_path = self.ground_truth_dir / "expert_validations.json"
        with open(ground_truth_path, 'w') as f:
            json.dump(consolidated, f, indent=2)
        
        print(f"\n✓ Consolidated ground truth saved to {ground_truth_path}")
        print(f"  Consolidated {len(consolidated)} scenarios")
        
        return consolidated
    
    def generate_validation_report(self) -> str:
        """
        Generate a report of expert validations.
        
        Returns:
            Report string
        """
        validation_files = list(self.ground_truth_dir.glob("*_validations.json"))
        
        if not validation_files:
            return "No expert validation files found."
        
        report = f"""
Expert Validation Report
{'='*80}
Generated: {datetime.now().isoformat()}

Number of Experts: {len(validation_files)}

"""
        
        for val_file in validation_files:
            expert_name = val_file.stem.replace("_validations", "")
            with open(val_file, 'r') as f:
                validations = json.load(f)
            
            report += f"\n{expert_name}:\n"
            report += f"  Validated {len(validations)} scenarios\n"
        
        # Consolidated ground truth
        consolidated_path = self.ground_truth_dir / "expert_validations.json"
        if consolidated_path.exists():
            with open(consolidated_path, 'r') as f:
                consolidated = json.load(f)
            
            report += f"\n\nConsolidated Ground Truth:\n"
            report += f"  {len(consolidated)} scenarios with majority consensus\n"
        
        return report


if __name__ == "__main__":
    # Get paths
    validation_dir = Path(__file__).parent
    scenarios_path = validation_dir / "test_scenarios.json"
    ground_truth_dir = validation_dir / "ground_truth"
    
    # Create validator
    validator = ExpertValidator(scenarios_path, ground_truth_dir)
    
    print("Expert Validation Tool")
    print("=" * 80)
    print("\nOptions:")
    print("1. Collect validations from an expert")
    print("2. Consolidate validations from all experts")
    print("3. Generate validation report")
    print("\nTo use interactively, run:")
    print("  validator.collect_expert_validations('expert_name')")
    print("  validator.consolidate_validations()")

