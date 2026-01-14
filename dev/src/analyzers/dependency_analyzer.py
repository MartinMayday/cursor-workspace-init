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
    
    # Database detection
    databases = detect_databases(repo_path, dependencies)
    
    return {
        'dependencies': dependencies,
        'testing': primary_testing,
        'testing_frameworks': testing_frameworks,
        'linting': linting_tools,
        'formatting': formatting_tools,
        'databases': databases
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


def detect_databases(repo_path: Path, dependencies: List[str]) -> List[str]:
    """
    Detect databases from dependencies and configuration files.
    
    Args:
        repo_path: Path to repository directory
        dependencies: List of detected dependencies
        
    Returns:
        List of detected database names
    """
    databases = []
    deps_lower = [d.lower() for d in dependencies]
    
    # Python database libraries
    db_patterns = {
        'postgresql': ['psycopg2', 'psycopg', 'postgresql', 'asyncpg', 'pg8000'],
        'mysql': ['mysql', 'mysqlclient', 'pymysql', 'mysql-connector'],
        'sqlite': ['sqlite3'],
        'mongodb': ['pymongo', 'motor', 'mongoengine'],
        'redis': ['redis', 'hiredis'],
        'cassandra': ['cassandra-driver', 'cassandra'],
        'elasticsearch': ['elasticsearch', 'elasticsearch-dsl'],
        'dynamodb': ['boto3', 'dynamodb'],
        'neo4j': ['neo4j', 'py2neo'],
        'influxdb': ['influxdb', 'influxdb-client'],
        'couchdb': ['couchdb'],
        'sqlalchemy': ['sqlalchemy']  # ORM, not a DB but indicates SQL usage
    }
    
    for db_name, patterns in db_patterns.items():
        if any(pattern in dep for dep in deps_lower for pattern in patterns):
            if db_name not in databases:
                databases.append(db_name)
    
    # JavaScript/TypeScript database libraries
    package_json = repo_path / 'package.json'
    if package_json.exists():
        try:
            import json
            data = json.loads(package_json.read_text())
            deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
            deps_keys = [k.lower() for k in deps.keys()]
            
            js_db_patterns = {
                'postgresql': ['pg', 'postgres', 'postgresql', 'node-postgres'],
                'mysql': ['mysql', 'mysql2', 'mysqljs'],
                'mongodb': ['mongodb', 'mongoose', 'typegoose'],
                'redis': ['redis', 'ioredis', 'node-redis'],
                'sqlite': ['sqlite3', 'better-sqlite3'],
                'cassandra': ['cassandra-driver'],
                'elasticsearch': ['elasticsearch', '@elastic/elasticsearch'],
                'dynamodb': ['aws-sdk', '@aws-sdk/client-dynamodb'],
                'neo4j': ['neo4j-driver'],
                'influxdb': ['influx', '@influxdata/influxdb-client']
            }
            
            for db_name, patterns in js_db_patterns.items():
                if any(pattern in key for key in deps_keys for pattern in patterns):
                    if db_name not in databases:
                        databases.append(db_name)
        except:
            pass
    
    # Check configuration files for database connections
    config_db = detect_databases_from_config(repo_path)
    for db in config_db:
        if db not in databases:
            databases.append(db)
    
    return databases


def detect_databases_from_config(repo_path: Path) -> List[str]:
    """Detect databases from configuration files."""
    databases = []
    
    # Check for common database config files
    # .env files
    env_files = list(repo_path.glob('.env*'))
    for env_file in env_files:
        try:
            content = env_file.read_text()
            # Look for database connection strings
            if 'postgres' in content.lower() or 'postgresql' in content.lower():
                if 'postgresql' not in databases:
                    databases.append('postgresql')
            if 'mysql' in content.lower():
                if 'mysql' not in databases:
                    databases.append('mysql')
            if 'mongodb' in content.lower() or 'mongo' in content.lower():
                if 'mongodb' not in databases:
                    databases.append('mongodb')
            if 'redis' in content.lower():
                if 'redis' not in databases:
                    databases.append('redis')
        except:
            pass
    
    # Check docker-compose for database services
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
                            image = service_config.get('image', '')
                            if any(db in image.lower() for db in ['postgres', 'mysql', 'mongo', 'redis', 'cassandra', 'elasticsearch']):
                                if 'postgres' in image.lower() and 'postgresql' not in databases:
                                    databases.append('postgresql')
                                elif 'mysql' in image.lower() and 'mysql' not in databases:
                                    databases.append('mysql')
                                elif 'mongo' in image.lower() and 'mongodb' not in databases:
                                    databases.append('mongodb')
                                elif 'redis' in image.lower() and 'redis' not in databases:
                                    databases.append('redis')
                                elif 'cassandra' in image.lower() and 'cassandra' not in databases:
                                    databases.append('cassandra')
                                elif 'elasticsearch' in image.lower() and 'elasticsearch' not in databases:
                                    databases.append('elasticsearch')
            except:
                pass
            break
    
    return databases

