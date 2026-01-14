"""
Manifest generator for validation testing.

Generates both baseline (current) and enhanced (proposed) format manifests
for test scenarios.
"""

from pathlib import Path
from typing import Dict, Any, List
import json


def generate_baseline_manifest(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate baseline manifest in current format (minimal structure).
    
    Args:
        context: Context variables dictionary from test scenario
        
    Returns:
        Baseline manifest dictionary
    """
    project_type = context.get("project_type")
    primary_language = context.get("primary_language")
    
    rules = []
    
    # Level 1 - Always required
    rules.append({
        "level": 1,
        "file": "level1-core.mdc",
        "description": "Core rules and principles",
        "required": True
    })
    
    # Level 2 - Always required
    rules.append({
        "level": 2,
        "file": "level2-architecture.mdc",
        "description": "Architecture and design patterns",
        "required": True
    })
    
    # Level 3 - Conditional on project_type
    if project_type and project_type != "unknown":
        rules.append({
            "level": 3,
            "file": "level3-project-type.mdc",
            "description": "Project type-specific rules",
            "required": False
        })
    
    # Level 4 - Conditional on primary_language
    if primary_language and primary_language != "unknown":
        rules.append({
            "level": 4,
            "file": "level4-language.mdc",
            "description": "Language-specific rules",
            "required": False
        })
    
    return {"rules": rules}


def generate_enhanced_manifest(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate enhanced manifest in proposed format (with semantic meaning, conditions, etc.).
    
    Args:
        context: Context variables dictionary from test scenario
        
    Returns:
        Enhanced manifest dictionary
    """
    project_type = context.get("project_type")
    primary_language = context.get("primary_language")
    
    rules = []
    
    # Level 1 - Always required
    rules.append({
        "level": 1,
        "file": "level1-core.mdc",
        "path": ".cursor/rules/level1-core.mdc",
        "category": "rules",
        "file_type": "rule",
        "description": "Core rules and principles",
        "required": True,
        "load_order": 1,
        "use_when": "always - these are fundamental rules that apply to all projects",
        "semantic_meaning": {
            "level_meaning": "Progressive loading hierarchy - Level 1 is most general, always loaded first",
            "specificity": "general",
            "scope": "project-wide",
            "purpose": "Contains fundamental rules and principles that apply universally to all projects"
        },
        "conditions": {
            "always_load": True,
            "context_required": [],
            "triggers": []
        }
    })
    
    # Level 2 - Always required
    rules.append({
        "level": 2,
        "file": "level2-architecture.mdc",
        "path": ".cursor/rules/level2-architecture.mdc",
        "category": "rules",
        "file_type": "rule",
        "description": "Architecture and design patterns",
        "required": True,
        "load_order": 2,
        "use_when": "always - architecture rules apply to all projects",
        "semantic_meaning": {
            "level_meaning": "Architecture and design pattern rules, loaded after core rules",
            "specificity": "architectural",
            "scope": "project-wide",
            "purpose": "Contains architecture and design pattern guidelines"
        },
        "conditions": {
            "always_load": True,
            "context_required": [],
            "triggers": []
        }
    })
    
    # Level 3 - Conditional on project_type
    if project_type and project_type != "unknown":
        rules.append({
            "level": 3,
            "file": "level3-project-type.mdc",
            "path": ".cursor/rules/level3-project-type.mdc",
            "category": "rules",
            "file_type": "rule",
            "description": "Project type-specific rules",
            "required": False,
            "load_order": 3,
            "use_when": f"when project_type is '{project_type}' and not 'unknown'",
            "semantic_meaning": {
                "level_meaning": "Project type-specific rules, loaded after core and architecture rules",
                "specificity": "project-type-specific",
                "scope": f"applies to {project_type} projects",
                "purpose": f"Contains rules specific to {project_type} project types"
            },
            "conditions": {
                "always_load": False,
                "context_required": ["project_type"],
                "triggers": [
                    {
                        "field": "project_type",
                        "operator": "!=",
                        "value": "unknown",
                        "action": "load"
                    },
                    {
                        "field": "project_type",
                        "operator": "!=",
                        "value": None,
                        "action": "load"
                    }
                ]
            }
        })
    
    # Level 4 - Conditional on primary_language
    if primary_language and primary_language != "unknown":
        rules.append({
            "level": 4,
            "file": "level4-language.mdc",
            "path": ".cursor/rules/level4-language.mdc",
            "category": "rules",
            "file_type": "rule",
            "description": "Language-specific rules",
            "required": False,
            "load_order": 4,
            "use_when": f"when primary_language is '{primary_language}' and not 'unknown'",
            "semantic_meaning": {
                "level_meaning": "Language-specific rules, loaded after project type rules",
                "specificity": "language-specific",
                "scope": f"applies to {primary_language} projects",
                "purpose": f"Contains rules specific to {primary_language} programming language"
            },
            "conditions": {
                "always_load": False,
                "context_required": ["primary_language"],
                "triggers": [
                    {
                        "field": "primary_language",
                        "operator": "!=",
                        "value": "unknown",
                        "action": "load"
                    },
                    {
                        "field": "primary_language",
                        "operator": "!=",
                        "value": None,
                        "action": "load"
                    }
                ]
            }
        })
    
    return {
        "manifest_type": "rules",
        "manifest_version": "1.0",
        "rules": rules
    }


def generate_all_manifests(scenarios_path: Path, baseline_dir: Path, enhanced_dir: Path):
    """
    Generate all baseline and enhanced manifests for all test scenarios.
    
    Args:
        scenarios_path: Path to test_scenarios.json file
        baseline_dir: Directory to save baseline manifests
        enhanced_dir: Directory to save enhanced manifests
    """
    # Load test scenarios
    with open(scenarios_path, 'r') as f:
        data = json.load(f)
        scenarios = data.get("scenarios", [])
    
    # Generate manifests for each scenario
    for scenario in scenarios:
        scenario_id = scenario["scenario_id"]
        context = scenario["context"]
        
        # Generate baseline manifest
        baseline_manifest = generate_baseline_manifest(context)
        baseline_path = baseline_dir / f"{scenario_id}.json"
        with open(baseline_path, 'w') as f:
            json.dump(baseline_manifest, f, indent=2)
        
        # Generate enhanced manifest
        enhanced_manifest = generate_enhanced_manifest(context)
        enhanced_path = enhanced_dir / f"{scenario_id}.json"
        with open(enhanced_path, 'w') as f:
            json.dump(enhanced_manifest, f, indent=2)
        
        print(f"Generated manifests for {scenario_id}")
    
    print(f"\nGenerated {len(scenarios)} baseline manifests in {baseline_dir}")
    print(f"Generated {len(scenarios)} enhanced manifests in {enhanced_dir}")


if __name__ == "__main__":
    # Get paths
    validation_dir = Path(__file__).parent
    scenarios_path = validation_dir / "test_scenarios.json"
    baseline_dir = validation_dir / "baseline_manifests"
    enhanced_dir = validation_dir / "enhanced_manifests"
    
    # Generate all manifests
    generate_all_manifests(scenarios_path, baseline_dir, enhanced_dir)

