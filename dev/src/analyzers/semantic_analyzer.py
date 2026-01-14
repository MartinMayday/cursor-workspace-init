"""
Semantic codebase analyzer using LLM.

Analyzes codebase semantically to understand purpose, architecture, patterns, and context.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import json
import re

from analyzers.llm_client import call_llm, load_llm_config


def analyze_codebase_semantically(repo_path: Path, max_files: int = 50) -> Dict[str, Any]:
    """
    Analyze codebase semantically using LLM.
    
    Args:
        repo_path: Path to repository directory
        max_files: Maximum number of files to analyze
        
    Returns:
        Dictionary with semantic analysis results
    """
    config = load_llm_config()
    
    # Check if LLM is configured
    provider = config["default_provider"]
    api_key = None
    if provider == "openai":
        api_key = config["openai_api_key"]
    elif provider == "anthropic":
        api_key = config["anthropic_api_key"]
    elif provider == "openrouter":
        api_key = config["openrouter_api_key"]
    
    if not api_key:
        # Fallback to static analysis if no LLM configured
        return {
            "project_description": "",
            "project_purpose": "",
            "architecture_understanding": "",
            "key_concepts": [],
            "domain_terms": [],
            "code_patterns": [],
            "business_logic": "",
            "llm_analysis": False,
            "error": "No LLM API key configured. Set LLM_PROVIDER and API key in .env file."
        }
    
    # Collect code samples for analysis
    code_samples = _collect_code_samples(repo_path, max_files)
    
    # Read README if available
    readme_content = ""
    readme_path = repo_path / "README.md"
    if readme_path.exists():
        try:
            readme_content = readme_path.read_text(encoding='utf-8', errors='ignore')[:2000]
        except:
            pass
    
    # Build analysis prompt
    prompt = _build_analysis_prompt(repo_path, code_samples, readme_content)
    
    # Call LLM
    result = call_llm(prompt, provider=provider)
    
    if result.get("error"):
        return {
            "project_description": "",
            "project_purpose": "",
            "architecture_understanding": "",
            "key_concepts": [],
            "domain_terms": [],
            "code_patterns": [],
            "business_logic": "",
            "llm_analysis": False,
            "error": result.get("reasoning", "LLM analysis failed")
        }
    
    # Parse LLM response
    analysis = _parse_llm_response(result["content"])
    analysis["llm_analysis"] = True
    
    return analysis


def _collect_code_samples(repo_path: Path, max_files: int) -> List[Dict[str, str]]:
    """Collect code samples from repository."""
    samples = []
    
    # Priority files to analyze
    priority_files = [
        "main.py", "app.py", "index.py", "__init__.py",
        "index.js", "app.js", "main.js", "server.js",
        "index.ts", "app.ts", "main.ts", "server.ts",
    ]
    
    # Collect priority files first
    for priority in priority_files:
        for ext in ["", ".py", ".js", ".ts"]:
            file_path = repo_path / (priority + ext)
            if file_path.exists() and file_path.is_file():
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    samples.append({
                        "path": str(file_path.relative_to(repo_path)),
                        "content": content[:1000]  # First 1000 chars
                    })
                    if len(samples) >= max_files:
                        return samples
                except:
                    continue
    
    # Collect other Python files
    python_files = list(repo_path.rglob("*.py"))
    for py_file in python_files[:max_files]:
        if py_file.name.startswith("__") or "test" in py_file.name.lower():
            continue
        if any(s["path"] == str(py_file.relative_to(repo_path)) for s in samples):
            continue
        try:
            content = py_file.read_text(encoding='utf-8', errors='ignore')
            samples.append({
                "path": str(py_file.relative_to(repo_path)),
                "content": content[:1000]
            })
            if len(samples) >= max_files:
                break
        except:
            continue
    
    # Collect JavaScript/TypeScript files
    js_files = list(repo_path.rglob("*.js")) + list(repo_path.rglob("*.ts"))
    for js_file in js_files[:max_files]:
        if "node_modules" in str(js_file) or "test" in js_file.name.lower():
            continue
        if any(s["path"] == str(js_file.relative_to(repo_path)) for s in samples):
            continue
        try:
            content = js_file.read_text(encoding='utf-8', errors='ignore')
            samples.append({
                "path": str(js_file.relative_to(repo_path)),
                "content": content[:1000]
            })
            if len(samples) >= max_files:
                break
        except:
            continue
    
    return samples


def _build_analysis_prompt(repo_path: Path, code_samples: List[Dict[str, str]], readme_content: str) -> str:
    """Build prompt for LLM analysis."""
    
    code_context = "\n\n".join([
        f"File: {s['path']}\n```\n{s['content']}\n```"
        for s in code_samples[:20]  # Limit to 20 files for prompt size
    ])
    
    prompt = f"""Analyze this codebase and provide a comprehensive semantic understanding.

Repository: {repo_path.name}

README Content:
{readme_content[:1000] if readme_content else "No README found"}

Code Samples:
{code_context}

Please analyze this codebase and provide the following information in JSON format:

{{
  "project_description": "A clear, concise description of what this project does (2-3 sentences)",
  "project_purpose": "The main purpose and goals of this project (1-2 sentences)",
  "architecture_understanding": "Description of the architecture, design patterns, and structure (3-4 sentences)",
  "key_concepts": ["concept1", "concept2", "concept3"],
  "domain_terms": ["term1", "term2", "term3"],
  "code_patterns": ["pattern1", "pattern2"],
  "business_logic": "Description of the core business logic and workflows (2-3 sentences)",
  "technologies_used": ["tech1", "tech2"],
  "framework_patterns": ["pattern1", "pattern2"]
}}

Focus on understanding:
- What the project actually does (not just file structure)
- The domain/business context
- Key architectural decisions
- Important patterns and conventions
- Core functionality and workflows

Respond ONLY with valid JSON, no markdown formatting."""
    
    return prompt


def _parse_llm_response(response: str) -> Dict[str, Any]:
    """Parse LLM response into structured data."""
    # Try to extract JSON from response
    json_match = re.search(r'\{.*\}', response, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except:
            pass
    
    # Fallback: try to parse as-is
    try:
        return json.loads(response)
    except:
        pass
    
    # Last resort: extract key information manually
    return {
        "project_description": _extract_field(response, "project_description", "description"),
        "project_purpose": _extract_field(response, "project_purpose", "purpose"),
        "architecture_understanding": _extract_field(response, "architecture", "architecture_understanding"),
        "key_concepts": _extract_list(response, "key_concepts", "concepts"),
        "domain_terms": _extract_list(response, "domain_terms", "terms"),
        "code_patterns": _extract_list(response, "code_patterns", "patterns"),
        "business_logic": _extract_field(response, "business_logic", "business"),
        "technologies_used": _extract_list(response, "technologies", "technologies_used"),
        "framework_patterns": _extract_list(response, "framework", "framework_patterns"),
    }


def _extract_field(text: str, *field_names: str) -> str:
    """Extract a field value from text."""
    for field_name in field_names:
        pattern = rf'"{field_name}"\s*:\s*"([^"]+)"'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return ""


def _extract_list(text: str, *field_names: str) -> List[str]:
    """Extract a list field from text."""
    for field_name in field_names:
        pattern = rf'"{field_name}"\s*:\s*\[(.*?)\]'
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            items_str = match.group(1)
            items = re.findall(r'"([^"]+)"', items_str)
            if items:
                return items
    return []
