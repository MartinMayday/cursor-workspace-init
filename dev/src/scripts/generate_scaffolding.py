"""
Script 3: Generate best practices scaffolding for new projects.

This script generates a new project structure with best practices
and includes cursor workspace files.
"""

from pathlib import Path
from typing import Dict, Any, Optional


def generate_scaffolding(
    project_type: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    output_path: str = "."
):
    """
    Generate new project scaffolding.
    
    Args:
        project_type: Type of project to scaffold (optional, will prompt if not provided)
        context: Context variables (optional, will run interview if not provided)
        output_path: Path where project should be created
    """
    output_path = Path(output_path).resolve()
    
    # If context not provided, run interview first
    if context is None:
        from scripts.interactive_interview import run_interview
        context = run_interview()
        if context is None:
            print("Interview cancelled. Cannot generate scaffolding without context.")
            return
    
    # If project type not provided, use from context
    if project_type is None:
        project_type = context.get('project_type', 'spa')
    
    # Generate project structure
    from generators.workspace_generator import generate_project_scaffold
    generate_project_scaffold(project_type, context, output_path)
    
    print(f"Project scaffolding generated at: {output_path}")

