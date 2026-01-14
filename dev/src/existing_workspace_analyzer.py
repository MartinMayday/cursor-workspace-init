"""
Existing workspace analyzer module.

Detects and analyzes existing Cursor workspace files.
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
import json
import re


def analyze_existing_workspace(repo_path: Path) -> Dict[str, Any]:
    """
    Analyze existing Cursor workspace files.
    
    Args:
        repo_path: Path to repository directory
        
    Returns:
        Dictionary with existing workspace information
    """
    workspace_info = {
        'has_cursorrules': False,
        'has_cursor_dir': False,
        'cursorrules_content': None,
        'rules_files': [],
        'commands_files': [],
        'agents_content': None,
        'source_list': None,
        'existing_structure': {}
    }
    
    # Check for .cursorrules
    cursorrules_path = repo_path / '.cursorrules'
    if cursorrules_path.exists():
        workspace_info['has_cursorrules'] = True
        try:
            workspace_info['cursorrules_content'] = cursorrules_path.read_text()
        except:
            pass
    
    # Check for .cursor directory
    cursor_dir = repo_path / '.cursor'
    if cursor_dir.exists() and cursor_dir.is_dir():
        workspace_info['has_cursor_dir'] = True
        
        # Analyze rules directory
        rules_dir = cursor_dir / 'rules'
        if rules_dir.exists():
            workspace_info['rules_files'] = [
                f.name for f in rules_dir.iterdir() 
                if f.is_file() and f.suffix in ['.mdc', '.md']
            ]
            
            # Check for rules manifest
            manifest_path = rules_dir / 'rules_manifest.json'
            if manifest_path.exists():
                try:
                    with open(manifest_path) as f:
                        workspace_info['existing_structure']['rules_manifest'] = json.load(f)
                except:
                    pass
        
        # Analyze commands directory
        commands_dir = cursor_dir / 'commands'
        if commands_dir.exists():
            workspace_info['commands_files'] = [
                f.name for f in commands_dir.iterdir()
                if f.is_file() and f.suffix in ['.mdc', '.md']
            ]
            
            # Check for commands manifest
            manifest_path = commands_dir / 'commands_manifest.json'
            if manifest_path.exists():
                try:
                    with open(manifest_path) as f:
                        workspace_info['existing_structure']['commands_manifest'] = json.load(f)
                except:
                    pass
        
        # Check for AGENTS.md
        agents_path = cursor_dir / 'AGENTS.md'
        if agents_path.exists():
            try:
                workspace_info['agents_content'] = agents_path.read_text()
            except:
                pass
    
    # Check for source_list.json
    source_list_path = repo_path / 'source_list.json'
    if source_list_path.exists():
        try:
            with open(source_list_path) as f:
                workspace_info['source_list'] = json.load(f)
        except:
            pass
    
    return workspace_info


def extract_existing_rules_content(workspace_info: Dict[str, Any], repo_path: Path) -> Dict[str, str]:
    """
    Extract content from existing rule files.
    
    Args:
        workspace_info: Workspace information dictionary
        repo_path: Path to repository directory
        
    Returns:
        Dictionary mapping rule file names to their content
    """
    rules_content = {}
    
    if not workspace_info.get('has_cursor_dir'):
        return rules_content
    
    rules_dir = repo_path / '.cursor' / 'rules'
    if not rules_dir.exists():
        return rules_content
    
    for rule_file in rules_dir.iterdir():
        if rule_file.is_file() and rule_file.suffix in ['.mdc', '.md']:
            try:
                rules_content[rule_file.name] = rule_file.read_text()
            except:
                pass
    
    return rules_content


def extract_existing_commands_content(workspace_info: Dict[str, Any], repo_path: Path) -> Dict[str, str]:
    """
    Extract content from existing command files.
    
    Args:
        workspace_info: Workspace information dictionary
        repo_path: Path to repository directory
        
    Returns:
        Dictionary mapping command file names to their content
    """
    commands_content = {}
    
    if not workspace_info.get('has_cursor_dir'):
        return commands_content
    
    commands_dir = repo_path / '.cursor' / 'commands'
    if not commands_dir.exists():
        return commands_content
    
    for command_file in commands_dir.iterdir():
        if command_file.is_file() and command_file.suffix in ['.mdc', '.md']:
            try:
                commands_content[command_file.name] = command_file.read_text()
            except:
                pass
    
    return commands_content

