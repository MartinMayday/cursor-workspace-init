"""
Workspace enhancer module.

Detects and enhances existing Cursor workspace files instead of overwriting.
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
import shutil
from datetime import datetime


def should_enhance_existing(output_path: Path) -> bool:
    """
    Check if existing workspace files should be enhanced.
    
    Args:
        output_path: Path to check for existing workspace
        
    Returns:
        True if existing workspace found, False otherwise
    """
    cursorrules_exists = (output_path / '.cursorrules').exists()
    cursor_dir_exists = (output_path / '.cursor').exists() and (output_path / '.cursor').is_dir()
    
    return cursorrules_exists or cursor_dir_exists


def backup_existing_workspace(output_path: Path) -> Path:
    """
    Backup existing workspace files.
    
    Args:
        output_path: Path to workspace directory
        
    Returns:
        Path to backup directory
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = output_path / '.cursor' / 'backups' / f'backup_{timestamp}'
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # Backup .cursorrules
    cursorrules_path = output_path / '.cursorrules'
    if cursorrules_path.exists():
        backup_cursorrules = backup_dir / '.cursorrules'
        shutil.copy2(cursorrules_path, backup_cursorrules)
    
    # Backup .cursor directory
    cursor_dir = output_path / '.cursor'
    if cursor_dir.exists():
        # Don't backup the backups directory itself
        for item in cursor_dir.iterdir():
            if item.name != 'backups':
                backup_item = backup_dir / item.name
                if item.is_dir():
                    shutil.copytree(item, backup_item, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, backup_item)
    
    return backup_dir


def merge_cursorrules(existing_content: str, new_content: str) -> str:
    """
    Merge existing .cursorrules with new content.
    
    Args:
        existing_content: Existing .cursorrules content
        new_content: New .cursorrules content to merge
        
    Returns:
        Merged content
    """
    # Simple merge: append new sections that don't exist
    existing_sections = extract_sections(existing_content)
    new_sections = extract_sections(new_content)
    
    merged = existing_content
    
    # Add new sections that don't exist
    for section_name, section_content in new_sections.items():
        if section_name not in existing_sections:
            merged += f"\n\n{section_content}\n"
    
    return merged


def extract_sections(content: str) -> Dict[str, str]:
    """
    Extract sections from markdown content.
    
    Args:
        content: Markdown content
        
    Returns:
        Dictionary mapping section names to content
    """
    sections = {}
    lines = content.split('\n')
    current_section = None
    current_content = []
    
    for line in lines:
        if line.startswith('##'):
            # Save previous section
            if current_section:
                sections[current_section] = '\n'.join(current_content)
            # Start new section
            current_section = line.strip()
            current_content = [line]
        else:
            if current_section:
                current_content.append(line)
    
    # Save last section
    if current_section:
        sections[current_section] = '\n'.join(current_content)
    
    return sections


def enhance_workspace_files(context: Dict[str, Any], output_path: Path, enhance_mode: bool = True) -> bool:
    """
    Enhance existing workspace files or create new ones.
    
    Args:
        context: Context variables dictionary
        output_path: Path where files should be generated
        enhance_mode: If True, enhance existing files; if False, overwrite
        
    Returns:
        True if enhancement successful, False otherwise
    """
    output_path = Path(output_path).resolve()
    
    if not enhance_mode:
        # Just generate new files (overwrite mode)
        from generators.workspace_generator import generate_workspace_files
        generate_workspace_files(context, output_path)
        return True
    
    # Check if existing workspace
    if not should_enhance_existing(output_path):
        # No existing workspace, generate new
        from generators.workspace_generator import generate_workspace_files
        generate_workspace_files(context, output_path)
        return True
    
    # Backup existing workspace
    backup_dir = backup_existing_workspace(output_path)
    print(f"Backed up existing workspace to: {backup_dir}")
    
    # Enhance existing files
    enhance_cursorrules(context, output_path)
    enhance_cursor_directory(context, output_path)
    
    return True


def enhance_cursorrules(context: Dict[str, Any], output_path: Path):
    """
    Enhance existing .cursorrules file.
    
    Args:
        context: Context variables dictionary
        output_path: Path where file should be generated
    """
    cursorrules_path = output_path / '.cursorrules'
    
    if cursorrules_path.exists():
        existing_content = cursorrules_path.read_text()
        
        # Generate new content to temp location
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            from generators.rules_generator import generate_cursorrules
            generate_cursorrules(context, temp_path)
            temp_cursorrules = temp_path / '.cursorrules'
            if temp_cursorrules.exists():
                new_content = temp_cursorrules.read_text()
                # Merge
                merged = merge_cursorrules(existing_content, new_content)
                cursorrules_path.write_text(merged)
                print("Enhanced .cursorrules file")
    else:
        # No existing file, generate new
        from generators.rules_generator import generate_cursorrules
        generate_cursorrules(context, output_path)


def enhance_cursor_directory(context: Dict[str, Any], output_path: Path):
    """
    Enhance existing .cursor/ directory.
    
    Args:
        context: Context variables dictionary
        output_path: Path where files should be generated
    """
    cursor_dir = output_path / '.cursor'
    cursor_dir.mkdir(exist_ok=True)
    
    # Enhance rules (add new rule files, don't overwrite existing)
    enhance_rules(context, cursor_dir)
    
    # Enhance commands (add new command files, don't overwrite existing)
    enhance_commands(context, cursor_dir)
    
    # Update AGENTS.md (merge)
    enhance_agents_md(context, cursor_dir)


def enhance_rules(context: Dict[str, Any], cursor_dir: Path):
    """
    Enhance existing rules directory.
    
    Args:
        context: Context variables dictionary
        cursor_dir: Path to .cursor directory
    """
    rules_dir = cursor_dir / 'rules'
    rules_dir.mkdir(exist_ok=True)
    
    # Get existing rule files
    existing_files = set()
    if rules_dir.exists():
        existing_files = {f.name for f in rules_dir.iterdir() if f.is_file()}
    
    # Generate new rule files
    from generators.rules_generator import generate_rules
    generate_rules(context, cursor_dir)
    
    # Note: generate_rules will create new files, existing ones are preserved
    # The manifest will be updated to include both old and new files
    # The manifest will be generated in enhanced format with semantic_meaning,
    # use_when, conditions, and triggers for better AI agent decision-making


def enhance_commands(context: Dict[str, Any], cursor_dir: Path):
    """
    Enhance existing commands directory.
    
    Args:
        context: Context variables dictionary
        cursor_dir: Path to .cursor directory
    """
    commands_dir = cursor_dir / 'commands'
    commands_dir.mkdir(exist_ok=True)
    
    # Get existing command files
    existing_files = set()
    if commands_dir.exists():
        existing_files = {f.name for f in commands_dir.iterdir() if f.is_file()}
    
    # Generate new command files
    from generators.commands_generator import generate_commands
    generate_commands(context, cursor_dir)
    
    # Note: generate_commands will create new files, existing ones are preserved
    # The manifest will be generated in enhanced format with semantic_meaning,
    # use_when, conditions, and triggers for better AI agent decision-making


def enhance_agents_md(context: Dict[str, Any], cursor_dir: Path):
    """
    Enhance existing AGENTS.md file.
    
    Args:
        context: Context variables dictionary
        cursor_dir: Path to .cursor directory
    """
    agents_path = cursor_dir / 'AGENTS.md'
    
    if agents_path.exists():
        existing_content = agents_path.read_text()
        
        # Generate new content to temp location
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_cursor_dir = Path(temp_dir) / '.cursor'
            temp_cursor_dir.mkdir(parents=True, exist_ok=True)
            from generators.manifest_generator import generate_agents_md
            generate_agents_md(context, temp_cursor_dir)
            temp_agents = temp_cursor_dir / 'AGENTS.md'
            if temp_agents.exists():
                new_content = temp_agents.read_text()
                # Merge
                merged = merge_cursorrules(existing_content, new_content)
                agents_path.write_text(merged)
                print("Enhanced AGENTS.md file")
    else:
        # No existing file, generate new
        from generators.manifest_generator import generate_agents_md
        generate_agents_md(context, cursor_dir)

