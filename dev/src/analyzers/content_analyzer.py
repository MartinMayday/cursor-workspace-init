"""
Content analyzer module.

Analyzes README, documentation, and project context.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import re


def analyze_content(repo_path: Path) -> Dict[str, Any]:
    """
    Analyze README and documentation for project context.
    
    Args:
        repo_path: Path to repository directory
        
    Returns:
        Dictionary with content analysis information
    """
    content_info = {
        'project_description': '',
        'project_purpose': '',
        'key_concepts': [],
        'documentation_sources': [],
        'readme_found': False,
        'docs_structure': []
    }
    
    # Analyze README
    readme_info = analyze_readme(repo_path)
    if readme_info:
        content_info.update(readme_info)
        content_info['readme_found'] = True
    
    # Analyze documentation directory
    docs_info = analyze_documentation(repo_path)
    if docs_info:
        content_info['docs_structure'] = docs_info.get('structure', [])
        content_info['documentation_sources'].extend(docs_info.get('sources', []))
    
    # Extract key concepts from codebase
    concepts = extract_key_concepts(repo_path)
    if concepts:
        content_info['key_concepts'].extend(concepts)
    
    return content_info


def analyze_readme(repo_path: Path) -> Optional[Dict[str, Any]]:
    """Analyze README file for project information."""
    readme_files = [
        'README.md',
        'README.rst',
        'README.txt',
        'readme.md',
        'Readme.md'
    ]
    
    for readme_name in readme_files:
        readme_path = repo_path / readme_name
        if readme_path.exists():
            try:
                content = readme_path.read_text()
                
                info = {
                    'readme_file': readme_name,
                    'project_description': extract_description(content),
                    'project_purpose': extract_purpose(content),
                    'documentation_sources': extract_doc_links(content)
                }
                
                return info
            except:
                pass
    
    return None


def extract_description(content: str) -> str:
    """Extract project description from README."""
    # Look for description in first few paragraphs
    lines = content.split('\n')
    description_parts = []
    
    # Skip title and badges
    skip_patterns = [r'^#+\s', r'^\[!\[', r'^<img', r'^---', r'^```']
    in_code_block = False
    
    for line in lines[:50]:  # Check first 50 lines
        # Track code blocks
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            continue
        
        if in_code_block:
            continue
        
        # Skip title, badges, separators
        if any(re.match(pattern, line) for pattern in skip_patterns):
            continue
        
        # Collect meaningful content
        stripped = line.strip()
        if stripped and len(stripped) > 20:
            description_parts.append(stripped)
            if len(description_parts) >= 3:  # Get first 3 meaningful paragraphs
                break
    
    description = ' '.join(description_parts)
    # Clean up markdown links and formatting
    description = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', description)
    description = re.sub(r'\*\*([^\*]+)\*\*', r'\1', description)
    description = re.sub(r'\*([^\*]+)\*', r'\1', description)
    
    return description[:500] if description else ''  # Limit length


def extract_purpose(content: str) -> str:
    """Extract project purpose from README."""
    # Look for common purpose indicators
    purpose_patterns = [
        r'(?:^|\n)#+\s*(?:About|Purpose|What|Overview|Introduction)',
        r'(?:^|\n)##\s*(?:About|Purpose|What|Overview|Introduction)',
        r'This (?:project|library|tool|application) (?:is|provides|aims to|allows)',
        r'(?:^|\n)(?:Purpose|Goal|Mission):\s*(.+)',
    ]
    
    for pattern in purpose_patterns:
        match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
        if match:
            # Extract following paragraph
            start = match.end()
            end = content.find('\n\n', start)
            if end == -1:
                end = min(start + 300, len(content))
            purpose = content[start:end].strip()
            # Clean up markdown
            purpose = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', purpose)
            purpose = re.sub(r'\*\*([^\*]+)\*\*', r'\1', purpose)
            return purpose[:300]
    
    return ''


def extract_doc_links(content: str) -> List[str]:
    """Extract documentation links from README."""
    links = []
    
    # Find markdown links
    link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
    matches = re.findall(link_pattern, content)
    
    for text, url in matches:
        # Filter for documentation-related links
        if any(keyword in text.lower() or keyword in url.lower() 
               for keyword in ['doc', 'read', 'guide', 'tutorial', 'api', 'reference']):
            if url.startswith('http'):
                links.append(url)
    
    # Find plain URLs
    url_pattern = r'https?://[^\s\)]+'
    urls = re.findall(url_pattern, content)
    for url in urls:
        if any(keyword in url.lower() for keyword in ['doc', 'read', 'guide', 'tutorial', 'api', 'reference']):
            links.append(url)
    
    return list(set(links))[:10]  # Limit to 10 unique links


def analyze_documentation(repo_path: Path) -> Optional[Dict[str, Any]]:
    """Analyze documentation directory structure."""
    docs_info = {
        'structure': [],
        'sources': []
    }
    
    # Common documentation directories
    docs_dirs = [
        'docs',
        'documentation',
        'doc',
        'wiki',
        'guides'
    ]
    
    for docs_dir_name in docs_dirs:
        docs_dir = repo_path / docs_dir_name
        if docs_dir.exists() and docs_dir.is_dir():
            # List documentation files
            doc_files = []
            for ext in ['*.md', '*.rst', '*.txt', '*.html']:
                doc_files.extend(list(docs_dir.glob(ext)))
                doc_files.extend(list(docs_dir.glob(f'**/{ext}')))
            
            if doc_files:
                docs_info['structure'].append({
                    'directory': docs_dir_name,
                    'files': [f.name for f in doc_files[:20]]  # Limit to 20 files
                })
    
    # Check for Sphinx docs
    sphinx_conf = repo_path / 'docs' / 'conf.py'
    if sphinx_conf.exists():
        docs_info['sources'].append('Sphinx documentation')
    
    # Check for MkDocs
    mkdocs_yml = repo_path / 'mkdocs.yml'
    if mkdocs_yml.exists():
        docs_info['sources'].append('MkDocs documentation')
    
    if docs_info['structure'] or docs_info['sources']:
        return docs_info
    
    return None


def extract_key_concepts(repo_path: Path) -> List[str]:
    """Extract key concepts and terminology from codebase."""
    concepts = set()
    
    # Look for common concept files
    concept_files = [
        'CONCEPTS.md',
        'ARCHITECTURE.md',
        'TERMINOLOGY.md',
        'GLOSSARY.md'
    ]
    
    for concept_file in concept_files:
        concept_path = repo_path / concept_file
        if concept_path.exists():
            try:
                content = concept_path.read_text()
                # Extract headings and key terms
                headings = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
                concepts.update([h.strip() for h in headings[:10]])
            except:
                pass
    
    # Extract from README headings
    readme_path = repo_path / 'README.md'
    if readme_path.exists():
        try:
            content = readme_path.read_text()
            # Extract main headings (## and ###)
            headings = re.findall(r'^##+\s+(.+)$', content, re.MULTILINE)
            # Filter for meaningful concepts
            for heading in headings[:15]:
                heading = heading.strip()
                if len(heading) > 3 and len(heading) < 50:
                    concepts.add(heading)
        except:
            pass
    
    return list(concepts)[:20]  # Limit to 20 concepts


