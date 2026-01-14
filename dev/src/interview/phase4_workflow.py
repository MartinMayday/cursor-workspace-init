"""
Phase 4: Development Workflow & Standards

Extracts: coding_standards, file_organization, testing_framework
"""

from typing import Dict, Any, Optional


def run_phase4(context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Run Phase 4: Development Workflow & Standards.
    
    Args:
        context: Context from previous phases
        
    Returns:
        Dictionary with coding_standards, file_organization, testing_framework
    """
    print("\n" + "=" * 60)
    print("PHASE 4: Development Workflow & Standards")
    print("=" * 60)
    
    # Get coding standards
    print("\nWhat coding standards do you follow? (press Enter for default)")
    primary_language = context.get('primary_language', '')
    
    # Show language-specific options
    if primary_language == 'python':
        print("Options: PEP 8, Google Style, Black, etc.")
    elif primary_language in ['javascript', 'typescript']:
        print("Options: Standard, Airbnb, Google, etc.")
    else:
        print("Options: Standard, Google Style, etc.")
    
    coding_standards = input("Coding standards: ").strip()
    
    # Set default based on language
    if not coding_standards:
        if primary_language == 'python':
            coding_standards = 'PEP 8'
        elif primary_language in ['javascript', 'typescript']:
            coding_standards = 'Standard'
        else:
            coding_standards = 'Standard'
    
    # Detect coding standards from existing files if available
    # (This would be done by coding_standards_detector in analyze mode)
    
    # Get file organization
    print("\nAny specific file organization preferences? (press Enter to skip)")
    file_organization = input("File organization: ").strip() or 'standard'
    
    # Get testing framework
    print("\nWhat testing framework are you using? (press Enter to skip)")
    testing_framework = input("Testing framework: ").strip()
    
    # Set default based on language
    if not testing_framework:
        primary_language = context.get('primary_language', '')
        if primary_language == 'python':
            testing_framework = 'pytest'
        elif primary_language in ['javascript', 'typescript']:
            testing_framework = 'jest'
        else:
            testing_framework = 'unknown'
    
    return {
        'coding_standards': coding_standards,
        'file_organization': file_organization,
        'testing_framework': testing_framework
    }

