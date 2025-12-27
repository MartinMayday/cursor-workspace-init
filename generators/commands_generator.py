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
    
    # Generate commands_manifest.json
    from generators.manifest_generator import generate_commands_manifest
    generate_commands_manifest(context, commands_dir)

