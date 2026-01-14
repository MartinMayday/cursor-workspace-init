"""
Knowledge extractor module.

Extracts domain knowledge and project context from codebase.
"""

from pathlib import Path
from typing import Dict, Any, List, Set
import re


def extract_knowledge(repo_path: Path) -> Dict[str, Any]:
    """
    Extract domain knowledge and project context.
    
    Args:
        repo_path: Path to repository directory
        
    Returns:
        Dictionary with extracted knowledge
    """
    knowledge = {
        'domain_terms': [],
        'key_concepts': [],
        'project_domain': '',
        'business_logic_patterns': [],
        'team_conventions': []
    }
    
    # Extract from README
    readme_info = extract_from_readme(repo_path)
    if readme_info:
        knowledge.update(readme_info)
    
    # Extract from code comments and docstrings
    code_knowledge = extract_from_code(repo_path)
    knowledge['domain_terms'].extend(code_knowledge.get('terms', []))
    knowledge['key_concepts'].extend(code_knowledge.get('concepts', []))
    
    # Extract from file/directory names
    structure_terms = extract_from_structure(repo_path)
    knowledge['domain_terms'].extend(structure_terms)
    
    # Remove duplicates
    knowledge['domain_terms'] = list(set(knowledge['domain_terms']))
    knowledge['key_concepts'] = list(set(knowledge['key_concepts']))
    
    return knowledge


def extract_from_readme(repo_path: Path) -> Dict[str, Any]:
    """
    Extract knowledge from README files.
    
    Args:
        repo_path: Path to repository directory
        
    Returns:
        Dictionary with extracted information
    """
    readme_files = [
        repo_path / 'README.md',
        repo_path / 'README.rst',
        repo_path / 'README.txt'
    ]
    
    knowledge = {
        'project_domain': '',
        'key_concepts': []
    }
    
    for readme_path in readme_files:
        if readme_path.exists():
            try:
                content = readme_path.read_text(encoding='utf-8', errors='ignore')
                
                # Extract project description (first paragraph)
                lines = content.split('\n')
                description = ''
                for line in lines[:20]:  # First 20 lines
                    line = line.strip()
                    if line and not line.startswith('#'):
                        description += line + ' '
                        if len(description) > 200:
                            break
                knowledge['project_domain'] = description.strip()
                
                # Extract key terms (capitalized words that appear multiple times)
                words = re.findall(r'\b[A-Z][a-z]+\b', content)
                word_counts = {}
                for word in words:
                    if len(word) > 3:  # Ignore short words
                        word_counts[word] = word_counts.get(word, 0) + 1
                
                # Get terms that appear at least 3 times
                key_terms = [word for word, count in word_counts.items() if count >= 3]
                knowledge['key_concepts'] = key_terms[:10]  # Top 10
                
                break
                
            except Exception:
                continue
    
    return knowledge


def extract_from_code(repo_path: Path) -> Dict[str, Any]:
    """
    Extract knowledge from code comments and docstrings.
    
    Args:
        repo_path: Path to repository directory
        
    Returns:
        Dictionary with extracted terms and concepts
    """
    knowledge = {
        'terms': [],
        'concepts': []
    }
    
    # Analyze Python files
    python_files = list(repo_path.rglob('*.py'))[:50]  # Limit for performance
    
    for py_file in python_files:
        try:
            content = py_file.read_text(encoding='utf-8', errors='ignore')
            
            # Extract from docstrings
            docstring_pattern = r'"""(.*?)"""'
            docstrings = re.findall(docstring_pattern, content, re.DOTALL)
            for docstring in docstrings:
                # Extract capitalized terms
                terms = re.findall(r'\b[A-Z][a-z]+\b', docstring)
                knowledge['terms'].extend(terms)
            
            # Extract from comments
            comment_lines = [line for line in content.split('\n') if line.strip().startswith('#')]
            for comment in comment_lines:
                terms = re.findall(r'\b[A-Z][a-z]+\b', comment)
                knowledge['terms'].extend(terms)
                
        except Exception:
            continue
    
    # Analyze JavaScript/TypeScript files
    js_files = list(repo_path.rglob('*.js')) + list(repo_path.rglob('*.ts'))
    js_files = js_files[:50]  # Limit for performance
    
    for js_file in js_files:
        try:
            content = js_file.read_text(encoding='utf-8', errors='ignore')
            
            # Extract from JSDoc comments
            jsdoc_pattern = r'/\*\*(.*?)\*/'
            jsdocs = re.findall(jsdoc_pattern, content, re.DOTALL)
            for jsdoc in jsdocs:
                terms = re.findall(r'\b[A-Z][a-z]+\b', jsdoc)
                knowledge['terms'].extend(terms)
            
            # Extract from single-line comments
            comment_lines = [line for line in content.split('\n') if '//' in line]
            for comment in comment_lines:
                terms = re.findall(r'\b[A-Z][a-z]+\b', comment)
                knowledge['terms'].extend(terms)
                
        except Exception:
            continue
    
    # Get most common terms
    term_counts = {}
    for term in knowledge['terms']:
        if len(term) > 3:  # Ignore short words
            term_counts[term] = term_counts.get(term, 0) + 1
    
    # Get terms that appear at least 2 times
    knowledge['concepts'] = [term for term, count in term_counts.items() if count >= 2]
    knowledge['concepts'] = knowledge['concepts'][:15]  # Top 15
    
    return knowledge


def extract_from_structure(repo_path: Path) -> List[str]:
    """
    Extract domain terms from file and directory structure.
    
    Args:
        repo_path: Path to repository directory
        
    Returns:
        List of extracted terms
    """
    terms = []
    
    # Get directory names (excluding common ones)
    exclude_dirs = {'src', 'lib', 'test', 'tests', 'docs', 'doc', 'build', 'dist', 'node_modules', '__pycache__', '.git'}
    
    for item in repo_path.iterdir():
        if item.is_dir() and item.name not in exclude_dirs:
            # Split camelCase or snake_case
            name = item.name
            if '_' in name:
                terms.extend(name.split('_'))
            elif re.search(r'[a-z][A-Z]', name):
                # camelCase
                parts = re.findall(r'[a-z]+|[A-Z][a-z]+', name)
                terms.extend(parts)
            else:
                terms.append(name)
    
    # Get file names (Python modules, JS modules)
    python_files = list(repo_path.rglob('*.py'))[:100]
    for py_file in python_files:
        if py_file.stem not in ['__init__', 'test', 'tests']:
            name = py_file.stem
            if '_' in name:
                terms.extend(name.split('_'))
            else:
                terms.append(name)
    
    # Filter and return meaningful terms
    meaningful_terms = [t for t in terms if len(t) > 3 and t.isalpha()]
    return list(set(meaningful_terms))[:20]  # Top 20 unique terms

