"""
Rule content generator module.

Generates actual rule content files based on project type, language, and framework.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional


def generate_rule_content(
    level: int,
    context: Dict[str, Any],
    template_dir: Path
) -> Optional[str]:
    """
    Generate rule content for a specific level.
    
    Args:
        level: Rule level (1-5)
        context: Context variables dictionary
        template_dir: Path to templates directory
        
    Returns:
        Generated rule content or None if template not found
    """
    template_map = {
        1: 'level1-core.mdc.template',
        2: 'level2-architecture.mdc.template',
        3: 'level3-project-type.mdc.template',
        4: 'level4-language.mdc.template',
        5: 'level5-framework.mdc.template',
    }
    
    template_name = template_map.get(level)
    if not template_name:
        return None
    
    template_path = template_dir / '.cursor' / 'rules' / template_name
    
    if template_path.exists():
        from generators.template_engine import load_template, replace_placeholders
        template = load_template(str(template_path))
        content = replace_placeholders(template, context)
        return content
    
    # Generate fallback content if template doesn't exist
    return generate_fallback_rule_content(level, context)


def generate_fallback_rule_content(level: int, context: Dict[str, Any]) -> str:
    """
    Generate fallback rule content when template is missing.
    
    Args:
        level: Rule level
        context: Context variables dictionary
        
    Returns:
        Fallback rule content
    """
    project_name = context.get('project_name', 'Project')
    
    if level == 1:
        return f"""# Level 1: Core Rules for {project_name}

## Zero-Assumption Principles
- Always reference official documentation before making recommendations
- Cite sources for all architectural decisions
- Never proceed without documentation backing
- Extract all variables explicitly - no guessing
- Never modify original reference files

## General Best Practices
- Use real, network-resolvable hostnames (avoid localhost/127.0.0.1 unless explicitly requested)
- Follow project coding standards: {context.get('coding_standards', 'unknown')}
- Maintain consistent file organization: {context.get('file_organization', 'standard')}
- Write comprehensive tests using: {context.get('testing_framework', 'unknown')}
"""
    
    elif level == 2:
        return f"""# Level 2: Architecture Rules for {project_name}

## Architecture Pattern
- Architecture: {context.get('architecture', 'unknown')}
- Deployment Type: {context.get('deployment_type', 'unknown')}
- Networking: {context.get('networking', 'None')}

## Design Principles
- Follow established architecture patterns for {context.get('architecture', 'the project')}
- Maintain separation of concerns
- Use appropriate design patterns for the architecture
"""
    
    elif level == 3:
        project_type = context.get('project_type', 'unknown')
        return f"""# Level 3: Project Type Rules for {project_name}

## Project Type: {project_type}

## Project-Specific Guidelines
- Follow best practices for {project_type} projects
- Maintain project structure appropriate for {project_type}
"""
    
    elif level == 4:
        primary_language = context.get('primary_language', 'unknown')
        return f"""# Level 4: Language-Specific Rules for {project_name}

## Primary Language: {primary_language}

## Language-Specific Guidelines
- Follow {primary_language} best practices and conventions
- Use appropriate language-specific tools and patterns
"""
    
    elif level == 5:
        framework = context.get('framework', 'unknown')
        return f"""# Level 5: Framework-Specific Rules for {project_name}

## Framework: {framework}

## Framework-Specific Guidelines
- Follow {framework} best practices and conventions
- Use framework-specific patterns and idioms
"""
    
    return ""


def get_required_rule_levels(context: Dict[str, Any]) -> List[int]:
    """
    Determine which rule levels should be generated based on context.
    
    Args:
        context: Context variables dictionary
        
    Returns:
        List of rule levels to generate
    """
    levels = [1, 2]  # Always generate level 1 and 2
    
    # Level 3: Project type
    if context.get('project_type') and context.get('project_type') != 'unknown':
        levels.append(3)
    
    # Level 4: Language
    if context.get('primary_language') and context.get('primary_language') != 'unknown':
        levels.append(4)
    
    # Level 5: Framework
    if context.get('framework') and context.get('framework') != 'unknown':
        levels.append(5)
    
    return levels


def generate_all_rule_files(
    context: Dict[str, Any],
    rules_dir: Path,
    template_dir: Path
) -> List[str]:
    """
    Generate all rule files based on context.
    
    Args:
        context: Context variables dictionary
        rules_dir: Path to .cursor/rules directory
        template_dir: Path to templates directory
        
    Returns:
        List of generated rule file names
    """
    generated_files = []
    required_levels = get_required_rule_levels(context)
    
    for level in required_levels:
        content = generate_rule_content(level, context, template_dir)
        if content:
            filename = f"level{level}-{get_level_name(level)}.mdc"
            file_path = rules_dir / filename
            file_path.write_text(content)
            generated_files.append(filename)
    
    return generated_files


def get_level_name(level: int) -> str:
    """Get the name component for a rule level."""
    names = {
        1: 'core',
        2: 'architecture',
        3: 'project-type',
        4: 'language',
        5: 'framework',
    }
    return names.get(level, 'unknown')


