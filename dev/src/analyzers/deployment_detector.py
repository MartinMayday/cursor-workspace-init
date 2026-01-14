"""
Deployment detector module.

Detects deployment configurations (Docker, Kubernetes, cloud platforms).
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import re


def detect_deployment(repo_path: Path) -> Dict[str, Any]:
    """
    Detect deployment type and configurations from repository.
    
    Args:
        repo_path: Path to repository directory
        
    Returns:
        Dictionary with deployment information
    """
    deployment = {
        'deployment_type': 'unknown',
        'containerization': [],
        'orchestration': [],
        'cloud_platforms': [],
        'config_files': [],
        'networking': {}
    }
    
    # Detect Docker
    docker_info = detect_docker(repo_path)
    if docker_info:
        deployment['containerization'].extend(docker_info.get('types', []))
        deployment['config_files'].extend(docker_info.get('config_files', []))
        if deployment['deployment_type'] == 'unknown':
            deployment['deployment_type'] = 'docker'
    
    # Detect Kubernetes
    k8s_info = detect_kubernetes(repo_path)
    if k8s_info:
        deployment['orchestration'].extend(k8s_info.get('types', []))
        deployment['config_files'].extend(k8s_info.get('config_files', []))
        if deployment['deployment_type'] == 'unknown':
            deployment['deployment_type'] = 'kubernetes'
    
    # Detect cloud platforms
    cloud_info = detect_cloud_platforms(repo_path)
    if cloud_info:
        deployment['cloud_platforms'] = cloud_info.get('platforms', [])
        deployment['config_files'].extend(cloud_info.get('config_files', []))
        if deployment['deployment_type'] == 'unknown' and cloud_info.get('platforms'):
            deployment['deployment_type'] = cloud_info['platforms'][0]
    
    # Extract networking configuration
    networking = extract_networking_config(repo_path)
    if networking:
        deployment['networking'] = networking
    
    return deployment


def detect_docker(repo_path: Path) -> Optional[Dict[str, Any]]:
    """Detect Docker configurations."""
    docker_info = {
        'types': [],
        'config_files': []
    }
    
    # Check for Dockerfile
    dockerfile = repo_path / 'Dockerfile'
    if dockerfile.exists():
        docker_info['types'].append('docker')
        docker_info['config_files'].append('Dockerfile')
        
        # Try to extract port information
        try:
            content = dockerfile.read_text()
            # Look for EXPOSE directives
            expose_pattern = r'EXPOSE\s+(\d+)'
            ports = re.findall(expose_pattern, content, re.IGNORECASE)
            if ports:
                docker_info['ports'] = [int(p) for p in ports]
        except:
            pass
    
    # Check for docker-compose files
    compose_files = [
        'docker-compose.yml',
        'docker-compose.yaml',
        'docker-compose.override.yml',
        'docker-compose.override.yaml',
        'compose.yml',
        'compose.yaml'
    ]
    for compose_file in compose_files:
        compose_path = repo_path / compose_file
        if compose_path.exists():
            docker_info['types'].append('docker-compose')
            docker_info['config_files'].append(compose_file)
            
            # Try to extract networking info from compose
            try:
                try:
                    import yaml
                except ImportError:
                    yaml = None
                
                if yaml:
                    with open(compose_path, 'r') as f:
                        data = yaml.safe_load(f)
                    if data and 'services' in data:
                        ports = []
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
                        if ports:
                            docker_info['ports'] = ports
            except:
                pass
            break
    
    # Check for .dockerignore
    dockerignore = repo_path / '.dockerignore'
    if dockerignore.exists():
        docker_info['config_files'].append('.dockerignore')
    
    if docker_info['types']:
        return docker_info
    
    return None


def detect_kubernetes(repo_path: Path) -> Optional[Dict[str, Any]]:
    """Detect Kubernetes configurations."""
    k8s_info = {
        'types': [],
        'config_files': []
    }
    
    # Check for k8s directory
    k8s_dir = repo_path / 'k8s'
    if k8s_dir.exists() and k8s_dir.is_dir():
        k8s_info['types'].append('kubernetes')
        k8s_files = list(k8s_dir.glob('*.yaml')) + list(k8s_dir.glob('*.yml'))
        k8s_info['config_files'].extend([f.name for f in k8s_files])
    
    # Check for kubernetes directory
    kubernetes_dir = repo_path / 'kubernetes'
    if kubernetes_dir.exists() and kubernetes_dir.is_dir():
        k8s_info['types'].append('kubernetes')
        k8s_files = list(kubernetes_dir.glob('*.yaml')) + list(kubernetes_dir.glob('*.yml'))
        k8s_info['config_files'].extend([f.name for f in k8s_files])
    
    # Check for manifests directory
    manifests_dir = repo_path / 'manifests'
    if manifests_dir.exists() and manifests_dir.is_dir():
        manifest_files = list(manifests_dir.glob('*.yaml')) + list(manifests_dir.glob('*.yml'))
        # Check if they look like K8s manifests
        for manifest_file in manifest_files[:3]:  # Check first few
            try:
                content = manifest_file.read_text()
                if 'apiVersion' in content and ('kind:' in content or 'Kind:' in content):
                    k8s_info['types'].append('kubernetes')
                    k8s_info['config_files'].extend([f.name for f in manifest_files])
                    break
            except:
                pass
    
    # Check for Helm charts
    charts_dir = repo_path / 'charts'
    if charts_dir.exists() and charts_dir.is_dir():
        k8s_info['types'].append('helm')
        k8s_info['config_files'].append('charts/')
    
    # Check for Chart.yaml (Helm)
    chart_yaml = repo_path / 'Chart.yaml'
    if chart_yaml.exists():
        k8s_info['types'].append('helm')
        k8s_info['config_files'].append('Chart.yaml')
    
    if k8s_info['types']:
        return k8s_info
    
    return None


def detect_cloud_platforms(repo_path: Path) -> Optional[Dict[str, Any]]:
    """Detect cloud platform configurations."""
    cloud_info = {
        'platforms': [],
        'config_files': []
    }
    
    # AWS
    aws_indicators = [
        'serverless.yml',
        'serverless.yaml',
        'template.yaml',  # SAM
        'template.yml',
        '.aws/',
        'aws.yml',
        'aws.yaml'
    ]
    for indicator in aws_indicators:
        indicator_path = repo_path / indicator
        if indicator_path.exists():
            cloud_info['platforms'].append('aws')
            cloud_info['config_files'].append(indicator)
            break
    
    # Check for Terraform (could be any cloud)
    terraform_files = list(repo_path.glob('*.tf')) + list(repo_path.glob('*.tfvars'))
    if terraform_files:
        cloud_info['platforms'].append('terraform')
        cloud_info['config_files'].extend([f.name for f in terraform_files[:5]])
    
    # Azure
    azure_indicators = [
        'azure-pipelines.yml',
        'azure-pipelines.yaml',
        '.azure/',
        'host.json'  # Azure Functions
    ]
    for indicator in azure_indicators:
        indicator_path = repo_path / indicator
        if indicator_path.exists():
            cloud_info['platforms'].append('azure')
            cloud_info['config_files'].append(indicator)
            break
    
    # GCP
    gcp_indicators = [
        'app.yaml',
        'app.yml',
        '.gcloudignore',
        'cloudbuild.yaml',
        'cloudbuild.yml'
    ]
    for indicator in gcp_indicators:
        indicator_path = repo_path / indicator
        if indicator_path.exists():
            cloud_info['platforms'].append('gcp')
            cloud_info['config_files'].append(indicator)
            break
    
    # Vercel
    vercel_json = repo_path / 'vercel.json'
    if vercel_json.exists():
        cloud_info['platforms'].append('vercel')
        cloud_info['config_files'].append('vercel.json')
    
    # Netlify
    netlify_toml = repo_path / 'netlify.toml'
    if netlify_toml.exists():
        cloud_info['platforms'].append('netlify')
        cloud_info['config_files'].append('netlify.toml')
    
    # Heroku
    procfile = repo_path / 'Procfile'
    if procfile.exists():
        cloud_info['platforms'].append('heroku')
        cloud_info['config_files'].append('Procfile')
    
    if cloud_info['platforms']:
        return cloud_info
    
    return None


def extract_networking_config(repo_path: Path) -> Optional[Dict[str, Any]]:
    """Extract networking configuration from various config files."""
    networking = {}
    
    # Check docker-compose for networking
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
                        ports = []
                        networks = []
                        for service_name, service_config in data['services'].items():
                            if 'ports' in service_config:
                                for port_mapping in service_config['ports']:
                                    if isinstance(port_mapping, str):
                                        port = port_mapping.split(':')[0]
                                        try:
                                            ports.append(int(port))
                                        except:
                                            pass
                            if 'networks' in service_config:
                                if isinstance(service_config['networks'], list):
                                    networks.extend(service_config['networks'])
                                elif isinstance(service_config['networks'], dict):
                                    networks.extend(list(service_config['networks'].keys()))
                        if ports:
                            networking['ports'] = ports
                        if networks:
                            networking['networks'] = list(set(networks))
            except:
                pass
            break
    
    # Check for nginx config
    nginx_configs = list(repo_path.glob('nginx.conf')) + list(repo_path.glob('**/nginx.conf'))
    if nginx_configs:
        networking['reverse_proxy'] = 'nginx'
        networking['config_files'] = [str(f.relative_to(repo_path)) for f in nginx_configs[:3]]
    
    # Check for Caddy config
    caddyfile = repo_path / 'Caddyfile'
    if caddyfile.exists():
        networking['reverse_proxy'] = 'caddy'
        networking['config_files'] = ['Caddyfile']
    
    if networking:
        return networking
    
    return None

