"""
Code structure analyzer module.

Analyzes code structure, imports, patterns, and architecture from repository.
"""

from pathlib import Path
from typing import Dict, Any, List, Set
import re
import ast


def analyze_code_structure(repo_path: Path) -> Dict[str, Any]:
    """
    Analyze code structure from repository.
    
    Args:
        repo_path: Path to repository directory
        
    Returns:
        Dictionary with code structure information
    """
    structure_info = {
        'import_patterns': {},
        'architecture_patterns': [],
        'common_modules': [],
        'code_organization': {},
        'patterns_detected': []
    }
    
    # Analyze Python code structure
    python_files = list(repo_path.rglob('*.py'))
    if python_files:
        python_structure = analyze_python_structure(python_files[:50])  # Limit for performance
        structure_info.update(python_structure)
    
    # Analyze JavaScript/TypeScript code structure
    js_files = list(repo_path.rglob('*.js')) + list(repo_path.rglob('*.ts'))
    if js_files:
        js_structure = analyze_javascript_structure(js_files[:50])  # Limit for performance
        structure_info['js_patterns'] = js_structure.get('patterns', [])
        structure_info['js_modules'] = js_structure.get('modules', [])
    
    # Detect architecture patterns
    architecture = detect_architecture_patterns(repo_path, structure_info)
    structure_info['architecture_patterns'] = architecture
    
    return structure_info


def analyze_python_structure(python_files: List[Path]) -> Dict[str, Any]:
    """
    Analyze Python code structure.
    
    Args:
        python_files: List of Python file paths
        
    Returns:
        Dictionary with Python structure information
    """
    imports = {}
    modules = []
    patterns = []
    
    for py_file in python_files:
        try:
            content = py_file.read_text(encoding='utf-8', errors='ignore')
            
            # Parse imports
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            module = alias.name.split('.')[0]
                            if module not in imports:
                                imports[module] = 0
                            imports[module] += 1
                            if module not in modules:
                                modules.append(module)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            module = node.module.split('.')[0]
                            if module not in imports:
                                imports[module] = 0
                            imports[module] += 1
                            if module not in modules:
                                modules.append(module)
            except:
                # Fallback to regex if AST parsing fails
                import_pattern = r'^(?:from|import)\s+([a-zA-Z0-9_]+)'
                for line in content.split('\n'):
                    match = re.match(import_pattern, line.strip())
                    if match:
                        module = match.group(1)
                        if module not in imports:
                            imports[module] = 0
                        imports[module] += 1
                        if module not in modules:
                            modules.append(module)
            
            # Detect patterns
            if 'class ' in content and 'def ' in content:
                patterns.append('object_oriented')
            if '@' in content and 'def ' in content:
                patterns.append('decorators')
            if 'async def' in content:
                patterns.append('async_await')
            if 'yield' in content:
                patterns.append('generators')
                
        except Exception:
            continue
    
    # Get most common modules
    common_modules = sorted(imports.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        'import_patterns': dict(common_modules),
        'common_modules': [m[0] for m in common_modules],
        'patterns_detected': list(set(patterns))
    }


def analyze_javascript_structure(js_files: List[Path]) -> Dict[str, Any]:
    """
    Analyze JavaScript/TypeScript code structure.
    
    Args:
        js_files: List of JavaScript/TypeScript file paths
        
    Returns:
        Dictionary with JavaScript structure information
    """
    imports = {}
    modules = []
    patterns = []
    
    for js_file in js_files:
        try:
            content = js_file.read_text(encoding='utf-8', errors='ignore')
            
            # Parse imports (ES6 and CommonJS)
            import_patterns = [
                r'import\s+.*?\s+from\s+["\']([^"\']+)["\']',
                r'require\(["\']([^"\']+)["\']\)',
                r'from\s+["\']([^"\']+)["\']'
            ]
            
            for pattern in import_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    module = match.split('/')[0].split('@')[0]  # Handle scoped packages
                    if module not in imports:
                        imports[module] = 0
                    imports[module] += 1
                    if module not in modules:
                        modules.append(module)
            
            # Detect patterns
            if 'class ' in content:
                patterns.append('classes')
            if 'async ' in content or 'await ' in content:
                patterns.append('async_await')
            if 'export ' in content:
                patterns.append('es6_modules')
            if 'module.exports' in content or 'exports.' in content:
                patterns.append('commonjs')
            if '=>' in content:
                patterns.append('arrow_functions')
                
        except Exception:
            continue
    
    # Get most common modules
    common_modules = sorted(imports.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        'modules': [m[0] for m in common_modules],
        'patterns': list(set(patterns))
    }


def detect_architecture_patterns(repo_path: Path, structure_info: Dict[str, Any]) -> List[str]:
    """
    Detect architecture patterns from code structure.
    
    Args:
        repo_path: Path to repository directory
        structure_info: Code structure information
        
    Returns:
        List of detected architecture patterns
    """
    patterns = []
    
    # Check for MVC pattern
    if any(d in ['models', 'views', 'controllers'] for d in [p.name.lower() for p in repo_path.iterdir() if p.is_dir()]):
        patterns.append('mvc')
    
    # Check for layered architecture
    if any(d in ['presentation', 'business', 'data', 'domain'] for d in [p.name.lower() for p in repo_path.iterdir() if p.is_dir()]):
        patterns.append('layered')
    
    # Check for repository pattern
    python_files = list(repo_path.rglob('*.py'))[:20]
    if any('repository' in p.name.lower() for p in python_files):
        patterns.append('repository')
    
    # Check for service pattern
    if any('service' in p.name.lower() for p in python_files):
        patterns.append('service')
    
    # Check for factory pattern
    if any('factory' in p.name.lower() for p in python_files):
        patterns.append('factory')
    
    # Check for dependency injection
    common_modules = structure_info.get('common_modules', [])
    if any(m in ['inject', 'di', 'dependency'] for m in common_modules):
        patterns.append('dependency_injection')
    
    return patterns

