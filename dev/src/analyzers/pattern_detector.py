"""
Pattern detector module.

Detects common patterns and anti-patterns in codebase.
"""

from pathlib import Path
from typing import Dict, Any, List, Set
import re


def detect_patterns(repo_path: Path) -> Dict[str, Any]:
    """
    Detect common patterns and anti-patterns in codebase.
    
    Args:
        repo_path: Path to repository directory
        
    Returns:
        Dictionary with detected patterns
    """
    patterns = {
        'common_patterns': [],
        'anti_patterns': [],
        'conventions': [],
        'code_smells': []
    }
    
    # Analyze Python files
    python_files = list(repo_path.rglob('*.py'))[:100]  # Limit for performance
    if python_files:
        py_patterns = detect_python_patterns(python_files)
        patterns['common_patterns'].extend(py_patterns.get('common', []))
        patterns['anti_patterns'].extend(py_patterns.get('anti', []))
        patterns['conventions'].extend(py_patterns.get('conventions', []))
    
    # Analyze JavaScript/TypeScript files
    js_files = list(repo_path.rglob('*.js')) + list(repo_path.rglob('*.ts'))
    js_files = js_files[:100]  # Limit for performance
    if js_files:
        js_patterns = detect_javascript_patterns(js_files)
        patterns['common_patterns'].extend(js_patterns.get('common', []))
        patterns['anti_patterns'].extend(js_patterns.get('anti', []))
        patterns['conventions'].extend(js_patterns.get('conventions', []))
    
    # Detect naming conventions
    naming = detect_naming_conventions(repo_path)
    patterns['conventions'].extend(naming)
    
    # Remove duplicates
    patterns['common_patterns'] = list(set(patterns['common_patterns']))
    patterns['anti_patterns'] = list(set(patterns['anti_patterns']))
    patterns['conventions'] = list(set(patterns['conventions']))
    
    return patterns


def detect_python_patterns(python_files: List[Path]) -> Dict[str, List[str]]:
    """
    Detect patterns in Python code.
    
    Args:
        python_files: List of Python file paths
        
    Returns:
        Dictionary with detected patterns
    """
    patterns = {
        'common': [],
        'anti': [],
        'conventions': []
    }
    
    for py_file in python_files:
        try:
            content = py_file.read_text(encoding='utf-8', errors='ignore')
            
            # Common patterns
            if 'with ' in content and 'open(' in content:
                patterns['common'].append('context_manager')
            if '@property' in content:
                patterns['common'].append('properties')
            if '@staticmethod' in content or '@classmethod' in content:
                patterns['common'].append('static_methods')
            if 'try:' in content and 'except' in content:
                patterns['common'].append('exception_handling')
            if 'if __name__ == "__main__":' in content:
                patterns['common'].append('main_guard')
            
            # Anti-patterns
            if 'eval(' in content or 'exec(' in content:
                patterns['anti'].append('eval_exec_usage')
            if re.search(r'print\s*\(', content) and 'logging' not in content:
                patterns['anti'].append('print_instead_of_logging')
            if 'import *' in content:
                patterns['anti'].append('wildcard_imports')
            
            # Conventions
            if re.search(r'def [a-z_]+\(', content):
                patterns['conventions'].append('snake_case_functions')
            if re.search(r'class [A-Z][a-zA-Z0-9]*', content):
                patterns['conventions'].append('PascalCase_classes')
                
        except Exception:
            continue
    
    return patterns


def detect_javascript_patterns(js_files: List[Path]) -> Dict[str, List[str]]:
    """
    Detect patterns in JavaScript/TypeScript code.
    
    Args:
        js_files: List of JavaScript/TypeScript file paths
        
    Returns:
        Dictionary with detected patterns
    """
    patterns = {
        'common': [],
        'anti': [],
        'conventions': []
    }
    
    for js_file in js_files:
        try:
            content = js_file.read_text(encoding='utf-8', errors='ignore')
            
            # Common patterns
            if 'const ' in content or 'let ' in content:
                patterns['common'].append('const_let_usage')
            if '=>' in content:
                patterns['common'].append('arrow_functions')
            if 'async ' in content:
                patterns['common'].append('async_await')
            if 'Promise' in content:
                patterns['common'].append('promises')
            
            # Anti-patterns
            if 'var ' in content:
                patterns['anti'].append('var_usage')
            if '== ' in content and '===' not in content:
                patterns['anti'].append('loose_equality')
            if 'eval(' in content:
                patterns['anti'].append('eval_usage')
            
            # Conventions
            if re.search(r'function [a-z][a-zA-Z0-9]*\(', content):
                patterns['conventions'].append('camelCase_functions')
            if re.search(r'class [A-Z][a-zA-Z0-9]*', content):
                patterns['conventions'].append('PascalCase_classes')
                
        except Exception:
            continue
    
    return patterns


def detect_naming_conventions(repo_path: Path) -> List[str]:
    """
    Detect naming conventions from file and directory structure.
    
    Args:
        repo_path: Path to repository directory
        
    Returns:
        List of detected naming conventions
    """
    conventions = []
    
    # Check file naming
    python_files = list(repo_path.rglob('*.py'))[:50]
    js_files = list(repo_path.rglob('*.js'))[:50]
    
    snake_case_count = 0
    kebab_case_count = 0
    camelCase_count = 0
    
    for file_path in python_files + js_files:
        name = file_path.stem
        if re.match(r'^[a-z_]+$', name):
            snake_case_count += 1
        elif '-' in name:
            kebab_case_count += 1
        elif re.match(r'^[a-z][a-zA-Z0-9]*$', name):
            camelCase_count += 1
    
    total = len(python_files) + len(js_files)
    if total > 0:
        if snake_case_count / total > 0.7:
            conventions.append('snake_case_files')
        elif kebab_case_count / total > 0.7:
            conventions.append('kebab-case_files')
        elif camelCase_count / total > 0.7:
            conventions.append('camelCase_files')
    
    return conventions

