"""
Script 2: Interactive AI-powered interview for new projects.

This script conducts a 5-phase interview following the SOP framework
to gather project requirements and generate workspace files.
"""

from typing import Dict, Any, Optional


def run_interview() -> Optional[Dict[str, Any]]:
    """
    Run the complete 5-phase interview process.
    
    Returns:
        Dictionary containing extracted context variables, or None if cancelled
    """
    from interview.interview_engine import InterviewEngine
    
    engine = InterviewEngine()
    context = engine.conduct_interview()
    
    return context


def generate_from_interview(context: Dict[str, Any], output_path: str):
    """
    Generate workspace files from interview context.
    
    Args:
        context: Context variables from interview
        output_path: Path where files should be generated
    """
    from generators.workspace_generator import generate_workspace_files
    generate_workspace_files(context, output_path)

