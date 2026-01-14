"""
Source list generator module.

Generates source_list.json with relevant documentation URLs based on
detected technologies, frameworks, and tools.
"""

from pathlib import Path
from typing import Dict, Any, List
import json
import yaml


def load_documentation_sources(config_dir: Path) -> Dict[str, Any]:
    """
    Load documentation sources mapping from configuration.
    
    Args:
        config_dir: Path to config directory
        
    Returns:
        Dictionary with documentation sources mapping
    """
    sources_path = config_dir / 'documentation_sources.yaml'
    
    if sources_path.exists():
        try:
            with open(sources_path, 'r') as f:
                return yaml.safe_load(f) or {}
        except:
            return {}
    
    return {}


def get_language_sources(
    languages: List[str],
    sources_config: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Get documentation sources for detected languages.
    
    Args:
        languages: List of detected languages
        sources_config: Documentation sources configuration
        
    Returns:
        List of source dictionaries
    """
    sources = []
    language_sources = sources_config.get('languages', {})
    
    for language in languages:
        if language in language_sources:
            sources.extend(language_sources[language])
    
    return sources


def get_framework_sources(
    frameworks: List[str],
    sources_config: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Get documentation sources for detected frameworks.
    
    Args:
        frameworks: List of detected frameworks
        sources_config: Documentation sources configuration
        
    Returns:
        List of source dictionaries
    """
    sources = []
    framework_sources = sources_config.get('frameworks', {})
    
    for framework in frameworks:
        if framework in framework_sources:
            sources.extend(framework_sources[framework])
    
    return sources


def get_tool_sources(
    context: Dict[str, Any],
    sources_config: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Get documentation sources for detected tools.
    
    Args:
        context: Context variables dictionary
        sources_config: Documentation sources configuration
        
    Returns:
        List of source dictionaries
    """
    sources = []
    tool_sources = sources_config.get('tools', {})
    
    # Check testing frameworks
    testing_framework = context.get('testing_framework', '')
    if testing_framework and testing_framework != 'unknown':
        if testing_framework in tool_sources:
            sources.extend(tool_sources[testing_framework])
    
    # Check containerization tools
    containerization = context.get('containerization', [])
    if containerization:
        for tool in containerization:
            if isinstance(tool, str) and tool.lower() in tool_sources:
                sources.extend(tool_sources[tool.lower()])
    
    # Check orchestration tools
    orchestration = context.get('orchestration', [])
    if orchestration:
        for tool in orchestration:
            if isinstance(tool, str) and tool.lower() in tool_sources:
                sources.extend(tool_sources[tool.lower()])
    
    return sources


def get_database_sources(
    databases: List[str],
    sources_config: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Get documentation sources for detected databases.
    
    Args:
        databases: List of detected databases
        sources_config: Documentation sources configuration
        
    Returns:
        List of source dictionaries
    """
    sources = []
    database_sources = sources_config.get('databases', {})
    
    for database in databases:
        if database.lower() in database_sources:
            sources.extend(database_sources[database.lower()])
    
    return sources


def get_cloud_platform_sources(
    cloud_platforms: List[str],
    sources_config: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Get documentation sources for detected cloud platforms.
    
    Args:
        cloud_platforms: List of detected cloud platforms
        sources_config: Documentation sources configuration
        
    Returns:
        List of source dictionaries
    """
    sources = []
    cloud_sources = sources_config.get('cloud_platforms', {})
    
    for platform in cloud_platforms:
        if platform.lower() in cloud_sources:
            sources.extend(cloud_sources[platform.lower()])
    
    return sources


def get_project_specific_sources(
    context: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Get project-specific documentation sources from context.
    
    Args:
        context: Context variables dictionary
        
    Returns:
        List of source dictionaries
    """
    sources = []
    documentation_sources = context.get('documentation_sources', [])
    
    for doc_url in documentation_sources:
        if isinstance(doc_url, str) and doc_url.startswith('http'):
            sources.append({
                'type': 'documentation',
                'description': 'Project-specific documentation',
                'url': doc_url
            })
    
    return sources


def generate_source_list(
    context: Dict[str, Any],
    config_dir: Path
) -> List[Dict[str, Any]]:
    """
    Generate comprehensive source list based on context.
    
    Args:
        context: Context variables dictionary
        config_dir: Path to config directory
        
    Returns:
        List of source dictionaries
    """
    sources_config = load_documentation_sources(config_dir)
    all_sources = []
    seen_urls = set()
    
    # Get language sources
    languages = context.get('languages', [])
    if languages:
        language_sources = get_language_sources(languages, sources_config)
        for source in language_sources:
            if source.get('url') and source['url'] not in seen_urls:
                all_sources.append(source)
                seen_urls.add(source['url'])
    
    # Get framework sources
    frameworks = context.get('frameworks', [])
    if frameworks:
        framework_sources = get_framework_sources(frameworks, sources_config)
        for source in framework_sources:
            if source.get('url') and source['url'] not in seen_urls:
                all_sources.append(source)
                seen_urls.add(source['url'])
    
    # Get tool sources
    tool_sources = get_tool_sources(context, sources_config)
    for source in tool_sources:
        if source.get('url') and source['url'] not in seen_urls:
            all_sources.append(source)
            seen_urls.add(source['url'])
    
    # Get database sources
    databases = context.get('databases', [])
    if databases:
        database_sources = get_database_sources(databases, sources_config)
        for source in database_sources:
            if source.get('url') and source['url'] not in seen_urls:
                all_sources.append(source)
                seen_urls.add(source['url'])
    
    # Get cloud platform sources
    cloud_platforms = context.get('cloud_platforms', [])
    if cloud_platforms:
        cloud_sources = get_cloud_platform_sources(cloud_platforms, sources_config)
        for source in cloud_sources:
            if source.get('url') and source['url'] not in seen_urls:
                all_sources.append(source)
                seen_urls.add(source['url'])
    
    # Get project-specific sources
    project_sources = get_project_specific_sources(context)
    for source in project_sources:
        if source.get('url') and source['url'] not in seen_urls:
            all_sources.append(source)
            seen_urls.add(source['url'])
    
    return all_sources


def generate_source_list_json(
    context: Dict[str, Any],
    config_dir: Path,
    output_path: Path
) -> None:
    """
    Generate source_list.json file.
    
    Args:
        context: Context variables dictionary
        config_dir: Path to config directory
        output_path: Path where file should be generated
    """
    sources = generate_source_list(context, config_dir)
    
    source_list = {
        'sources': sources
    }
    
    source_list_path = output_path / 'source_list.json'
    source_list_path.write_text(json.dumps(source_list, indent=2))
    
    if sources:
        print(f"Generated source_list.json with {len(sources)} documentation sources")


