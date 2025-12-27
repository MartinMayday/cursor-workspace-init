"""
Script 1: Analyze existing repository and generate cursor workspace files.

This script orchestrates all analyzers to collect project information
and generate workspace files from templates.
"""

from pathlib import Path
from typing import Dict, Any


def analyze_repository(repo_path: str = ".") -> Dict[str, Any]:
    """
    Analyze an existing repository and extract context variables.
    
    Args:
        repo_path: Path to the repository directory
        
    Returns:
        Dictionary containing extracted context variables
    """
    repo_path = Path(repo_path).resolve()
    
    # Import analyzers
    from analyzers.language_detector import detect_language
    from analyzers.framework_detector import detect_framework
    from analyzers.project_type_detector import detect_project_type
    from analyzers.dependency_analyzer import analyze_dependencies
    
    # Run all analyzers
    language_info = detect_language(repo_path)
    framework_info = detect_framework(repo_path)
    project_type_info = detect_project_type(repo_path)
    dependency_info = analyze_dependencies(repo_path)
    
    # Collect results into context dictionary
    context = {
        'project_name': repo_path.name,
        'project_type': project_type_info.get('type', 'unknown'),
        'primary_language': language_info.get('primary', 'unknown'),
        'languages': language_info.get('languages', []),
        'framework': framework_info.get('framework', 'unknown'),
        'frameworks': framework_info.get('frameworks', []),
        'dependencies': dependency_info.get('dependencies', []),
        'testing_framework': dependency_info.get('testing', 'unknown'),
        'linting_tools': dependency_info.get('linting', []),
        'formatting_tools': dependency_info.get('formatting', []),
        'services': project_type_info.get('services', []),
        'ports': project_type_info.get('ports', []),
        'architecture': project_type_info.get('architecture', 'unknown'),
    }
    
    return context


def extract_context_variables(analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract and normalize context variables from analysis results.
    
    Args:
        analysis: Raw analysis results dictionary
        
    Returns:
        Normalized context variables dictionary
    """
    # This function can be used for additional processing/normalization
    return analysis


def generate_workspace_files(context: Dict[str, Any], output_path: str):
    """
    Generate workspace files from context.
    
    Args:
        context: Context variables dictionary
        output_path: Path where files should be generated
    """
    from generators.workspace_generator import generate_workspace_files as gen_workspace
    gen_workspace(context, output_path)


def validate_generated_files(output_path: str) -> bool:
    """
    Validate that generated files are correct.
    
    Args:
        output_path: Path to generated files
        
    Returns:
        True if validation passes, False otherwise
    """
    output_path = Path(output_path)
    
    required_files = [
        '.cursorrules',
        '.cursor/rules/rules_manifest.json',
        '.cursor/commands/commands_manifest.json',
    ]
    
    for file_path in required_files:
        if not (output_path / file_path).exists():
            print(f"Warning: Required file not found: {file_path}")
            return False
    
    return True

