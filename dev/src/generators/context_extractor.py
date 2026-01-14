"""
Context extractor module.

Parses projectFile.md and extracts context variables for template population.
"""

from pathlib import Path
from typing import Dict, Any, Optional
from generators.project_file_manager import load_project_file


def extract_context_from_project_file(project_root: Optional[str] = None) -> Dict[str, Any]:
    """
    Extract context variables from projectFile.md.
    
    Args:
        project_root: Project root directory (default: current directory)
        
    Returns:
        Context dictionary for template population
    """
    project_data = load_project_file(project_root)
    
    if project_data is None:
        raise FileNotFoundError("projectFile.md not found. Run analysis first.")
    
    # Convert project file data to context format expected by template engine
    context = {
        'project_name': project_data.get('project_name', 'Project'),
        'project_type': project_data.get('project_type', 'unknown'),
        'primary_language': project_data.get('primary_language', 'unknown'),
        'frameworks': project_data.get('frameworks', []),
        'languages': project_data.get('languages', []),
        'technologies': project_data.get('technologies', 'Unknown'),
        'architecture': project_data.get('architecture', 'unknown'),
        'deployment_type': project_data.get('deployment_type', 'unknown'),
        'coding_standards': project_data.get('coding_standards', {}),
        'file_organization': project_data.get('file_organization', 'standard'),
        'testing_framework': project_data.get('testing_framework', 'unknown'),
        'services': project_data.get('services', []),
        'ports': project_data.get('ports', []),
        'databases': project_data.get('databases', []),
        'networking': project_data.get('networking', {}),
        'project_description': project_data.get('project_description', ''),
        'project_purpose': project_data.get('project_purpose', ''),
        'key_concepts': project_data.get('key_concepts', []),
        'documentation_sources': project_data.get('documentation_sources', []),
        'containerization': project_data.get('containerization', []),
        'orchestration': project_data.get('orchestration', []),
        'cloud_platforms': project_data.get('cloud_platforms', []),
        'linting_tools': project_data.get('linting_tools', []),
        'formatting_tools': project_data.get('formatting_tools', []),
        'build_tools': project_data.get('build_tools', []),
    }
    
    # Extract framework if frameworks list is not empty
    if context['frameworks'] and not context.get('framework'):
        context['framework'] = context['frameworks'][0]
    
    return context


def merge_context_with_analysis(project_file_context: Dict[str, Any], 
                               analysis_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge context from projectFile.md with fresh analysis results.
    
    Args:
        project_file_context: Context from projectFile.md
        analysis_context: Context from fresh analysis
        
    Returns:
        Merged context dictionary (analysis takes precedence)
    """
    merged = project_file_context.copy()
    
    # Update with analysis results (analysis takes precedence)
    merged.update(analysis_context)
    
    # Preserve metadata from project file if present
    if 'metadata' in project_file_context:
        merged['metadata'] = project_file_context['metadata']
    
    return merged


def validate_context(context: Dict[str, Any]) -> tuple[bool, list[str]]:
    """
    Validate that context has required variables for template population.
    
    Args:
        context: Context dictionary
        
    Returns:
        Tuple of (is_valid, list_of_missing_variables)
    """
    required_variables = ['project_name', 'project_type', 'primary_language']
    missing = []
    
    for var in required_variables:
        if var not in context or not context[var] or context[var] == 'unknown':
            missing.append(var)
    
    return (len(missing) == 0, missing)
