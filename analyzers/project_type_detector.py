"""
Project type detector module.

Classifies project type based on directory structure and files.
"""

from pathlib import Path
from typing import Dict, Any, List


def detect_project_type(repo_path: Path) -> Dict[str, Any]:
    """
    Detect project type from repository structure.
    
    Args:
        repo_path: Path to repository directory
        
    Returns:
        Dictionary with project type information
    """
    # Check for microservices indicators
    services_dir = repo_path / 'services'
    if services_dir.exists() and services_dir.is_dir():
        services = [d.name for d in services_dir.iterdir() if d.is_dir()]
        return {
            'type': 'microservices',
            'services': services,
            'architecture': 'microservices',
            'ports': []
        }
    
    # Check for monorepo indicators
    packages_dir = repo_path / 'packages'
    apps_dir = repo_path / 'apps'
    if (packages_dir.exists() and packages_dir.is_dir()) or \
       (apps_dir.exists() and apps_dir.is_dir()):
        return {
            'type': 'monorepo',
            'services': [],
            'architecture': 'monorepo',
            'ports': []
        }
    
    # Check for SPA indicators
    package_json = repo_path / 'package.json'
    if package_json.exists():
        try:
            import json
            data = json.loads(package_json.read_text())
            deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
            
            if 'react' in deps or 'vue' in deps or 'angular' in deps:
                # Check if there's a backend
                backend_indicators = ['backend', 'server', 'api']
                has_backend = any((repo_path / d).exists() for d in backend_indicators)
                
                if has_backend:
                    return {
                        'type': 'full_stack',
                        'services': [],
                        'architecture': 'full_stack',
                        'ports': [3000, 8000]
                    }
                else:
                    return {
                        'type': 'spa',
                        'services': [],
                        'architecture': 'spa',
                        'ports': [3000]
                    }
        except:
            pass
    
    # Check for API indicators
    if (repo_path / 'requirements.txt').exists() or \
       (repo_path / 'pyproject.toml').exists() or \
       (repo_path / 'go.mod').exists():
        # Check for API-specific structure
        api_indicators = ['routes', 'controllers', 'handlers', 'api', 'endpoints']
        has_api_structure = any((repo_path / d).exists() for d in api_indicators)
        
        if has_api_structure:
            return {
                'type': 'api',
                'services': [],
                'architecture': 'api',
                'ports': [8000]
            }
    
    # Check for CLI indicators
    if (repo_path / 'cmd').exists() or \
       (repo_path / 'cli').exists() or \
       (repo_path / 'commands').exists():
        return {
            'type': 'cli',
            'services': [],
            'architecture': 'cli',
            'ports': []
        }
    
    # Default to unknown
    return {
        'type': 'unknown',
        'services': [],
        'architecture': 'unknown',
        'ports': []
    }

