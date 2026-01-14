"""
Project type detector module.

Classifies project type based on directory structure and files.
"""

from pathlib import Path
from typing import Dict, Any, List


def detect_project_type(repo_path: Path) -> Dict[str, Any]:
    """
    Detect project type from repository structure with deep analysis.
    
    Args:
        repo_path: Path to repository directory
        
    Returns:
        Dictionary with project type information
    """
    # Deep analysis: Check for microservices indicators
    services_dir = repo_path / 'services'
    if services_dir.exists() and services_dir.is_dir():
        services = [d.name for d in services_dir.iterdir() if d.is_dir()]
        # Analyze service structure
        ports = analyze_service_ports(repo_path, services)
        return {
            'type': 'microservices',
            'services': services,
            'architecture': 'microservices',
            'ports': ports,
            'file_organization': analyze_file_organization(repo_path)
        }
    
    # Deep analysis: Check for monorepo indicators
    packages_dir = repo_path / 'packages'
    apps_dir = repo_path / 'apps'
    if (packages_dir.exists() and packages_dir.is_dir()) or \
       (apps_dir.exists() and apps_dir.is_dir()):
        # Analyze monorepo structure
        packages = []
        if packages_dir.exists():
            packages.extend([d.name for d in packages_dir.iterdir() if d.is_dir()])
        if apps_dir.exists():
            packages.extend([d.name for d in apps_dir.iterdir() if d.is_dir()])
        
        return {
            'type': 'monorepo',
            'services': packages,
            'architecture': 'monorepo',
            'ports': [],
            'file_organization': analyze_file_organization(repo_path)
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
    
    # Check for CLI indicators (comprehensive detection)
    cli_indicators = detect_cli_indicators(repo_path)
    if cli_indicators['is_cli']:
        result = {
            'type': 'cli',
            'services': [],
            'architecture': 'cli',
            'ports': [],
            'file_organization': analyze_file_organization(repo_path)
        }
        # Add detection reasons for debugging (optional)
        if cli_indicators.get('reasons'):
            result['detection_reasons'] = cli_indicators['reasons']
        return result
    
    # Default to unknown
    return {
        'type': 'unknown',
        'services': [],
        'architecture': 'unknown',
        'ports': [],
        'file_organization': analyze_file_organization(repo_path)
    }


def detect_cli_indicators(repo_path: Path) -> Dict[str, Any]:
    """
    Detect CLI tool indicators with comprehensive analysis.
    
    Args:
        repo_path: Path to repository directory
        
    Returns:
        Dictionary with CLI detection results
    """
    indicators = {
        'is_cli': False,
        'confidence': 0,
        'reasons': []
    }
    
    # Strong indicators (high confidence)
    # 1. Check for common CLI directory structures
    cli_dirs = ['cmd', 'cli', 'commands', 'scripts', 'bin']
    for cli_dir in cli_dirs:
        if (repo_path / cli_dir).exists() and (repo_path / cli_dir).is_dir():
            indicators['is_cli'] = True
            indicators['confidence'] += 3
            indicators['reasons'].append(f"Has {cli_dir}/ directory")
    
    # 2. Check for main entry point files with CLI patterns
    main_files = list(repo_path.glob('*.py')) + list((repo_path / 'src').glob('*.py')) if (repo_path / 'src').exists() else []
    for main_file in main_files[:10]:  # Limit to first 10 for performance
        try:
            content = main_file.read_text(encoding='utf-8', errors='ignore')
            
            # Check for argparse usage
            if 'argparse' in content and ('ArgumentParser' in content or 'add_argument' in content):
                indicators['is_cli'] = True
                indicators['confidence'] += 2
                indicators['reasons'].append(f"{main_file.name} uses argparse")
                break
            
            # Check for click usage
            if 'import click' in content or 'from click import' in content:
                indicators['is_cli'] = True
                indicators['confidence'] += 2
                indicators['reasons'].append(f"{main_file.name} uses click")
                break
            
            # Check for main entry point pattern
            if 'if __name__' in content and '__main__' in content:
                # Check if it calls a main function or has command-line logic
                if 'main()' in content or 'sys.argv' in content:
                    indicators['confidence'] += 1
                    indicators['reasons'].append(f"{main_file.name} has main entry point")
        except:
            continue
    
    # 3. Check for setup.py or pyproject.toml with console_scripts
    setup_py = repo_path / 'setup.py'
    if setup_py.exists():
        try:
            content = setup_py.read_text(encoding='utf-8', errors='ignore')
            if 'console_scripts' in content or 'entry_points' in content:
                indicators['is_cli'] = True
                indicators['confidence'] += 3
                indicators['reasons'].append("setup.py has console_scripts entry_points")
        except:
            pass
    
    pyproject_toml = repo_path / 'pyproject.toml'
    if pyproject_toml.exists():
        try:
            content = pyproject_toml.read_text(encoding='utf-8', errors='ignore')
            if 'console_scripts' in content or '[project.scripts]' in content or '[tool.poetry.scripts]' in content:
                indicators['is_cli'] = True
                indicators['confidence'] += 3
                indicators['reasons'].append("pyproject.toml has console_scripts")
        except:
            pass
    
    # 4. Check for Go CLI patterns
    if (repo_path / 'main.go').exists() or (repo_path / 'cmd').exists():
        go_mod = repo_path / 'go.mod'
        if go_mod.exists():
            indicators['is_cli'] = True
            indicators['confidence'] += 2
            indicators['reasons'].append("Go project with cmd/ or main.go")
    
    # 5. Check README for CLI mentions
    readme_files = [
        repo_path / 'README.md',
        repo_path / 'README.rst',
        repo_path / 'README.txt'
    ]
    for readme in readme_files:
        if readme.exists():
            try:
                content = readme.read_text(encoding='utf-8', errors='ignore').lower()
                cli_keywords = ['command-line', 'cli tool', 'command line', 'cli interface', 'usage:', '--help', 'arguments']
                if any(keyword in content for keyword in cli_keywords):
                    indicators['confidence'] += 1
                    indicators['reasons'].append("README mentions CLI usage")
                    break
            except:
                continue
    
    # 6. Negative indicators (reduce confidence if present)
    # If it has web/API indicators, it's probably not a CLI
    web_indicators = ['routes', 'controllers', 'handlers', 'api', 'endpoints', 'app.py', 'main.py']
    has_web_structure = any((repo_path / d).exists() for d in web_indicators)
    
    # Check for web frameworks in dependencies
    requirements = repo_path / 'requirements.txt'
    if requirements.exists():
        try:
            content = requirements.read_text(encoding='utf-8', errors='ignore').lower()
            web_frameworks = ['flask', 'django', 'fastapi', 'tornado', 'bottle', 'cherrypy']
            if any(fw in content for fw in web_frameworks):
                # Reduce confidence but don't rule out CLI (could be CLI + web)
                if has_web_structure:
                    indicators['confidence'] -= 2
                    indicators['reasons'].append("Has web framework, likely not pure CLI")
        except:
            pass
    
    # 7. Check for package.json with CLI scripts
    package_json = repo_path / 'package.json'
    if package_json.exists():
        try:
            import json
            data = json.loads(package_json.read_text())
            # Check for bin field (CLI indicator)
            if 'bin' in data:
                indicators['is_cli'] = True
                indicators['confidence'] += 2
                indicators['reasons'].append("package.json has bin field (CLI)")
        except:
            pass
    
    # Final decision: CLI if confidence >= 2 or explicit CLI indicators
    if indicators['confidence'] >= 2:
        indicators['is_cli'] = True
    
    return indicators


def analyze_file_organization(repo_path: Path) -> str:
    """
    Analyze file organization patterns from directory structure.
    
    Args:
        repo_path: Path to repository directory
        
    Returns:
        String describing file organization pattern
    """
    patterns = []
    
    # Check for common organization patterns
    if (repo_path / 'src').exists():
        patterns.append('src-based')
    
    if (repo_path / 'lib').exists():
        patterns.append('lib-based')
    
    if (repo_path / 'app').exists() or (repo_path / 'apps').exists():
        patterns.append('app-based')
    
    # Check for MVC pattern
    if (repo_path / 'models').exists() or (repo_path / 'views').exists() or (repo_path / 'controllers').exists():
        patterns.append('MVC')
    
    # Check for feature-based organization
    if (repo_path / 'features').exists() or (repo_path / 'modules').exists():
        patterns.append('feature-based')
    
    # Check for domain-driven design
    if (repo_path / 'domain').exists() or (repo_path / 'domains').exists():
        patterns.append('DDD')
    
    # Check for layered architecture
    if (repo_path / 'layers').exists() or (repo_path / 'infrastructure').exists():
        patterns.append('layered')
    
    if patterns:
        return ', '.join(patterns)
    
    return 'standard'


def analyze_service_ports(repo_path: Path, services: List[str]) -> List[int]:
    """
    Analyze ports from service configurations.
    
    Args:
        repo_path: Path to repository directory
        services: List of service names
        
    Returns:
        List of detected ports
    """
    ports = []
    
    # Check docker-compose for ports
    compose_files = [
        repo_path / 'docker-compose.yml',
        repo_path / 'docker-compose.yaml',
        repo_path / 'compose.yml',
        repo_path / 'compose.yaml'
    ]
    
    for compose_file in compose_files:
        if compose_file.exists():
            try:
                try:
                    import yaml
                except ImportError:
                    yaml = None
                
                if yaml:
                    with open(compose_file, 'r') as f:
                        data = yaml.safe_load(f)
                    if data and 'services' in data:
                        for service_name, service_config in data['services'].items():
                            if 'ports' in service_config:
                                for port_mapping in service_config['ports']:
                                    if isinstance(port_mapping, str):
                                        # Format: "8000:8000" or "8000"
                                        port = port_mapping.split(':')[0]
                                        try:
                                            ports.append(int(port))
                                        except:
                                            pass
                                    elif isinstance(port_mapping, dict) and 'published' in port_mapping:
                                        ports.append(port_mapping['published'])
            except:
                pass
            break
    
    # Check for .env files with port configurations
    env_files = list(repo_path.glob('.env*'))
    for env_file in env_files:
        try:
            content = env_file.read_text()
            # Look for PORT= or PORT: patterns
            import re
            port_matches = re.findall(r'PORT[=:]\s*(\d+)', content, re.IGNORECASE)
            for port_str in port_matches:
                try:
                    ports.append(int(port_str))
                except:
                    pass
        except:
            pass
    
    return list(set(ports))  # Remove duplicates

