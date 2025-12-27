"""
Workspace generator module.

Generates .cursorrules, .cursor/ directory structure, and all workspace files.
"""

from pathlib import Path
from typing import Dict, Any
import yaml


def generate_workspace_files(context: Dict[str, Any], output_path: str):
    """
    Generate all workspace files from context.
    
    Args:
        context: Context variables dictionary
        output_path: Path where files should be generated
    """
    output_path = Path(output_path).resolve()
    
    # Generate .cursorrules
    from generators.rules_generator import generate_cursorrules
    generate_cursorrules(context, output_path)
    
    # Generate .cursor/ directory structure
    generate_cursor_directory(context, output_path)
    
    # Generate source_list.json
    from generators.manifest_generator import generate_source_list
    generate_source_list(context, output_path)
    
    print(f"Workspace files generated at: {output_path}")


def generate_cursor_directory(context: Dict[str, Any], output_path: Path):
    """
    Generate .cursor/ directory structure.
    
    Args:
        context: Context variables dictionary
        output_path: Path where files should be generated
    """
    cursor_dir = output_path / '.cursor'
    cursor_dir.mkdir(exist_ok=True)
    
    # Generate rules
    from generators.rules_generator import generate_rules
    generate_rules(context, cursor_dir)
    
    # Generate commands
    from generators.commands_generator import generate_commands
    generate_commands(context, cursor_dir)
    
    # Generate AGENTS.md
    from generators.manifest_generator import generate_agents_md
    generate_agents_md(context, cursor_dir)


def generate_project_scaffold(
    project_type: str,
    context: Dict[str, Any],
    output_path: Path
):
    """
    Generate complete project scaffolding.
    
    Args:
        project_type: Type of project
        context: Context variables dictionary
        output_path: Path where project should be created
    """
    from generators.workspace_generator import create_directory_structure
    from generators.workspace_generator import create_initial_files
    
    # Create directory structure
    create_directory_structure(project_type, output_path)
    
    # Create initial files
    create_initial_files(project_type, context, output_path)
    
    # Setup cursor workspace
    generate_workspace_files(context, output_path)


def create_directory_structure(project_type: str, output_path: Path):
    """
    Create directory structure for project type.
    
    Args:
        project_type: Type of project
        output_path: Path where project should be created
    """
    # Load project type configuration
    config_path = Path(__file__).parent.parent / 'config' / 'best_practices.yaml'
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    project_config = config.get('project_types', {}).get(project_type, {})
    structure = project_config.get('structure', [])
    
    for dir_path in structure:
        (output_path / dir_path).mkdir(parents=True, exist_ok=True)


def create_initial_files(project_type: str, context: Dict[str, Any], output_path: Path):
    """
    Create initial project files.
    
    Args:
        project_type: Type of project
        context: Context variables dictionary
        output_path: Path where project should be created
    """
    # This will be implemented based on project type
    # For now, create a basic README
    readme_path = output_path / 'README.md'
    if not readme_path.exists():
        readme_content = f"# {context.get('project_name', 'New Project')}\n\n"
        readme_content += f"Project type: {project_type}\n"
        readme_content += f"Primary language: {context.get('primary_language', 'unknown')}\n"
        readme_path.write_text(readme_content)

