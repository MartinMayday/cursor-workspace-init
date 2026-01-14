"""
Language detector module.

Detects primary language(s) from repository files.
"""

from pathlib import Path
from typing import Dict, Any, List


def detect_language(repo_path: Path) -> Dict[str, Any]:
    """
    Detect primary language(s) from repository.
    
    Args:
        repo_path: Path to repository directory
        
    Returns:
        Dictionary with language information
    """
    languages = []
    language_files = {}
    
    # Check for language-specific files
    indicators = {
        'python': ['*.py', 'requirements.txt', 'pyproject.toml', 'setup.py', 'Pipfile'],
        'javascript': ['*.js', 'package.json', 'yarn.lock', 'package-lock.json'],
        'typescript': ['*.ts', 'tsconfig.json', '*.tsx'],
        'go': ['*.go', 'go.mod', 'go.sum'],
        'rust': ['*.rs', 'Cargo.toml', 'Cargo.lock'],
        'java': ['*.java', 'pom.xml', 'build.gradle', 'build.gradle.kts'],
        'cpp': ['*.cpp', '*.hpp', 'CMakeLists.txt', 'Makefile'],
        'c': ['*.c', '*.h', 'Makefile'],
    }
    
    for lang, patterns in indicators.items():
        count = 0
        for pattern in patterns:
            matches = list(repo_path.rglob(pattern))
            count += len(matches)
            if matches:
                language_files[lang] = language_files.get(lang, 0) + len(matches)
        
        if count > 0:
            languages.append(lang)
    
    # Determine primary language (most files)
    primary = max(language_files.items(), key=lambda x: x[1])[0] if language_files else 'unknown'
    
    # Get language version if possible
    version = None
    if primary == 'python':
        version = detect_python_version(repo_path)
    elif primary == 'javascript' or primary == 'typescript':
        version = detect_node_version(repo_path)
    elif primary == 'go':
        version = detect_go_version(repo_path)
    
    return {
        'primary': primary,
        'languages': languages,
        'version': version,
        'file_counts': language_files
    }


def detect_python_version(repo_path: Path) -> str:
    """Detect Python version from files."""
    # Check pyproject.toml
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
            
            if 'tool' in data and 'python' in data['tool']:
                requires = data['tool']['python'].get('requires-python', '')
                if requires:
                    return requires
        except:
            pass
    
    # Check .python-version
    python_version = repo_path / '.python-version'
    if python_version.exists():
        return python_version.read_text().strip()
    
    return 'unknown'


def detect_node_version(repo_path: Path) -> str:
    """Detect Node.js version from package.json."""
    package_json = repo_path / 'package.json'
    if package_json.exists():
        try:
            import json
            data = json.loads(package_json.read_text())
            engines = data.get('engines', {})
            if 'node' in engines:
                return engines['node']
        except:
            pass
    
    # Check .nvmrc
    nvmrc = repo_path / '.nvmrc'
    if nvmrc.exists():
        return nvmrc.read_text().strip()
    
    return 'unknown'


def detect_go_version(repo_path: Path) -> str:
    """Detect Go version from go.mod."""
    go_mod = repo_path / 'go.mod'
    if go_mod.exists():
        try:
            content = go_mod.read_text()
            for line in content.split('\n'):
                if line.startswith('go '):
                    return line.split()[1]
        except:
            pass
    
    return 'unknown'

