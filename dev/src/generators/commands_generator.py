"""
Commands generator module.

Generates .cursor/commands/ files.
"""

from pathlib import Path
from typing import Dict, Any


def generate_commands(context: Dict[str, Any], cursor_dir: Path):
    """
    Generate .cursor/commands/ files.
    
    Args:
        context: Context variables dictionary
        cursor_dir: Path to .cursor directory
    """
    commands_dir = cursor_dir / 'commands'
    commands_dir.mkdir(exist_ok=True)
    
    # Generate actual command content files FIRST
    from generators.command_content_generator import generate_all_command_files
    template_dir = Path(__file__).parent.parent / 'templates'
    
    generated_files = generate_all_command_files(context, commands_dir, template_dir)
    
    # Generate commands_manifest.json AFTER command files are created, based on what was actually generated
    from generators.manifest_generator import generate_commands_manifest
    generate_commands_manifest(context, commands_dir, generated_files=generated_files)
    
    if generated_files:
        print(f"Generated {len(generated_files)} command files: {', '.join(generated_files)}")
    else:
        print("Warning: No command files were generated")

