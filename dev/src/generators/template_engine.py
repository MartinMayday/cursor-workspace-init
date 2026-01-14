"""
Template engine module.

Handles loading templates and replacing placeholders with context variables.
"""

from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
import re


def load_template(template_path: str) -> str:
    """
    Load a template file.
    
    Args:
        template_path: Path to template file
        
    Returns:
        Template content as string
    """
    template_file = Path(template_path)
    if not template_file.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")
    
    return template_file.read_text()


def normalize_context(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize context variables with defaults and computed values.
    
    Args:
        context: Raw context dictionary
        
    Returns:
        Normalized context with defaults and computed values
    """
    normalized = context.copy()
    
    # Define default values for common variables
    defaults = {
        'project_name': 'Project',
        'project_type': 'unknown',
        'primary_language': 'unknown',
        'framework': 'unknown',
        'frameworks': [],
        'technologies': 'Unknown',
        'architecture': 'unknown',
        'deployment_type': 'unknown',
        'coding_standards': 'unknown',
        'file_organization': 'standard',
        'testing_framework': 'unknown',
        'services': [],
        'ports': [],
        'databases': [],
        'networking': {},
        'project_description': '',
        'project_purpose': '',
        'key_concepts': [],
        'documentation_sources': [],
        'containerization': [],
        'orchestration': [],
        'cloud_platforms': [],
        'linting_tools': [],
        'formatting_tools': [],
        'build_tools': [],
    }
    
    # Apply defaults for missing values
    for key, default_value in defaults.items():
        if key not in normalized or normalized[key] is None:
            normalized[key] = default_value
    
    # Compute derived values
    # Format technologies if not already formatted
    if 'technologies' not in normalized or normalized['technologies'] == 'Unknown':
        frameworks = normalized.get('frameworks', [])
        languages = normalized.get('languages', [])
        if frameworks or languages:
            tech_parts = []
            if languages:
                tech_parts.extend([lang.capitalize() for lang in languages])
            if frameworks:
                formatted_frameworks = []
                for fw in frameworks:
                    if fw == 'nextjs':
                        formatted_frameworks.append('Next.js')
                    elif fw == 'nestjs':
                        formatted_frameworks.append('NestJS')
                    else:
                        formatted_frameworks.append(fw.capitalize())
                tech_parts.extend(formatted_frameworks)
            normalized['technologies'] = ', '.join(tech_parts) if tech_parts else 'Unknown'
    
    # Format networking as string if it's a dict
    if isinstance(normalized.get('networking'), dict):
        networking = normalized['networking']
        if networking:
            parts = []
            if 'ports' in networking and networking['ports']:
                parts.append(f"Ports: {', '.join([str(p) for p in networking['ports']])}")
            if 'networks' in networking and networking['networks']:
                parts.append(f"Networks: {', '.join(networking['networks'])}")
            if 'reverse_proxy' in networking:
                parts.append(f"Reverse Proxy: {networking['reverse_proxy']}")
            normalized['networking'] = '; '.join(parts) if parts else 'None'
    
    return normalized


def get_placeholder_mapping() -> Dict[str, str]:
    """
    Get mapping from placeholder names to context variable names.
    
    Returns:
        Dictionary mapping placeholder names to context keys
    """
    return {
        'PROJECT_NAME': 'project_name',
        'PRIMARY_LANGUAGE': 'primary_language',
        'PROJECT_TYPE': 'project_type',
        'CODING_STANDARDS': 'coding_standards',
        'FILE_ORGANIZATION': 'file_organization',
        'TESTING_FRAMEWORK': 'testing_framework',
        'ARCHITECTURE': 'architecture',
        'DEPLOYMENT_TYPE': 'deployment_type',
        'NETWORKING': 'networking',
        'TECHNOLOGIES': 'technologies',
        'SERVICES': 'services',
        'PORTS': 'ports',
        'DATABASE': 'databases',
        'FRAMEWORK': 'framework',
        'FRAMEWORKS': 'frameworks',
        'LANGUAGES': 'languages',
        'PROJECT_DESCRIPTION': 'project_description',
        'PROJECT_PURPOSE': 'project_purpose',
        'KEY_CONCEPTS': 'key_concepts',
        'DOCUMENTATION_SOURCES': 'documentation_sources',
        'LINTING_TOOLS': 'linting_tools',
        'FORMATTING_TOOLS': 'formatting_tools',
        'CONTAINERIZATION': 'containerization',
        'ORCHESTRATION': 'orchestration',
        'CLOUD_PLATFORMS': 'cloud_platforms',
        'BUILD_TOOLS': 'build_tools',
    }


def process_conditional_placeholders(template: str, context: Dict[str, Any]) -> str:
    """
    Process conditional placeholders like <PLACEHOLDER: IF_PYTHON>.
    
    Args:
        template: Template string with conditional placeholders
        context: Context variables dictionary
        
    Returns:
        Template with conditional placeholders processed
    """
    normalized_context = normalize_context(context)
    result = template
    
    # Handle conditional placeholders
    # Format: <PLACEHOLDER: IF_CONDITION>...content...</PLACEHOLDER: ENDIF_CONDITION>
    conditional_pattern = r'<PLACEHOLDER:\s*IF_(\w+)>(.*?)<PLACEHOLDER:\s*ENDIF_\1>'
    
    def process_conditional(match):
        condition = match.group(1).lower()
        content = match.group(2)
        
        # Check various conditions
        if condition == 'python':
            if normalized_context.get('primary_language') == 'python':
                return content
        elif condition == 'javascript':
            lang = normalized_context.get('primary_language', '')
            if lang in ['javascript', 'typescript']:
                return content
        elif condition == 'go':
            if normalized_context.get('primary_language') == 'go':
                return content
        elif condition == 'rust':
            if normalized_context.get('primary_language') == 'rust':
                return content
        elif condition == 'fastapi':
            if normalized_context.get('framework') == 'fastapi':
                return content
        elif condition == 'django':
            if normalized_context.get('framework') == 'django':
                return content
        elif condition == 'flask':
            if normalized_context.get('framework') == 'flask':
                return content
        elif condition == 'react':
            if normalized_context.get('framework') == 'react':
                return content
        elif condition == 'nextjs':
            if normalized_context.get('framework') == 'nextjs':
                return content
        elif condition == 'express':
            if normalized_context.get('framework') == 'express':
                return content
        elif condition == 'nestjs':
            if normalized_context.get('framework') == 'nestjs':
                return content
        elif condition == 'microservices':
            if normalized_context.get('project_type') == 'microservices':
                return content
        elif condition == 'monorepo':
            if normalized_context.get('project_type') == 'monorepo':
                return content
        elif condition == 'spa':
            if normalized_context.get('project_type') == 'spa':
                return content
        elif condition == 'api':
            if normalized_context.get('project_type') == 'api':
                return content
        elif condition == 'full_stack':
            if normalized_context.get('project_type') == 'full_stack':
                return content
        elif condition == 'cli':
            if normalized_context.get('project_type') == 'cli':
                return content
        elif condition == 'docker':
            containerization = normalized_context.get('containerization', [])
            if containerization and 'docker' in str(containerization).lower():
                return content
        elif condition == 'kubernetes':
            orchestration = normalized_context.get('orchestration', [])
            if orchestration and 'kubernetes' in str(orchestration).lower():
                return content
        elif condition == 'aws':
            cloud_platforms = normalized_context.get('cloud_platforms', [])
            if cloud_platforms and 'aws' in str(cloud_platforms).lower():
                return content
        elif condition == 'azure':
            cloud_platforms = normalized_context.get('cloud_platforms', [])
            if cloud_platforms and 'azure' in str(cloud_platforms).lower():
                return content
        elif condition == 'gcp':
            cloud_platforms = normalized_context.get('cloud_platforms', [])
            if cloud_platforms and 'gcp' in str(cloud_platforms).lower():
                return content
        elif condition == 'vercel':
            cloud_platforms = normalized_context.get('cloud_platforms', [])
            if cloud_platforms and 'vercel' in str(cloud_platforms).lower():
                return content
        elif condition == 'netlify':
            cloud_platforms = normalized_context.get('cloud_platforms', [])
            if cloud_platforms and 'netlify' in str(cloud_platforms).lower():
                return content
        elif condition == 'heroku':
            cloud_platforms = normalized_context.get('cloud_platforms', [])
            if cloud_platforms and 'heroku' in str(cloud_platforms).lower():
                return content
        
        # Condition not met, remove content
        return ''
    
    result = re.sub(conditional_pattern, process_conditional, result, flags=re.DOTALL)
    
    # Also handle simple conditional placeholders that should be replaced with content or removed
    simple_conditional_pattern = r'<PLACEHOLDER:\s*IF_(\w+)>'
    
    def process_simple_conditional(match):
        condition = match.group(1).lower()
        # Check conditions same as above
        if condition == 'python' and normalized_context.get('primary_language') == 'python':
            return ''  # Remove placeholder, keep following content
        elif condition == 'javascript':
            lang = normalized_context.get('primary_language', '')
            if lang in ['javascript', 'typescript']:
                return ''
        elif condition == 'go' and normalized_context.get('primary_language') == 'go':
            return ''
        elif condition == 'rust' and normalized_context.get('primary_language') == 'rust':
            return ''
        elif condition == 'fastapi' and normalized_context.get('framework') == 'fastapi':
            return ''
        elif condition == 'django' and normalized_context.get('framework') == 'django':
            return ''
        elif condition == 'flask' and normalized_context.get('framework') == 'flask':
            return ''
        elif condition == 'react' and normalized_context.get('framework') == 'react':
            return ''
        elif condition == 'nextjs' and normalized_context.get('framework') == 'nextjs':
            return ''
        elif condition == 'express' and normalized_context.get('framework') == 'express':
            return ''
        elif condition == 'nestjs' and normalized_context.get('framework') == 'nestjs':
            return ''
        elif condition == 'microservices' and normalized_context.get('project_type') == 'microservices':
            return ''
        elif condition == 'monorepo' and normalized_context.get('project_type') == 'monorepo':
            return ''
        elif condition == 'spa' and normalized_context.get('project_type') == 'spa':
            return ''
        elif condition == 'api' and normalized_context.get('project_type') == 'api':
            return ''
        elif condition == 'full_stack' and normalized_context.get('project_type') == 'full_stack':
            return ''
        elif condition == 'cli' and normalized_context.get('project_type') == 'cli':
            return ''
        elif condition == 'docker':
            containerization = normalized_context.get('containerization', [])
            if containerization and 'docker' in str(containerization).lower():
                return ''
        elif condition == 'kubernetes':
            orchestration = normalized_context.get('orchestration', [])
            if orchestration and 'kubernetes' in str(orchestration).lower():
                return ''
        elif condition == 'aws':
            cloud_platforms = normalized_context.get('cloud_platforms', [])
            if cloud_platforms and 'aws' in str(cloud_platforms).lower():
                return ''
        elif condition == 'azure':
            cloud_platforms = normalized_context.get('cloud_platforms', [])
            if cloud_platforms and 'azure' in str(cloud_platforms).lower():
                return ''
        elif condition == 'gcp':
            cloud_platforms = normalized_context.get('cloud_platforms', [])
            if cloud_platforms and 'gcp' in str(cloud_platforms).lower():
                return ''
        elif condition == 'vercel':
            cloud_platforms = normalized_context.get('cloud_platforms', [])
            if cloud_platforms and 'vercel' in str(cloud_platforms).lower():
                return ''
        elif condition == 'netlify':
            cloud_platforms = normalized_context.get('cloud_platforms', [])
            if cloud_platforms and 'netlify' in str(cloud_platforms).lower():
                return ''
        elif condition == 'heroku':
            cloud_platforms = normalized_context.get('cloud_platforms', [])
            if cloud_platforms and 'heroku' in str(cloud_platforms).lower():
                return ''
        
        # Condition not met, remove placeholder and following content until next section
        return ''
    
    result = re.sub(simple_conditional_pattern, process_simple_conditional, result)
    
    return result


def replace_placeholders(template: str, context: Dict[str, Any]) -> str:
    """
    Replace placeholders in template with context variables.
    
    Placeholder format: <PLACEHOLDER: VARIABLE_NAME>
    
    Args:
        template: Template string with placeholders
        context: Dictionary of context variables
        
    Returns:
        Template with placeholders replaced
    """
    # Normalize context first
    normalized_context = normalize_context(context)
    
    # Get placeholder mapping
    placeholder_map = get_placeholder_mapping()
    
    # Process conditional placeholders first
    result = process_conditional_placeholders(template, context)
    
    # Find all placeholders in format <PLACEHOLDER: VARIABLE_NAME>
    pattern = r'<PLACEHOLDER:\s*(\w+)>'
    
    def replace_match(match):
        var_name = match.group(1)
        
        # Skip conditional placeholders (already processed)
        if var_name.startswith('IF_') or var_name.startswith('ENDIF_'):
            return ''
        
        # Try mapping first
        if var_name in placeholder_map:
            context_key = placeholder_map[var_name]
            if context_key in normalized_context:
                value = normalized_context[context_key]
                return format_value(value)
        
        # Convert to context key format (lowercase with underscores)
        context_key = var_name.lower()
        
        # Try exact match
        if context_key in normalized_context:
            value = normalized_context[context_key]
            return format_value(value)
        
        # Try with underscores (handle camelCase placeholders)
        if '_' not in context_key:
            # Try adding underscores (e.g., PROJECT_NAME -> project_name)
            context_key = '_'.join(re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)', var_name)).lower()
            if context_key in normalized_context:
                value = normalized_context[context_key]
                return format_value(value)
        
        # Try camelCase version
        if '_' in context_key:
            camel_case = ''.join(word.capitalize() if i > 0 else word for i, word in enumerate(context_key.split('_')))
            if camel_case in normalized_context:
                return format_value(normalized_context[camel_case])
        
        # If not found, use default or return placeholder
        print(f"Warning: Context variable '{var_name}' not found, using default")
        return ''  # Return empty string instead of leaving placeholder
    
    result = re.sub(pattern, replace_match, result)
    
    return result


def format_value(value: Any) -> str:
    """
    Format a value for template replacement.
    
    Args:
        value: Value to format
        
    Returns:
        Formatted string
    """
    if value is None:
        return ''
    
    # Handle empty strings
    if isinstance(value, str) and not value.strip():
        return ''
    
    if isinstance(value, list):
        if not value:
            return 'None'
        # Format list items nicely
        formatted_items = [str(v) for v in value]
        if len(formatted_items) <= 3:
            return ', '.join(formatted_items)
        else:
            return ', '.join(formatted_items[:3]) + f', and {len(formatted_items) - 3} more'
    
    if isinstance(value, dict):
        if not value:
            return 'None'
        # Format dict as key-value pairs
        pairs = [f"{k}: {v}" for k, v in value.items()]
        return '; '.join(pairs)
    
    return str(value)


def validate_replacements(result: str) -> bool:
    """
    Validate that all placeholders have been replaced.
    
    Args:
        result: Result string after replacement
        
    Returns:
        True if all placeholders replaced, False otherwise
    """
    pattern = r'<PLACEHOLDER:\s*\w+>'
    remaining = re.findall(pattern, result)
    
    if remaining:
        print(f"Warning: {len(remaining)} placeholders not replaced: {remaining}")
        return False
    
    return True


def validate_template_context(template: str, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate that all placeholders in template have corresponding context variables.
    
    Args:
        template: Template string with placeholders
        context: Dictionary of context variables
        
    Returns:
        Tuple of (is_valid, missing_variables)
    """
    # Normalize context
    normalized_context = normalize_context(context)
    placeholder_map = get_placeholder_mapping()
    
    # Find all placeholders
    pattern = r'<PLACEHOLDER:\s*(\w+)>'
    placeholders = set(re.findall(pattern, template))
    
    missing = []
    for placeholder in placeholders:
        # Check mapping
        if placeholder in placeholder_map:
            context_key = placeholder_map[placeholder]
            if context_key not in normalized_context:
                missing.append(f"{placeholder} (maps to {context_key})")
            continue
        
        # Try direct lookup
        context_key = placeholder.lower()
        if context_key not in normalized_context:
            # Try with underscores
            if '_' not in context_key:
                context_key = '_'.join(re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)', placeholder)).lower()
            
            if context_key not in normalized_context:
                missing.append(placeholder)
    
    return (len(missing) == 0, missing)

