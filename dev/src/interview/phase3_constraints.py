"""
Phase 3: Constraints & Requirements

Extracts: deployment_type, networking, database, constraints
"""

from typing import Dict, Any, Optional


def run_phase3(context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Run Phase 3: Constraints & Requirements.
    
    Args:
        context: Context from previous phases
        
    Returns:
        Dictionary with deployment_type, networking, database, constraints
    """
    print("\n" + "=" * 60)
    print("PHASE 3: Constraints & Requirements")
    print("=" * 60)
    
    # Get deployment type
    print("\nWhat is the deployment type?")
    print("1. Docker")
    print("2. Kubernetes")
    print("3. Cloud (AWS/GCP/Azure)")
    print("4. Serverless")
    print("5. Local development only")
    print("6. Other")
    
    deployment_choice = input("Enter choice (1-6): ").strip()
    deployment_map = {
        '1': 'docker',
        '2': 'kubernetes',
        '3': 'cloud',
        '4': 'serverless',
        '5': 'local',
        '6': 'other'
    }
    deployment_type = deployment_map.get(deployment_choice, 'local')
    
    if deployment_type == 'other':
        deployment_type = input("Please specify deployment type: ").strip() or 'unknown'
    
    # Get networking requirements
    print("\nAny specific networking requirements? (press Enter to skip)")
    networking = input("Networking: ").strip() or 'standard'
    
    # Get database
    print("\nWhat database(s) are you using? (comma-separated, or press Enter to skip)")
    database_input = input("Databases: ").strip()
    databases = [d.strip() for d in database_input.split(',') if d.strip()] if database_input else []
    
    # Get constraints
    print("\nAny specific constraints or requirements? (press Enter to skip)")
    constraints_input = input("Constraints: ").strip()
    constraints = constraints_input if constraints_input else None
    
    return {
        'deployment_type': deployment_type,
        'networking': networking,
        'database': databases,
        'constraints': constraints
    }

