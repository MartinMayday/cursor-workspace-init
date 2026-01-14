"""
Phase 2: Technology Stack & Architecture

Extracts: services, technologies, ports, architecture
"""

from typing import Dict, Any, Optional


def run_phase2(context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Run Phase 2: Technology Stack & Architecture.
    
    Args:
        context: Context from previous phases
        
    Returns:
        Dictionary with services, technologies, ports, architecture
    """
    print("\n" + "=" * 60)
    print("PHASE 2: Technology Stack & Architecture")
    print("=" * 60)
    
    # Get framework/technologies
    print("\nWhat framework(s) are you using? (comma-separated, or press Enter to skip)")
    technologies_input = input("Frameworks: ").strip()
    technologies = [t.strip() for t in technologies_input.split(',') if t.strip()] if technologies_input else []
    
    # Store as frameworks list for context
    frameworks = technologies.copy()
    
    # Framework-dependent questions
    if frameworks:
        primary_framework = frameworks[0].lower()
        
        # Ask framework-specific questions
        if primary_framework in ['fastapi', 'django', 'flask']:
            print(f"\n{primary_framework.capitalize()} detected. Any specific configuration? (press Enter to skip)")
            config = input("Configuration: ").strip()
            if config:
                technologies.append(f"{primary_framework} config: {config}")
        
        elif primary_framework in ['react', 'nextjs', 'vue']:
            print(f"\n{primary_framework.capitalize()} detected. Using TypeScript? (yes/no, press Enter for no)")
            use_ts = input("TypeScript: ").strip().lower()
            if use_ts in ['yes', 'y']:
                technologies.append('typescript')
        
        elif primary_framework in ['express', 'nestjs']:
            print(f"\n{primary_framework.capitalize()} detected. Any specific middleware? (press Enter to skip)")
            middleware = input("Middleware: ").strip()
            if middleware:
                technologies.append(f"middleware: {middleware}")
    
    # Get services (for microservices/monorepo)
    project_type = context.get('project_type', '')
    services = []
    if project_type in ['microservices', 'monorepo']:
        print("\nWhat services/components does this project have? (comma-separated, or press Enter to skip)")
        services_input = input("Services: ").strip()
        services = [s.strip() for s in services_input.split(',') if s.strip()]
    
    # Get ports
    print("\nWhat ports will your services use? (comma-separated, or press Enter to skip)")
    ports_input = input("Ports: ").strip()
    ports = []
    if ports_input:
        try:
            ports = [int(p.strip()) for p in ports_input.split(',') if p.strip()]
        except ValueError:
            print("Warning: Invalid port numbers, skipping.")
    
    # Get architecture
    print("\nWhat is the architecture pattern? (press Enter for default)")
    print("Options: microservices, monolith, serverless, event-driven, etc.")
    architecture = input("Architecture: ").strip() or context.get('project_type', 'unknown')
    
    return {
        'services': services,
        'technologies': technologies,
        'frameworks': frameworks,  # Store as frameworks list
        'ports': ports,
        'architecture': architecture
    }

