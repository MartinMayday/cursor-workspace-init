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
    from generators.template_engine import validate_template_context
    from generators.template_engine import load_template
    
    engine = InterviewEngine()
    context = engine.conduct_interview()
    
    if context is None:
        return None
    
    # Pre-generation validation: ensure all template variables are available
    template_path = Path(__file__).parent.parent / 'templates' / '.cursorrules.template'
    if template_path.exists():
        template = load_template(str(template_path))
        is_valid, missing = validate_template_context(template, context)
        
        if not is_valid:
            print(f"\nWarning: Missing context variables: {missing}")
            print("Some placeholders may not be replaced correctly.")
            response = input("Continue anyway? (yes/no): ").strip().lower()
            if response not in ['yes', 'y']:
                print("Interview cancelled.")
                return None
    
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

