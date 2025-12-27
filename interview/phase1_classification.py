"""
Phase 1: Project Classification

Extracts: project_name, project_type, primary_language
"""

from typing import Dict, Any, Optional


def run_phase1() -> Optional[Dict[str, Any]]:
    """
    Run Phase 1: Project Classification.
    
    Returns:
        Dictionary with project_name, project_type, primary_language
    """
    print("\n" + "=" * 60)
    print("PHASE 1: Project Classification")
    print("=" * 60)
    
    # Get project name
    project_name = input("What is the name of your project? ").strip()
    if not project_name:
        print("Project name is required.")
        return None
    
    # Get project type
    print("\nWhat type of project is this?")
    print("1. Microservices")
    print("2. Monorepo")
    print("3. SPA (Single Page Application)")
    print("4. API Server")
    print("5. Full-stack")
    print("6. CLI Tool")
    print("7. Other")
    
    project_type_choice = input("Enter choice (1-7): ").strip()
    project_type_map = {
        '1': 'microservices',
        '2': 'monorepo',
        '3': 'spa',
        '4': 'api',
        '5': 'full_stack',
        '6': 'cli',
        '7': 'other'
    }
    project_type = project_type_map.get(project_type_choice, 'other')
    
    if project_type == 'other':
        project_type = input("Please specify project type: ").strip() or 'unknown'
    
    # Get primary language
    print("\nWhat is the primary programming language?")
    print("1. Python")
    print("2. JavaScript")
    print("3. TypeScript")
    print("4. Go")
    print("5. Rust")
    print("6. Java")
    print("7. Other")
    
    language_choice = input("Enter choice (1-7): ").strip()
    language_map = {
        '1': 'python',
        '2': 'javascript',
        '3': 'typescript',
        '4': 'go',
        '5': 'rust',
        '6': 'java',
        '7': 'other'
    }
    primary_language = language_map.get(language_choice, 'other')
    
    if primary_language == 'other':
        primary_language = input("Please specify primary language: ").strip() or 'unknown'
    
    return {
        'project_name': project_name,
        'project_type': project_type,
        'primary_language': primary_language
    }

