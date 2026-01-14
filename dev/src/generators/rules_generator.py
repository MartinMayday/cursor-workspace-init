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
    from generators.template_engine import load_template, replace_placeholders, validate_template_context
    from generators.tailoring_engine import enhance_context_with_tailoring
    
    # Enhance context with tailoring
    config_dir = Path(__file__).parent.parent / 'config'
    enhanced_context = enhance_context_with_tailoring(context, config_dir)
    
    template_path = Path(__file__).parent.parent / 'templates' / '.cursorrules.template'
    
    if template_path.exists():
        template = load_template(str(template_path))
        
        # Validate context before generation
        is_valid, missing = validate_template_context(template, enhanced_context)
        if not is_valid:
            print(f"Warning: Missing context variables: {missing}")
            print("Proceeding with defaults...")
        
        content = replace_placeholders(template, enhanced_context)
        (output_path / '.cursorrules').write_text(content)
    else:
        # Generate basic .cursorrules if template doesn't exist
        generate_basic_cursorrules(enhanced_context, output_path)


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
    
    # Enhance context with tailoring
    from generators.tailoring_engine import enhance_context_with_tailoring
    config_dir = Path(__file__).parent.parent / 'config'
    enhanced_context = enhance_context_with_tailoring(context, config_dir)
    
    # Generate actual rule content files FIRST
    from generators.rule_content_generator import generate_all_rule_files
    template_dir = Path(__file__).parent.parent / 'templates'
    
    generated_files = generate_all_rule_files(enhanced_context, rules_dir, template_dir)
    
    # Generate rules_manifest.json AFTER rule files are created, based on what was actually generated
    from generators.manifest_generator import generate_rules_manifest
    generate_rules_manifest(enhanced_context, rules_dir, generated_files=generated_files)
    
    if generated_files:
        print(f"Generated {len(generated_files)} rule files: {', '.join(generated_files)}")
    else:
        print("Warning: No rule files were generated")

