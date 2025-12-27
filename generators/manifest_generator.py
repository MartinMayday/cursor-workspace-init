"""
Manifest generator module.

Generates manifest files (rules_manifest.json, commands_manifest.json, etc.)
and other configuration files.
"""

from pathlib import Path
from typing import Dict, Any
import json


def generate_rules_manifest(context: Dict[str, Any], rules_dir: Path):
    """
    Generate rules_manifest.json.
    
    Args:
        context: Context variables dictionary
        rules_dir: Path to .cursor/rules directory
    """
    from generators.template_engine import load_template, replace_placeholders
    
    template_path = Path(__file__).parent.parent / 'templates' / '.cursor' / 'rules' / 'rules_manifest.json.template'
    
    if template_path.exists():
        template = load_template(str(template_path))
        content = replace_placeholders(template, context)
        manifest_path = rules_dir / 'rules_manifest.json'
        manifest_path.write_text(content)
    else:
        # Generate basic manifest if template doesn't exist
        manifest = {
            "rules": [
                {
                    "level": 1,
                    "file": "level1-core.mdc",
                    "description": "Core rules and principles"
                },
                {
                    "level": 2,
                    "file": "level2-architecture.mdc",
                    "description": "Architecture and design patterns"
                }
            ]
        }
        manifest_path = rules_dir / 'rules_manifest.json'
        manifest_path.write_text(json.dumps(manifest, indent=2))


def generate_commands_manifest(context: Dict[str, Any], commands_dir: Path):
    """
    Generate commands_manifest.json.
    
    Args:
        context: Context variables dictionary
        commands_dir: Path to .cursor/commands directory
    """
    from generators.template_engine import load_template, replace_placeholders
    
    template_path = Path(__file__).parent.parent / 'templates' / '.cursor' / 'commands' / 'commands_manifest.json.template'
    
    if template_path.exists():
        template = load_template(str(template_path))
        content = replace_placeholders(template, context)
        manifest_path = commands_dir / 'commands_manifest.json'
        manifest_path.write_text(content)
    else:
        # Generate basic manifest if template doesn't exist
        manifest = {
            "commands": []
        }
        manifest_path = commands_dir / 'commands_manifest.json'
        manifest_path.write_text(json.dumps(manifest, indent=2))


def generate_source_list(context: Dict[str, Any], output_path: Path):
    """
    Generate source_list.json.
    
    Args:
        context: Context variables dictionary
        output_path: Path where file should be generated
    """
    from generators.template_engine import load_template, replace_placeholders
    
    template_path = Path(__file__).parent.parent / 'templates' / 'source_list.json.template'
    
    if template_path.exists():
        template = load_template(str(template_path))
        content = replace_placeholders(template, context)
        source_list_path = output_path / 'source_list.json'
        source_list_path.write_text(content)
    else:
        # Generate basic source_list.json if template doesn't exist
        source_list = {
            "sources": []
        }
        source_list_path = output_path / 'source_list.json'
        source_list_path.write_text(json.dumps(source_list, indent=2))


def generate_agents_md(context: Dict[str, Any], cursor_dir: Path):
    """
    Generate AGENTS.md.
    
    Args:
        context: Context variables dictionary
        cursor_dir: Path to .cursor directory
    """
    from generators.template_engine import load_template, replace_placeholders
    
    template_path = Path(__file__).parent.parent / 'templates' / '.cursor' / 'AGENTS.md.template'
    
    if template_path.exists():
        template = load_template(str(template_path))
        content = replace_placeholders(template, context)
        (cursor_dir / 'AGENTS.md').write_text(content)
    else:
        # Generate basic AGENTS.md if template doesn't exist
        generate_basic_agents_md(context, cursor_dir)


def generate_basic_agents_md(context: Dict[str, Any], cursor_dir: Path):
    """
    Generate basic AGENTS.md without template.
    
    Args:
        context: Context variables dictionary
        cursor_dir: Path to .cursor directory
    """
    project_name = context.get('project_name', 'Project')
    
    content = f"""# Agents Configuration for {project_name}

## Project Context
- Project Name: {project_name}
- Primary Language: {context.get('primary_language', 'unknown')}
- Project Type: {context.get('project_type', 'unknown')}

## Agent Instructions
Follow the project's coding standards and best practices.
Reference official documentation for all recommendations.
"""
    (cursor_dir / 'AGENTS.md').write_text(content)

