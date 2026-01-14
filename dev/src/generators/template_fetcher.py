"""
Template fetcher module.

Pulls templates from GitHub repository with caching and authentication support.
"""

import os
import subprocess
import shutil
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
from hashlib import sha256


def get_template_repo_url() -> str:
    """
    Get template repository URL from config or environment variable.
    
    Returns:
        GitHub repository URL
    """
    # Check environment variable first
    repo_url = os.getenv('CURSOR_TEMPLATES_REPO_URL')
    if repo_url:
        return repo_url
    
    # Try to read from config file
    try:
        import yaml
        config_path = Path(__file__).parent.parent / 'config' / 'template_config.yaml'
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                if config and 'template_repository' in config:
                    return config['template_repository'].get('url', '')
    except (ImportError, FileNotFoundError, KeyError):
        pass
    
    # Default repository URL
    return 'https://github.com/MartinMayday/cursor-workspace-templates.git'


def get_template_branch() -> str:
    """
    Get template repository branch from config or environment variable.
    
    Returns:
        Branch name (default: main)
    """
    # Check environment variable first
    branch = os.getenv('CURSOR_TEMPLATES_BRANCH')
    if branch:
        return branch
    
    # Try to read from config file
    try:
        import yaml
        config_path = Path(__file__).parent.parent / 'config' / 'template_config.yaml'
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                if config and 'template_repository' in config:
                    return config['template_repository'].get('branch', 'main')
    except (ImportError, FileNotFoundError, KeyError):
        pass
    
    return 'main'


def get_template_cache_dir() -> Path:
    """
    Get template cache directory path.
    
    Returns:
        Path to cache directory
    """
    cache_dir = os.getenv('CURSOR_TEMPLATE_CACHE_DIR')
    if cache_dir:
        return Path(cache_dir)
    
    # Default cache directory
    artifacts_dir = os.getenv('CURSOR_ARTIFACTS_DIR', 'artifacts')
    return Path(artifacts_dir) / '.template-cache'


def clone_or_update_template_repo(repo_url: Optional[str] = None, 
                                   branch: Optional[str] = None,
                                   cache_dir: Optional[Path] = None) -> Path:
    """
    Clone or update template repository from GitHub.
    
    Args:
        repo_url: Repository URL (default: from config/env)
        branch: Branch name (default: main)
        cache_dir: Cache directory path (default: artifacts/.template-cache)
        
    Returns:
        Path to cloned repository directory
    """
    repo_url = repo_url or get_template_repo_url()
    branch = branch or get_template_branch()
    cache_dir = cache_dir or get_template_cache_dir()
    
    # Create cache directory
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a hash-based directory name for the repository
    repo_hash = sha256(repo_url.encode()).hexdigest()[:16]
    repo_cache_dir = cache_dir / f'repo-{repo_hash}'
    
    # Check if repository is already cloned
    if (repo_cache_dir / '.git').exists():
        # Update existing repository
        try:
            subprocess.run(
                ['git', 'fetch', 'origin'],
                cwd=repo_cache_dir,
                check=True,
                capture_output=True
            )
            subprocess.run(
                ['git', 'checkout', branch],
                cwd=repo_cache_dir,
                check=True,
                capture_output=True
            )
            subprocess.run(
                ['git', 'pull', 'origin', branch],
                cwd=repo_cache_dir,
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError as e:
            # If update fails, try recloning
            shutil.rmtree(repo_cache_dir, ignore_errors=True)
            return clone_or_update_template_repo(repo_url, branch, cache_dir)
    else:
        # Clone repository
        try:
            subprocess.run(
                ['git', 'clone', '--depth', '1', '--branch', branch, repo_url, str(repo_cache_dir)],
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError as e:
            # If branch doesn't exist, try default branch
            if branch != 'main':
                return clone_or_update_template_repo(repo_url, 'main', cache_dir)
            raise RuntimeError(f"Failed to clone template repository: {e}")
    
    return repo_cache_dir


def get_template_files(repo_path: Path) -> Dict[str, Path]:
    """
    Get all template files from repository.
    
    Args:
        repo_path: Path to cloned repository
        
    Returns:
        Dictionary mapping template relative paths to full paths
    """
    templates = {}
    
    # Find all .template files
    for template_file in repo_path.rglob('*.template'):
        # Get relative path from repo root
        rel_path = template_file.relative_to(repo_path)
        templates[str(rel_path)] = template_file
    
    # Also find .mdc.template files
    for template_file in repo_path.rglob('*.mdc.template'):
        rel_path = template_file.relative_to(repo_path)
        templates[str(rel_path)] = template_file
    
    return templates


def fetch_templates(repo_url: Optional[str] = None,
                   branch: Optional[str] = None,
                   cache_dir: Optional[Path] = None) -> Dict[str, Path]:
    """
    Fetch templates from GitHub repository.
    
    Args:
        repo_url: Repository URL (default: from config/env)
        branch: Branch name (default: main)
        cache_dir: Cache directory path (default: artifacts/.template-cache)
        
    Returns:
        Dictionary mapping template relative paths to full paths
    """
    repo_path = clone_or_update_template_repo(repo_url, branch, cache_dir)
    return get_template_files(repo_path)


def get_template_content(template_path: Path) -> str:
    """
    Read template file content.
    
    Args:
        template_path: Path to template file
        
    Returns:
        Template content as string
    """
    return template_path.read_text(encoding='utf-8')


def clear_template_cache(cache_dir: Optional[Path] = None):
    """
    Clear template cache directory.
    
    Args:
        cache_dir: Cache directory path (default: artifacts/.template-cache)
    """
    cache_dir = cache_dir or get_template_cache_dir()
    if cache_dir.exists():
        shutil.rmtree(cache_dir, ignore_errors=True)
