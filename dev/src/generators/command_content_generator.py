"""
Command content generator module.

Generates actual command files with project-specific commands.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional


def generate_command_content(
    command_type: str,
    context: Dict[str, Any],
    template_dir: Path
) -> Optional[str]:
    """
    Generate command content for a specific type.
    
    Args:
        command_type: Type of command file (test, build, deploy, docker)
        context: Context variables dictionary
        template_dir: Path to templates directory
        
    Returns:
        Generated command content or None if template not found
    """
    template_map = {
        'test': 'test-commands.mdc.template',
        'build': 'build-commands.mdc.template',
        'deploy': 'deploy-commands.mdc.template',
        'docker': 'docker-commands.mdc.template',
    }
    
    template_name = template_map.get(command_type)
    if not template_name:
        return None
    
    template_path = template_dir / '.cursor' / 'commands' / template_name
    
    if template_path.exists():
        from generators.template_engine import load_template, replace_placeholders
        template = load_template(str(template_path))
        content = replace_placeholders(template, context)
        return content
    
    # Generate fallback content if template doesn't exist
    return generate_fallback_command_content(command_type, context)


def generate_fallback_command_content(command_type: str, context: Dict[str, Any]) -> str:
    """
    Generate fallback command content when template is missing.
    
    Args:
        command_type: Type of command file
        context: Context variables dictionary
        
    Returns:
        Fallback command content
    """
    project_name = context.get('project_name', 'Project')
    primary_language = context.get('primary_language', 'unknown')
    testing_framework = context.get('testing_framework', 'unknown')
    
    if command_type == 'test':
        return f"""# Test Commands for {project_name}

## Running Tests
- Use {testing_framework} for testing
- Run all tests: Check project documentation for test command
- Run specific test: Check project documentation for test command
"""
    
    elif command_type == 'build':
        return f"""# Build Commands for {project_name}

## Building the Project
- Build command: Check project documentation for build command
- Build for production: Check project documentation for production build
"""
    
    elif command_type == 'deploy':
        deployment_type = context.get('deployment_type', 'unknown')
        return f"""# Deployment Commands for {project_name}

## Deployment
- Deployment type: {deployment_type}
- Deploy command: Check project documentation for deployment command
"""
    
    elif command_type == 'docker':
        return f"""# Docker Commands for {project_name}

## Docker Commands
- Build image: docker build -t {project_name.lower()} .
- Run container: docker run {project_name.lower()}
"""
    
    return ""


def get_required_command_files(context: Dict[str, Any]) -> List[str]:
    """
    Determine which command files should be generated based on context.
    
    Args:
        context: Context variables dictionary
        
    Returns:
        List of command file types to generate
    """
    command_files = []
    
    # Always generate test commands if testing framework is detected
    if context.get('testing_framework') and context.get('testing_framework') != 'unknown':
        command_files.append('test')
    
    # Always generate build commands
    command_files.append('build')
    
    # Generate deploy commands if deployment type is detected
    if context.get('deployment_type') and context.get('deployment_type') != 'unknown':
        command_files.append('deploy')
    
    # Generate docker commands if Docker is detected
    containerization = context.get('containerization', [])
    if containerization and 'docker' in str(containerization).lower():
        command_files.append('docker')
    
    return command_files


def generate_all_command_files(
    context: Dict[str, Any],
    commands_dir: Path,
    template_dir: Path
) -> List[str]:
    """
    Generate all command files based on context.
    
    Args:
        context: Context variables dictionary
        commands_dir: Path to .cursor/commands directory
        template_dir: Path to templates directory
        
    Returns:
        List of generated command file names
    """
    generated_files = []
    required_files = get_required_command_files(context)
    
    for command_type in required_files:
        content = generate_command_content(command_type, context, template_dir)
        if content:
            filename = f"{command_type}-commands.mdc"
            file_path = commands_dir / filename
            file_path.write_text(content)
            generated_files.append(filename)
    
    return generated_files


