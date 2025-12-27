"""
Template engine module.

Handles loading templates and replacing placeholders with context variables.
"""

from pathlib import Path
from typing import Dict, Any
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
    result = template
    
    # Find all placeholders in format <PLACEHOLDER: VARIABLE_NAME>
    pattern = r'<PLACEHOLDER:\s*(\w+)>'
    
    def replace_match(match):
        var_name = match.group(1)
        # Convert to context key format (lowercase with underscores)
        context_key = var_name.lower()
        
        # Try exact match first
        if context_key in context:
            value = context[context_key]
            return format_value(value)
        
        # Try with underscores
        if '_' in context_key:
            # Try camelCase version
            camel_case = ''.join(word.capitalize() if i > 0 else word for i, word in enumerate(context_key.split('_')))
            if camel_case in context:
                return format_value(context[camel_case])
        
        # If not found, return empty string or placeholder
        print(f"Warning: Context variable '{var_name}' not found, leaving placeholder")
        return match.group(0)  # Return original placeholder if not found
    
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
    
    if isinstance(value, list):
        if not value:
            return 'None'
        return ', '.join(str(v) for v in value)
    
    if isinstance(value, dict):
        return ', '.join(f"{k}: {v}" for k, v in value.items())
    
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

