"""
Phase 5: Confirmation & Examples

Extracts: examples, confirmations
"""

from typing import Dict, Any, Optional


def run_phase5(context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Run Phase 5: Confirmation & Examples.
    
    Args:
        context: Context from previous phases
        
    Returns:
        Dictionary with examples, confirmations
    """
    print("\n" + "=" * 60)
    print("PHASE 5: Confirmation & Examples")
    print("=" * 60)
    
    # Recap findings
    print("\n--- Recap of Project Information ---")
    print(f"Project Name: {context.get('project_name', 'N/A')}")
    print(f"Project Type: {context.get('project_type', 'N/A')}")
    print(f"Primary Language: {context.get('primary_language', 'N/A')}")
    print(f"Technologies: {', '.join(context.get('technologies', [])) or 'N/A'}")
    print(f"Architecture: {context.get('architecture', 'N/A')}")
    print(f"Deployment Type: {context.get('deployment_type', 'N/A')}")
    print(f"Testing Framework: {context.get('testing_framework', 'N/A')}")
    print("=" * 60)
    
    # Confirm
    confirmation = input("\nIs this information correct? (yes/no): ").strip().lower()
    if confirmation not in ['yes', 'y']:
        print("Please review and correct any information as needed.")
        # Could implement correction flow here
    
    # Get examples (optional)
    print("\nWould you like to provide examples of correct/incorrect code? (yes/no)")
    examples_choice = input("Provide examples: ").strip().lower()
    examples = None
    if examples_choice in ['yes', 'y']:
        print("Enter examples (press Enter twice to finish):")
        example_lines = []
        while True:
            line = input()
            if not line and example_lines:
                break
            if line:
                example_lines.append(line)
        examples = '\n'.join(example_lines) if example_lines else None
    
    return {
        'confirmed': confirmation in ['yes', 'y'],
        'examples': examples
    }

