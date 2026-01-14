"""
Manifest generator module.

Generates manifest files (rules_manifest.json, commands_manifest.json, etc.)
and other configuration files using enhanced format with semantic_meaning,
use_when, conditions, and triggers for better AI agent decision-making.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import json


def _generate_trigger(field: str, operator: str, value: Any, action: str = "load") -> Dict[str, Any]:
    """
    Helper to create trigger objects.
    
    Args:
        field: Context field name to check
        operator: Comparison operator (!=, ==, in, etc.)
        value: Value to compare against
        action: Action to take if trigger matches (default: "load")
        
    Returns:
        Trigger dictionary
    """
    return {
        "field": field,
        "operator": operator,
        "value": value,
        "action": action
    }


def _build_rule_semantic_meaning(level: int, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate semantic_meaning object for rules.
    
    Args:
        level: Rule level (1-5)
        context: Context variables dictionary
        
    Returns:
        Semantic meaning dictionary
    """
    level_meanings = {
        1: "Progressive loading hierarchy - Level 1 is most general, always loaded first",
        2: "Architecture and design pattern rules, loaded after core rules",
        3: "Project type-specific rules, loaded after core and architecture rules",
        4: "Language-specific rules, loaded after project type rules",
        5: "Framework-specific rules, loaded after language rules"
    }
    
    specificities = {
        1: "general",
        2: "architectural",
        3: "project-type-specific",
        4: "language-specific",
        5: "framework-specific"
    }
    
    scopes = {
        1: "project-wide",
        2: "project-wide",
        3: f"applies to {context.get('project_type', 'specific project type')} projects",
        4: f"applies to {context.get('primary_language', 'specific language')} projects",
        5: f"applies to {context.get('framework', 'specific framework')} projects"
    }
    
    purposes = {
        1: "Contains fundamental rules and principles that apply universally to all projects",
        2: "Contains architecture and design pattern guidelines",
        3: f"Contains rules specific to {context.get('project_type', 'project type')} project types",
        4: f"Contains rules specific to {context.get('primary_language', 'programming language')} programming language",
        5: f"Contains rules specific to {context.get('framework', 'framework')} framework"
    }
    
    semantic = {
        "level_meaning": level_meanings.get(level, f"Level {level} rules"),
        "specificity": specificities.get(level, "specific"),
        "scope": scopes.get(level, "project-wide"),
        "purpose": purposes.get(level, f"Contains level {level} rules")
    }
    
    return semantic


def _build_rule_conditions(level: int, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate conditions object with triggers for rules.
    
    Args:
        level: Rule level (1-5)
        context: Context variables dictionary
        
    Returns:
        Conditions dictionary with always_load, context_required, and triggers
    """
    # Levels 1-2 always load
    if level <= 2:
        return {
            "always_load": True,
            "context_required": [],
            "triggers": []
        }
    
    # Level 3: Conditional on project_type
    if level == 3:
        project_type = context.get("project_type")
        if project_type and project_type != "unknown":
            return {
                "always_load": False,
                "context_required": ["project_type"],
                "triggers": [
                    _generate_trigger("project_type", "!=", "unknown", "load"),
                    _generate_trigger("project_type", "!=", None, "load")
                ]
            }
        else:
            return {
                "always_load": False,
                "context_required": ["project_type"],
                "triggers": []
            }
    
    # Level 4: Conditional on primary_language
    if level == 4:
        primary_language = context.get("primary_language")
        if primary_language and primary_language != "unknown":
            return {
                "always_load": False,
                "context_required": ["primary_language"],
                "triggers": [
                    _generate_trigger("primary_language", "!=", "unknown", "load"),
                    _generate_trigger("primary_language", "!=", None, "load")
                ]
            }
        else:
            return {
                "always_load": False,
                "context_required": ["primary_language"],
                "triggers": []
            }
    
    # Level 5: Conditional on framework
    if level == 5:
        framework = context.get("framework")
        if framework and framework != "unknown":
            return {
                "always_load": False,
                "context_required": ["framework"],
                "triggers": [
                    _generate_trigger("framework", "!=", "unknown", "load"),
                    _generate_trigger("framework", "!=", None, "load")
                ]
            }
        else:
            return {
                "always_load": False,
                "context_required": ["framework"],
                "triggers": []
            }
    
    # Default for unknown levels
    return {
        "always_load": False,
        "context_required": [],
        "triggers": []
    }


def _get_rule_use_when(level: int, context: Dict[str, Any]) -> str:
    """
    Generate use_when description for rules.
    
    Args:
        level: Rule level (1-5)
        context: Context variables dictionary
        
    Returns:
        Human-readable use_when description
    """
    if level == 1:
        return "always - these are fundamental rules that apply to all projects"
    elif level == 2:
        return "always - architecture rules apply to all projects"
    elif level == 3:
        project_type = context.get("project_type", "project_type")
        return f"when project_type is '{project_type}' and not 'unknown'"
    elif level == 4:
        primary_language = context.get("primary_language", "primary_language")
        return f"when primary_language is '{primary_language}' and not 'unknown'"
    elif level == 5:
        framework = context.get("framework", "framework")
        return f"when framework is '{framework}' and not 'unknown'"
    else:
        return f"when level {level} conditions are met"


def generate_rules_manifest(context: Dict[str, Any], rules_dir: Path, generated_files: list = None):
    """
    Generate rules_manifest.json dynamically based on actual rule files.
    
    Args:
        context: Context variables dictionary
        rules_dir: Path to .cursor/rules directory
        generated_files: Optional list of generated rule file names. If None, scans directory.
    """
    # If generated_files not provided, scan directory for rule files
    if generated_files is None:
        if rules_dir.exists():
            generated_files = [
                f.name for f in rules_dir.iterdir() 
                if f.is_file() and f.name.startswith('level') and f.name.endswith('.mdc')
            ]
        else:
            generated_files = []
    
    # Build manifest from actual files
    rules = []
    level_descriptions = {
        1: "Core rules and principles",
        2: "Architecture and design patterns",
        3: "Project type-specific rules",
        4: "Language-specific rules",
        5: "Framework-specific rules"
    }
    
    # Sort files by level
    level_files = {}
    for filename in generated_files:
        if filename.startswith('level') and filename.endswith('.mdc'):
            try:
                level = int(filename.split('-')[0].replace('level', ''))
                level_files[level] = filename
            except (ValueError, IndexError):
                continue
    
    # Build enhanced format manifest entries
    for level in sorted(level_files.keys()):
        filename = level_files[level]
        description = level_descriptions.get(level, f"Level {level} rules")
        
        # Build enhanced format entry
        rule_entry = {
            "level": level,
            "file": filename,
            "path": f".cursor/rules/{filename}",
            "category": "rules",
            "file_type": "rule",
            "description": description,
            "required": level <= 2,  # Levels 1 and 2 are always required
            "load_order": level,
            "use_when": _get_rule_use_when(level, context),
            "semantic_meaning": _build_rule_semantic_meaning(level, context),
            "conditions": _build_rule_conditions(level, context)
        }
        
        rules.append(rule_entry)
    
    # If no files found, provide defaults with enhanced format
    if not rules:
        for level in [1, 2]:
            filename = f"level{level}-core.mdc" if level == 1 else f"level{level}-architecture.mdc"
            description = level_descriptions.get(level, f"Level {level} rules")
            
            rule_entry = {
                "level": level,
                "file": filename,
                "path": f".cursor/rules/{filename}",
                "category": "rules",
                "file_type": "rule",
                "description": description,
                "required": True,
                "load_order": level,
                "use_when": _get_rule_use_when(level, context),
                "semantic_meaning": _build_rule_semantic_meaning(level, context),
                "conditions": _build_rule_conditions(level, context)
            }
            rules.append(rule_entry)
    
    manifest = {
        "manifest_type": "rules",
        "manifest_version": "1.0",
        "rules": rules
    }
    manifest_path = rules_dir / 'rules_manifest.json'
    manifest_path.write_text(json.dumps(manifest, indent=2))


def _build_command_semantic_meaning(command_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate semantic_meaning object for commands.
    
    Args:
        command_type: Command type (build, test, deploy, docker)
        context: Context variables dictionary
        
    Returns:
        Semantic meaning dictionary
    """
    meanings = {
        'build': {
            "specificity": "build-specific",
            "scope": "project-wide",
            "purpose": "Contains build and compilation commands"
        },
        'test': {
            "specificity": "test-specific",
            "scope": "project-wide",
            "purpose": f"Contains test commands for {context.get('testing_framework', 'testing framework')}"
        },
        'deploy': {
            "specificity": "deployment-specific",
            "scope": "project-wide",
            "purpose": f"Contains deployment commands for {context.get('deployment_type', 'deployment type')}"
        },
        'docker': {
            "specificity": "containerization-specific",
            "scope": "project-wide",
            "purpose": "Contains Docker containerization commands"
        }
    }
    
    return meanings.get(command_type, {
        "specificity": f"{command_type}-specific",
        "scope": "project-wide",
        "purpose": f"Contains {command_type} commands"
    })


def _build_command_conditions(command_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate conditions object with triggers for commands.
    
    Args:
        command_type: Command type (build, test, deploy, docker)
        context: Context variables dictionary
        
    Returns:
        Conditions dictionary with always_load, context_required, and triggers
    """
    # Build commands always load
    if command_type == 'build':
        return {
            "always_load": True,
            "context_required": [],
            "triggers": []
        }
    
    # Test commands: Conditional on testing_framework
    if command_type == 'test':
        testing_framework = context.get("testing_framework")
        if testing_framework and testing_framework != "unknown":
            return {
                "always_load": False,
                "context_required": ["testing_framework"],
                "triggers": [
                    _generate_trigger("testing_framework", "!=", "unknown", "load"),
                    _generate_trigger("testing_framework", "!=", None, "load")
                ]
            }
        else:
            return {
                "always_load": False,
                "context_required": ["testing_framework"],
                "triggers": []
            }
    
    # Deploy commands: Conditional on deployment_type
    if command_type == 'deploy':
        deployment_type = context.get("deployment_type")
        if deployment_type and deployment_type != "unknown":
            return {
                "always_load": False,
                "context_required": ["deployment_type"],
                "triggers": [
                    _generate_trigger("deployment_type", "!=", "unknown", "load"),
                    _generate_trigger("deployment_type", "!=", None, "load")
                ]
            }
        else:
            return {
                "always_load": False,
                "context_required": ["deployment_type"],
                "triggers": []
            }
    
    # Docker commands: Conditional on containerization
    if command_type == 'docker':
        containerization = context.get("containerization", [])
        containerization_str = str(containerization).lower() if containerization else ""
        if containerization and "docker" in containerization_str:
            return {
                "always_load": False,
                "context_required": ["containerization"],
                "triggers": [
                    {
                        "field": "containerization",
                        "operator": "contains",
                        "value": "docker",
                        "action": "load"
                    }
                ]
            }
        else:
            return {
                "always_load": False,
                "context_required": ["containerization"],
                "triggers": []
            }
    
    # Default for unknown command types
    return {
        "always_load": False,
        "context_required": [],
        "triggers": []
    }


def _get_command_use_when(command_type: str, context: Dict[str, Any]) -> str:
    """
    Generate use_when description for commands.
    
    Args:
        command_type: Command type (build, test, deploy, docker)
        context: Context variables dictionary
        
    Returns:
        Human-readable use_when description
    """
    if command_type == 'build':
        return "always - build commands are needed for all projects"
    elif command_type == 'test':
        return "when testing_framework is present and not 'unknown'"
    elif command_type == 'deploy':
        return "when deployment_type is present and not 'unknown'"
    elif command_type == 'docker':
        return "when Docker containerization is detected"
    else:
        return f"when {command_type} commands are needed"


def _get_command_load_order(command_type: str) -> int:
    """
    Get load order priority for command types.
    
    Args:
        command_type: Command type
        
    Returns:
        Load order integer (lower = loaded first)
    """
    order = {
        'build': 1,
        'test': 2,
        'deploy': 3,
        'docker': 4
    }
    return order.get(command_type, 99)


def generate_commands_manifest(context: Dict[str, Any], commands_dir: Path, generated_files: list = None):
    """
    Generate commands_manifest.json dynamically based on actual command files.
    Uses enhanced format with semantic_meaning, use_when, conditions, and triggers.
    
    Args:
        context: Context variables dictionary
        commands_dir: Path to .cursor/commands directory
        generated_files: Optional list of generated command file names. If None, scans directory.
    """
    # If generated_files not provided, scan directory for command files
    if generated_files is None:
        if commands_dir.exists():
            generated_files = [
                f.name for f in commands_dir.iterdir() 
                if f.is_file() and f.name.endswith('-commands.mdc')
            ]
        else:
            generated_files = []
    
    # Build manifest from actual files
    commands = []
    command_descriptions = {
        'test': 'Test commands',
        'build': 'Build commands',
        'deploy': 'Deployment commands',
        'docker': 'Docker commands'
    }
    
    # Sort files by type
    for filename in sorted(generated_files):
        if filename.endswith('-commands.mdc'):
            # Extract command type from filename (e.g., "build-commands.mdc" -> "build")
            command_type = filename.replace('-commands.mdc', '')
            description = command_descriptions.get(command_type, f"{command_type.capitalize()} commands")
            
            # Build enhanced format entry
            command_entry = {
                "type": command_type,
                "file": filename,
                "path": f".cursor/commands/{filename}",
                "category": "commands",
                "file_type": "command",
                "description": description,
                "load_order": _get_command_load_order(command_type),
                "use_when": _get_command_use_when(command_type, context),
                "semantic_meaning": _build_command_semantic_meaning(command_type, context),
                "conditions": _build_command_conditions(command_type, context)
            }
            
            commands.append(command_entry)
    
    manifest = {
        "manifest_type": "commands",
        "manifest_version": "1.0",
        "commands": commands
    }
    manifest_path = commands_dir / 'commands_manifest.json'
    manifest_path.write_text(json.dumps(manifest, indent=2))


def generate_source_list(context: Dict[str, Any], output_path: Path):
    """
    Generate source_list.json with auto-populated documentation sources.
    
    Args:
        context: Context variables dictionary
        output_path: Path where file should be generated
    """
    from generators.source_list_generator import generate_source_list_json
    
    config_dir = Path(__file__).parent.parent / 'config'
    generate_source_list_json(context, config_dir, output_path)


def generate_agents_md(context: Dict[str, Any], cursor_dir: Path):
    """
    Generate AGENTS.md.
    
    Args:
        context: Context variables dictionary
        cursor_dir: Path to .cursor directory
    """
    from generators.template_engine import load_template, replace_placeholders, validate_template_context
    
    template_path = Path(__file__).parent.parent / 'templates' / '.cursor' / 'AGENTS.md.template'
    
    if template_path.exists():
        template = load_template(str(template_path))
        
        # Validate context before generation
        is_valid, missing = validate_template_context(template, context)
        if not is_valid:
            print(f"Warning: Missing context variables for AGENTS.md: {missing}")
            print("Proceeding with defaults...")
        
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

