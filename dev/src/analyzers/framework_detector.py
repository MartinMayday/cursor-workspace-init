"""
Framework detector module.

Detects frameworks and build tools from repository.
"""

from pathlib import Path
from typing import Dict, Any, List


def detect_framework(repo_path: Path) -> Dict[str, Any]:
    """
    Detect framework(s) from repository.
    
    Args:
        repo_path: Path to repository directory
        
    Returns:
        Dictionary with framework information
    """
    frameworks = []
    build_tools = []
    
    # Python frameworks
    if (repo_path / 'requirements.txt').exists() or (repo_path / 'pyproject.toml').exists():
        requirements = repo_path / 'requirements.txt'
        if requirements.exists():
            content = requirements.read_text().lower()
            if 'fastapi' in content or 'uvicorn' in content:
                frameworks.append('fastapi')
            if 'django' in content:
                frameworks.append('django')
            if 'flask' in content:
                frameworks.append('flask')
            if 'quart' in content:
                frameworks.append('quart')
    
    # JavaScript/TypeScript frameworks
    package_json = repo_path / 'package.json'
    if package_json.exists():
        try:
            import json
            data = json.loads(package_json.read_text())
            deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
            
            if 'react' in deps:
                frameworks.append('react')
            if 'next' in deps:
                frameworks.append('nextjs')
            if 'vue' in deps:
                frameworks.append('vue')
            if 'express' in deps:
                frameworks.append('express')
            if 'nestjs' in deps:
                frameworks.append('nestjs')
            
            # Build tools
            if 'webpack' in deps:
                build_tools.append('webpack')
            if 'vite' in deps:
                build_tools.append('vite')
            if 'rollup' in deps:
                build_tools.append('rollup')
        except:
            pass
    
    # Go frameworks
    go_mod = repo_path / 'go.mod'
    if go_mod.exists():
        try:
            content = go_mod.read_text().lower()
            if 'github.com/gin-gonic/gin' in content:
                frameworks.append('gin')
            if 'github.com/labstack/echo' in content:
                frameworks.append('echo')
            if 'github.com/gofiber/fiber' in content:
                frameworks.append('fiber')
        except:
            pass
    
    # Rust frameworks
    cargo_toml = repo_path / 'Cargo.toml'
    if cargo_toml.exists():
        try:
            content = cargo_toml.read_text().lower()
            if 'actix-web' in content:
                frameworks.append('actix')
            if 'axum' in content:
                frameworks.append('axum')
            if 'rocket' in content:
                frameworks.append('rocket')
        except:
            pass
    
    primary_framework = frameworks[0] if frameworks else 'unknown'
    
    return {
        'framework': primary_framework,
        'frameworks': frameworks,
        'build_tools': build_tools
    }

