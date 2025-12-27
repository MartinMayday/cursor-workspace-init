"""
Dependency analyzer module.

Extracts dependencies, testing frameworks, and linting/formatting tools.
"""

from pathlib import Path
from typing import Dict, Any, List


def analyze_dependencies(repo_path: Path) -> Dict[str, Any]:
    """
    Analyze dependencies from repository.
    
    Args:
        repo_path: Path to repository directory
        
    Returns:
        Dictionary with dependency information
    """
    dependencies = []
    testing_frameworks = []
    linting_tools = []
    formatting_tools = []
    
    # Python dependencies
    requirements = repo_path / 'requirements.txt'
    if requirements.exists():
        deps = parse_requirements(requirements)
        dependencies.extend(deps)
        testing_frameworks.extend([d for d in deps if 'pytest' in d or 'unittest' in d])
        linting_tools.extend([d for d in deps if 'ruff' in d or 'flake8' in d or 'pylint' in d])
        formatting_tools.extend([d for d in deps if 'black' in d or 'autopep8' in d])
    
    pyproject = repo_path / 'pyproject.toml'
    if pyproject.exists():
        try:
            # Try tomli first (Python 3.11+), fallback to tomllib
            try:
                import tomli
                with open(pyproject, 'rb') as f:
                    data = tomli.load(f)
            except ImportError:
                import tomllib
                with open(pyproject, 'rb') as f:
                    data = tomllib.load(f)
            
            deps = data.get('project', {}).get('dependencies', [])
            dependencies.extend(deps)
        except:
            pass
    
    # JavaScript/TypeScript dependencies
    package_json = repo_path / 'package.json'
    if package_json.exists():
        try:
            import json
            data = json.loads(package_json.read_text())
            deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
            dependencies.extend(list(deps.keys()))
            
            # Testing
            if 'jest' in deps:
                testing_frameworks.append('jest')
            if 'vitest' in deps:
                testing_frameworks.append('vitest')
            if 'mocha' in deps:
                testing_frameworks.append('mocha')
            
            # Linting
            if 'eslint' in deps:
                linting_tools.append('eslint')
            if 'tslint' in deps:
                linting_tools.append('tslint')
            
            # Formatting
            if 'prettier' in deps:
                formatting_tools.append('prettier')
        except:
            pass
    
    # Go dependencies
    go_mod = repo_path / 'go.mod'
    if go_mod.exists():
        try:
            content = go_mod.read_text()
            for line in content.split('\n'):
                if line.strip() and not line.startswith('module') and not line.startswith('go '):
                    dep = line.split()[0] if line.split() else None
                    if dep:
                        dependencies.append(dep)
        except:
            pass
    
    primary_testing = testing_frameworks[0] if testing_frameworks else 'unknown'
    
    return {
        'dependencies': dependencies,
        'testing': primary_testing,
        'testing_frameworks': testing_frameworks,
        'linting': linting_tools,
        'formatting': formatting_tools
    }


def parse_requirements(requirements_file: Path) -> List[str]:
    """
    Parse requirements.txt file.
    
    Args:
        requirements_file: Path to requirements.txt
        
    Returns:
        List of dependency names
    """
    dependencies = []
    try:
        content = requirements_file.read_text()
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                # Extract package name (before ==, >=, etc.)
                dep = line.split('==')[0].split('>=')[0].split('<=')[0].split('>')[0].split('<')[0].split('~=')[0].strip()
                if dep:
                    dependencies.append(dep)
    except:
        pass
    
    return dependencies

