"""
Coding standards detector module.

Extracts coding standards and style configurations from repository files.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional


def detect_coding_standards(repo_path: Path) -> Dict[str, Any]:
    """
    Detect coding standards from repository.
    
    Args:
        repo_path: Path to repository directory
        
    Returns:
        Dictionary with coding standards information
    """
    standards = {
        'style_guide': 'unknown',
        'line_length': None,
        'indentation': None,
        'quote_style': None,
        'config_files': []
    }
    
    # Python coding standards
    python_standards = detect_python_standards(repo_path)
    if python_standards:
        standards.update(python_standards)
    
    # JavaScript/TypeScript coding standards
    js_standards = detect_javascript_standards(repo_path)
    if js_standards:
        standards.update(js_standards)
    
    # Go coding standards
    go_standards = detect_go_standards(repo_path)
    if go_standards:
        standards.update(go_standards)
    
    # Generic style files
    generic_standards = detect_generic_standards(repo_path)
    if generic_standards:
        standards.update(generic_standards)
    
    return standards


def detect_python_standards(repo_path: Path) -> Optional[Dict[str, Any]]:
    """Detect Python coding standards."""
    standards = {}
    config_files = []
    
    # Check for pyproject.toml (PEP 518/621)
    pyproject = repo_path / 'pyproject.toml'
    if pyproject.exists():
        try:
            try:
                import tomli
                with open(pyproject, 'rb') as f:
                    data = tomli.load(f)
            except ImportError:
                import tomllib
                with open(pyproject, 'rb') as f:
                    data = tomllib.load(f)
            
            config_files.append('pyproject.toml')
            
            # Check for black configuration
            if 'tool' in data and 'black' in data['tool']:
                black_config = data['tool']['black']
                standards['style_guide'] = 'black'
                if 'line-length' in black_config:
                    standards['line_length'] = black_config['line-length']
            
            # Check for ruff configuration
            if 'tool' in data and 'ruff' in data['tool']:
                ruff_config = data['tool']['ruff']
                if standards.get('style_guide') == 'unknown':
                    standards['style_guide'] = 'ruff'
                if 'line-length' in ruff_config:
                    standards['line_length'] = ruff_config['line-length']
            
            # Check for pylint configuration
            if 'tool' in data and 'pylint' in data['tool']:
                if standards.get('style_guide') == 'unknown':
                    standards['style_guide'] = 'pylint'
            
            # Check for flake8 configuration
            if 'tool' in data and 'flake8' in data['tool']:
                if standards.get('style_guide') == 'unknown':
                    standards['style_guide'] = 'flake8'
                if 'max-line-length' in data['tool']['flake8']:
                    standards['line_length'] = data['tool']['flake8']['max-line-length']
        except:
            pass
    
    # Check for setup.cfg
    setup_cfg = repo_path / 'setup.cfg'
    if setup_cfg.exists():
        try:
            config_files.append('setup.cfg')
            content = setup_cfg.read_text()
            
            # Check for black
            if '[tool.black]' in content or '[black]' in content:
                standards['style_guide'] = 'black'
                for line in content.split('\n'):
                    if 'line-length' in line.lower():
                        try:
                            standards['line_length'] = int(line.split('=')[1].strip())
                        except:
                            pass
            
            # Check for flake8
            if '[flake8]' in content:
                if standards.get('style_guide') == 'unknown':
                    standards['style_guide'] = 'flake8'
                for line in content.split('\n'):
                    if 'max-line-length' in line.lower():
                        try:
                            standards['line_length'] = int(line.split('=')[1].strip())
                        except:
                            pass
        except:
            pass
    
    # Check for .flake8 or setup.cfg
    flake8_config = repo_path / '.flake8'
    if flake8_config.exists():
        config_files.append('.flake8')
        if standards.get('style_guide') == 'unknown':
            standards['style_guide'] = 'flake8'
    
    # Check for .pylintrc
    pylintrc = repo_path / '.pylintrc'
    if pylintrc.exists():
        config_files.append('.pylintrc')
        if standards.get('style_guide') == 'unknown':
            standards['style_guide'] = 'pylint'
    
    # Check for pyproject.toml PEP 8 reference
    if pyproject.exists():
        try:
            try:
                import tomli
                with open(pyproject, 'rb') as f:
                    data = tomli.load(f)
            except ImportError:
                import tomllib
                with open(pyproject, 'rb') as f:
                    data = tomllib.load(f)
            
            # Check if PEP 8 is mentioned in project metadata
            if 'project' in data:
                keywords = data['project'].get('keywords', [])
                if any('pep8' in str(k).lower() or 'pep 8' in str(k).lower() for k in keywords):
                    if standards.get('style_guide') == 'unknown':
                        standards['style_guide'] = 'PEP 8'
        except:
            pass
    
    # Default to PEP 8 if Python detected but no config found
    if not standards and (repo_path / 'requirements.txt').exists() or (repo_path / 'pyproject.toml').exists():
        standards['style_guide'] = 'PEP 8'
        standards['line_length'] = 79  # PEP 8 default
    
    if standards:
        standards['config_files'] = config_files
        return standards
    
    return None


def detect_javascript_standards(repo_path: Path) -> Optional[Dict[str, Any]]:
    """Detect JavaScript/TypeScript coding standards."""
    standards = {}
    config_files = []
    
    package_json = repo_path / 'package.json'
    if package_json.exists():
        try:
            import json
            data = json.loads(package_json.read_text())
            config_files.append('package.json')
            
            # Check for ESLint
            if 'eslintConfig' in data or 'eslint' in str(data.get('devDependencies', {})):
                standards['style_guide'] = 'ESLint'
                config_files.append('.eslintrc*')
            
            # Check for Prettier
            if 'prettier' in str(data.get('devDependencies', {})) or 'prettier' in str(data.get('dependencies', {})):
                if standards.get('style_guide') == 'unknown':
                    standards['style_guide'] = 'Prettier'
                config_files.append('.prettierrc*')
            
            # Check for Standard JS
            if 'standard' in str(data.get('devDependencies', {})):
                standards['style_guide'] = 'Standard JS'
        except:
            pass
    
    # Check for .eslintrc files
    eslint_configs = [
        '.eslintrc',
        '.eslintrc.js',
        '.eslintrc.json',
        '.eslintrc.yaml',
        '.eslintrc.yml',
        '.eslintrc.cjs'
    ]
    for config_name in eslint_configs:
        config_file = repo_path / config_name
        if config_file.exists():
            config_files.append(config_name)
            if standards.get('style_guide') == 'unknown':
                standards['style_guide'] = 'ESLint'
            break
    
    # Check for .prettierrc files
    prettier_configs = [
        '.prettierrc',
        '.prettierrc.js',
        '.prettierrc.json',
        '.prettierrc.yaml',
        '.prettierrc.yml',
        '.prettierrc.toml'
    ]
    for config_name in prettier_configs:
        config_file = repo_path / config_name
        if config_file.exists():
            config_files.append(config_name)
            if standards.get('style_guide') == 'unknown':
                standards['style_guide'] = 'Prettier'
            break
    
    # Check for .editorconfig
    editorconfig = repo_path / '.editorconfig'
    if editorconfig.exists():
        config_files.append('.editorconfig')
        try:
            content = editorconfig.read_text()
            for line in content.split('\n'):
                if 'max_line_length' in line.lower():
                    try:
                        standards['line_length'] = int(line.split('=')[1].strip())
                    except:
                        pass
        except:
            pass
    
    if standards:
        standards['config_files'] = config_files
        return standards
    
    return None


def detect_go_standards(repo_path: Path) -> Optional[Dict[str, Any]]:
    """Detect Go coding standards."""
    standards = {}
    config_files = []
    
    # Go follows gofmt by default
    go_mod = repo_path / 'go.mod'
    if go_mod.exists():
        standards['style_guide'] = 'gofmt'
        config_files.append('go.mod')
    
    # Check for golangci-lint config
    golangci_configs = [
        '.golangci.yml',
        '.golangci.yaml',
        '.golangci.toml',
        '.golangci.json'
    ]
    for config_name in golangci_configs:
        config_file = repo_path / config_name
        if config_file.exists():
            config_files.append(config_name)
            standards['style_guide'] = 'golangci-lint'
            break
    
    if standards:
        standards['config_files'] = config_files
        return standards
    
    return None


def detect_generic_standards(repo_path: Path) -> Optional[Dict[str, Any]]:
    """Detect generic coding standards from common config files."""
    standards = {}
    config_files = []
    
    # Check for .editorconfig (cross-language)
    editorconfig = repo_path / '.editorconfig'
    if editorconfig.exists():
        config_files.append('.editorconfig')
        try:
            content = editorconfig.read_text()
            for line in content.split('\n'):
                if 'indent_size' in line.lower() or 'indent_style' in line.lower():
                    if 'indent_style' in line.lower():
                        indent_style = line.split('=')[1].strip() if '=' in line else 'space'
                        standards['indentation'] = indent_style
                if 'max_line_length' in line.lower():
                    try:
                        standards['line_length'] = int(line.split('=')[1].strip())
                    except:
                        pass
        except:
            pass
    
    # Check for .clang-format (C/C++)
    clang_format = repo_path / '.clang-format'
    if clang_format.exists():
        config_files.append('.clang-format')
        if standards.get('style_guide') == 'unknown':
            standards['style_guide'] = 'clang-format'
    
    if standards:
        standards['config_files'] = config_files
        return standards
    
    return None

