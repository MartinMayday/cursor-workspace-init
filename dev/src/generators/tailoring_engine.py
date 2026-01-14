"""
Tailoring engine module.

Generates project-specific, tailored rules and configurations based on
project type, language, framework, and architecture.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml


def load_tailoring_config(config_dir: Path) -> Dict[str, Any]:
    """
    Load tailoring configuration files.
    
    Args:
        config_dir: Path to config directory
        
    Returns:
        Dictionary with tailoring configurations
    """
    config = {}
    
    # Load language standards
    language_standards_path = config_dir / 'language_standards.yaml'
    if language_standards_path.exists():
        try:
            with open(language_standards_path, 'r') as f:
                config['language_standards'] = yaml.safe_load(f) or {}
        except:
            config['language_standards'] = {}
    else:
        config['language_standards'] = {}
    
    # Load framework rules
    framework_rules_path = config_dir / 'framework_rules.yaml'
    if framework_rules_path.exists():
        try:
            with open(framework_rules_path, 'r') as f:
                config['framework_rules'] = yaml.safe_load(f) or {}
        except:
            config['framework_rules'] = {}
    else:
        config['framework_rules'] = {}
    
    # Load best practices
    best_practices_path = config_dir / 'best_practices.yaml'
    if best_practices_path.exists():
        try:
            with open(best_practices_path, 'r') as f:
                best_practices = yaml.safe_load(f) or {}
                config['project_types'] = best_practices.get('project_types', {})
                config['frameworks'] = best_practices.get('frameworks', {})
        except:
            config['project_types'] = {}
            config['frameworks'] = {}
    else:
        config['project_types'] = {}
        config['frameworks'] = {}
    
    return config


def get_language_specific_rules(
    language: str,
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Get language-specific rules and standards.
    
    Args:
        language: Primary language
        config: Tailoring configuration
        
    Returns:
        Dictionary with language-specific rules
    """
    language_standards = config.get('language_standards', {})
    return language_standards.get(language, {})


def get_framework_specific_rules(
    framework: str,
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Get framework-specific rules and best practices.
    
    Args:
        framework: Framework name
        config: Tailoring configuration
        
    Returns:
        Dictionary with framework-specific rules
    """
    framework_rules = config.get('framework_rules', {})
    return framework_rules.get(framework, {})


def get_project_type_specific_rules(
    project_type: str,
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Get project type-specific rules and patterns.
    
    Args:
        project_type: Project type
        config: Tailoring configuration
        
    Returns:
        Dictionary with project type-specific rules
    """
    project_types = config.get('project_types', {})
    return project_types.get(project_type, {})


def get_architecture_specific_rules(
    architecture: str,
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Get architecture-specific rules and patterns.
    
    Args:
        architecture: Architecture pattern
        config: Tailoring configuration
        
    Returns:
        Dictionary with architecture-specific rules
    """
    # Architecture rules can be derived from project types
    project_types = config.get('project_types', {})
    
    # Map architecture to project type if applicable
    architecture_map = {
        'microservices': 'microservices',
        'monorepo': 'monorepo',
        'full_stack': 'full_stack',
        'spa': 'spa',
        'api': 'api',
        'cli': 'cli',
    }
    
    project_type = architecture_map.get(architecture, architecture)
    return project_types.get(project_type, {})


def enhance_context_with_tailoring(
    context: Dict[str, Any],
    config_dir: Path
) -> Dict[str, Any]:
    """
    Enhance context with tailored rules and best practices.
    
    Args:
        context: Original context dictionary
        config_dir: Path to config directory
        
    Returns:
        Enhanced context with tailoring information
    """
    enhanced = context.copy()
    config = load_tailoring_config(config_dir)
    
    # Add language-specific rules
    primary_language = context.get('primary_language', 'unknown')
    if primary_language != 'unknown':
        language_rules = get_language_specific_rules(primary_language, config)
        if language_rules:
            enhanced['language_specific_rules'] = language_rules
            # Enhance coding standards if not set
            if not enhanced.get('coding_standards') or enhanced.get('coding_standards') == 'unknown':
                standards = language_rules.get('coding_standards', {})
                if standards:
                    enhanced['coding_standards'] = standards.get('primary', 'unknown')
    
    # Add framework-specific rules
    framework = context.get('framework', 'unknown')
    if framework != 'unknown':
        framework_rules = get_framework_specific_rules(framework, config)
        if framework_rules:
            enhanced['framework_specific_rules'] = framework_rules
    
    # Add project type-specific rules
    project_type = context.get('project_type', 'unknown')
    if project_type != 'unknown':
        project_type_rules = get_project_type_specific_rules(project_type, config)
        if project_type_rules:
            enhanced['project_type_specific_rules'] = project_type_rules
    
    # Add architecture-specific rules
    architecture = context.get('architecture', 'unknown')
    if architecture != 'unknown':
        architecture_rules = get_architecture_specific_rules(architecture, config)
        if architecture_rules:
            enhanced['architecture_specific_rules'] = architecture_rules
    
    return enhanced


def generate_tailored_rules(
    context: Dict[str, Any],
    config_dir: Path
) -> Dict[str, Any]:
    """
    Generate tailored rules based on project characteristics.
    
    Args:
        context: Context variables dictionary
        config_dir: Path to config directory
        
    Returns:
        Dictionary with tailored rules
    """
    tailored = {}
    config = load_tailoring_config(config_dir)
    
    # Get language-specific best practices
    primary_language = context.get('primary_language', 'unknown')
    if primary_language != 'unknown':
        language_rules = get_language_specific_rules(primary_language, config)
        if language_rules:
            tailored['language_best_practices'] = language_rules.get('best_practices', [])
            tailored['language_patterns'] = language_rules.get('patterns', [])
            tailored['language_anti_patterns'] = language_rules.get('anti_patterns', [])
    
    # Get framework-specific best practices
    framework = context.get('framework', 'unknown')
    if framework != 'unknown':
        framework_rules = get_framework_specific_rules(framework, config)
        if framework_rules:
            tailored['framework_best_practices'] = framework_rules.get('best_practices', [])
            tailored['framework_patterns'] = framework_rules.get('patterns', [])
            tailored['framework_anti_patterns'] = framework_rules.get('anti_patterns', [])
    
    # Get project type-specific best practices
    project_type = context.get('project_type', 'unknown')
    if project_type != 'unknown':
        project_type_rules = get_project_type_specific_rules(project_type, config)
        if project_type_rules:
            tailored['project_type_best_practices'] = project_type_rules.get('best_practices', [])
            tailored['project_type_patterns'] = project_type_rules.get('patterns', [])
    
    return tailored


