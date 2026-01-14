"""
Script 1: Analyze existing repository and generate cursor workspace files.

This script orchestrates all analyzers to collect project information
and generate workspace files from templates.
"""

from pathlib import Path
from typing import Dict, Any, List


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
    from analyzers.coding_standards_detector import detect_coding_standards
    from analyzers.deployment_detector import detect_deployment
    from analyzers.content_analyzer import analyze_content
    from analyzers.code_structure_analyzer import analyze_code_structure
    from analyzers.existing_workspace_analyzer import analyze_existing_workspace
    from analyzers.pattern_detector import detect_patterns
    from analyzers.knowledge_extractor import extract_knowledge
    
    # Run all analyzers
    language_info = detect_language(repo_path)
    framework_info = detect_framework(repo_path)
    project_type_info = detect_project_type(repo_path)
    dependency_info = analyze_dependencies(repo_path)
    coding_standards_info = detect_coding_standards(repo_path)
    deployment_info = detect_deployment(repo_path)
    content_info = analyze_content(repo_path)
    code_structure_info = analyze_code_structure(repo_path)
    existing_workspace_info = analyze_existing_workspace(repo_path)
    patterns_info = detect_patterns(repo_path)
    knowledge_info = extract_knowledge(repo_path)
    
    # Format technology stack
    technologies = format_technology_stack(framework_info.get('frameworks', []), language_info.get('languages', []))
    
    # Collect results into context dictionary
    context = {
        'project_name': repo_path.name,
        'project_type': project_type_info.get('type', 'unknown'),
        'primary_language': language_info.get('primary', 'unknown'),
        'languages': language_info.get('languages', []),
        'framework': framework_info.get('framework', 'unknown'),
        'frameworks': framework_info.get('frameworks', []),
        'build_tools': framework_info.get('build_tools', []),
        'technologies': technologies,  # Formatted technology stack
        'dependencies': dependency_info.get('dependencies', []),
        'testing_framework': dependency_info.get('testing', 'unknown'),
        'linting_tools': dependency_info.get('linting', []),
        'formatting_tools': dependency_info.get('formatting', []),
        'databases': dependency_info.get('databases', []),
        'services': project_type_info.get('services', []),
        'ports': project_type_info.get('ports', []),
        'architecture': project_type_info.get('architecture', 'unknown'),
        'file_organization': project_type_info.get('file_organization', 'standard'),
        # Coding standards
        'coding_standards': coding_standards_info.get('style_guide', 'unknown'),
        'line_length': coding_standards_info.get('line_length'),
        'indentation': coding_standards_info.get('indentation'),
        # Deployment
        'deployment_type': deployment_info.get('deployment_type', 'unknown'),
        'containerization': deployment_info.get('containerization', []),
        'orchestration': deployment_info.get('orchestration', []),
        'cloud_platforms': deployment_info.get('cloud_platforms', []),
        'networking': deployment_info.get('networking', {}),
        # Content
        'project_description': content_info.get('project_description', ''),
        'project_purpose': content_info.get('project_purpose', ''),
        'key_concepts': content_info.get('key_concepts', []),
        'documentation_sources': content_info.get('documentation_sources', []),
        # Code structure
        'import_patterns': code_structure_info.get('import_patterns', {}),
        'architecture_patterns': code_structure_info.get('architecture_patterns', []),
        'common_modules': code_structure_info.get('common_modules', []),
        'code_patterns': code_structure_info.get('patterns_detected', []),
        # Existing workspace
        'has_existing_workspace': existing_workspace_info.get('has_cursorrules', False) or existing_workspace_info.get('has_cursor_dir', False),
        'existing_workspace': existing_workspace_info,
        # Patterns
        'common_patterns': patterns_info.get('common_patterns', []),
        'anti_patterns': patterns_info.get('anti_patterns', []),
        'conventions': patterns_info.get('conventions', []),
        # Knowledge extraction
        'domain_terms': knowledge_info.get('domain_terms', []),
        'project_domain': knowledge_info.get('project_domain', ''),
        'extracted_concepts': knowledge_info.get('key_concepts', []),
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


def format_technology_stack(frameworks: List[str], languages: List[str]) -> str:
    """
    Format technology stack as a readable string.
    
    Args:
        frameworks: List of framework names
        languages: List of language names
        
    Returns:
        Formatted technology stack string
    """
    stack_parts = []
    
    # Add languages
    if languages:
        stack_parts.extend([lang.capitalize() for lang in languages])
    
    # Add frameworks
    if frameworks:
        # Capitalize framework names properly
        formatted_frameworks = []
        for fw in frameworks:
            if fw == 'nextjs':
                formatted_frameworks.append('Next.js')
            elif fw == 'nestjs':
                formatted_frameworks.append('NestJS')
            else:
                formatted_frameworks.append(fw.capitalize())
        stack_parts.extend(formatted_frameworks)
    
    if stack_parts:
        return ', '.join(stack_parts)
    
    return 'Unknown'


def generate_workspace_files(context: Dict[str, Any], output_path: str, enhance_mode: bool = True):
    """
    Generate workspace files from context.
    
    Args:
        context: Context variables dictionary
        output_path: Path where files should be generated
        enhance_mode: If True, enhance existing files; if False, overwrite
    """
    from generators.workspace_generator import generate_workspace_files as gen_workspace
    gen_workspace(context, output_path, enhance_mode=enhance_mode)


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

