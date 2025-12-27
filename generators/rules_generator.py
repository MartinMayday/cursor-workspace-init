"""
Rules generator module.

Generates .cursorrules and .cursor/rules/ files.
"""

from pathlib import Path
from typing import Dict, Any


def generate_cursorrules(context: Dict[str, Any], output_path: Path):
    """
    Generate .cursorrules file.
    
    Args:
        context: Context variables dictionary
        output_path: Path where file should be generated
    """
    from generators.template_engine import load_template, replace_placeholders
    
    template_path = Path(__file__).parent.parent / 'templates' / '.cursorrules.template'
    
    if template_path.exists():
        template = load_template(str(template_path))
        content = replace_placeholders(template, context)
        (output_path / '.cursorrules').write_text(content)
    else:
        # Generate basic .cursorrules if template doesn't exist
        generate_basic_cursorrules(context, output_path)


def generate_basic_cursorrules(context: Dict[str, Any], output_path: Path):
    """
    Generate basic .cursorrules file without template.
    
    Args:
        context: Context variables dictionary
        output_path: Path where file should be generated
    """
    project_name = context.get('project_name', 'Project')
    primary_language = context.get('primary_language', 'unknown')
    
    content = f"""# Cursor Rules for {project_name}

## Project Information
- Project Name: {project_name}
- Primary Language: {primary_language}
- Project Type: {context.get('project_type', 'unknown')}

## Best Practices
- Always reference official documentation before making recommendations
- Cite sources for all architectural decisions
- Extract all variables explicitly - no guessing
- Use real, network-resolvable hostnames (avoid localhost/127.0.0.1 unless explicitly requested)

## Code Standards
- Follow project coding standards
- Maintain consistent file organization
- Write comprehensive tests
"""
    (output_path / '.cursorrules').write_text(content)


def generate_rules(context: Dict[str, Any], cursor_dir: Path):
    """
    Generate .cursor/rules/ files.
    
    Args:
        context: Context variables dictionary
        cursor_dir: Path to .cursor directory
    """
    rules_dir = cursor_dir / 'rules'
    rules_dir.mkdir(exist_ok=True)
    
    # Generate rules_manifest.json
    from generators.manifest_generator import generate_rules_manifest
    generate_rules_manifest(context, rules_dir)
    
    # Generate rule files (level1, level2, etc.)
    # This will be expanded based on project type and requirements
    from generators.template_engine import load_template, replace_placeholders
    
    manifest_template_path = Path(__file__).parent.parent / 'templates' / '.cursor' / 'rules' / 'rules_manifest.json.template'
    if manifest_template_path.exists():
        template = load_template(str(manifest_template_path))
        content = replace_placeholders(template, context)
        (rules_dir / 'rules_manifest.json').write_text(content)

