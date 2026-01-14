"""
Validation runner for manifest format testing.

Executes tests by presenting manifests to AI agents and recording results.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import json
import time
import re
from datetime import datetime
try:
    from .config import load_config, get_api_key, get_model, validate_config
except ImportError:
    from config import load_config, get_api_key, get_model, validate_config


class ValidationRunner:
    """Runs validation tests against AI agents."""
    
    def __init__(self, scenarios_path: Path, baseline_dir: Path, enhanced_dir: Path, results_dir: Path):
        """
        Initialize validation runner.
        
        Args:
            scenarios_path: Path to test_scenarios.json
            baseline_dir: Directory containing baseline manifests
            enhanced_dir: Directory containing enhanced manifests
            results_dir: Directory to save results
        """
        self.scenarios_path = scenarios_path
        self.baseline_dir = baseline_dir
        self.enhanced_dir = enhanced_dir
        self.results_dir = results_dir
        self.results_dir.mkdir(exist_ok=True)
        
        # Load configuration
        self.config = load_config()
        self.provider = self.config["default_provider"]
        
        # Validate configuration
        is_valid, missing = validate_config()
        if not is_valid:
            print(f"Warning: Missing configuration: {', '.join(missing)}")
            print("Please set environment variables or create a .env file")
            print("See env.example for required variables")
        
    def load_scenarios(self) -> List[Dict[str, Any]]:
        """Load test scenarios from JSON file."""
        with open(self.scenarios_path, 'r') as f:
            data = json.load(f)
            return data.get("scenarios", [])
    
    def load_manifest(self, scenario_id: str, format_type: str) -> Dict[str, Any]:
        """
        Load manifest for a scenario.
        
        Args:
            scenario_id: Scenario identifier
            format_type: 'baseline' or 'enhanced'
            
        Returns:
            Manifest dictionary
        """
        if format_type == "baseline":
            manifest_path = self.baseline_dir / f"{scenario_id}.json"
        else:
            manifest_path = self.enhanced_dir / f"{scenario_id}.json"
        
        with open(manifest_path, 'r') as f:
            return json.load(f)
    
    def create_prompt(self, manifest: Dict[str, Any], context: Dict[str, Any], format_type: str) -> str:
        """
        Create prompt for AI agent.
        
        Args:
            manifest: Manifest dictionary
            context: Context variables
            format_type: 'baseline' or 'enhanced'
            
        Returns:
            Prompt string
        """
        manifest_json = json.dumps(manifest, indent=2)
        context_json = json.dumps(context, indent=2)
        
        prompt = f"""You are an AI agent that needs to determine which rule files should be loaded based on a manifest file and project context.

MANIFEST FORMAT: {format_type.upper()}
MANIFEST:
{manifest_json}

PROJECT CONTEXT:
{context_json}

TASK: Determine which files from the manifest should be loaded and explain your reasoning.

Please respond in the following JSON format:
{{
  "selected_files": ["file1.mdc", "file2.mdc", ...],
  "reasoning": "Explanation of why these files were selected",
  "confidence": 95,
  "clarification_needed": false
}}

Confidence should be a number between 0-100 indicating how certain you are about your selection.
If you need clarification, set clarification_needed to true and explain what information is missing.
"""
        return prompt
    
    def call_ai_agent(self, prompt: str, model: Optional[str] = None) -> Dict[str, Any]:
        """
        Call AI agent via API.
        
        Args:
            prompt: Prompt to send to AI
            model: AI model to use (defaults to configured model)
            
        Returns:
            Response dictionary with selected_files, reasoning, confidence, clarification_needed
        """
        if model is None:
            model = get_model(self.provider)
        
        api_key = get_api_key(self.provider)
        if not api_key:
            return {
                "selected_files": [],
                "reasoning": f"Error: No API key configured for provider '{self.provider}'",
                "confidence": 0,
                "clarification_needed": True,
                "raw_response": "API key missing"
            }
        
        # Call appropriate provider
        if self.provider.lower() == "openai":
            return self._call_openai(prompt, model, api_key)
        elif self.provider.lower() == "anthropic":
            return self._call_anthropic(prompt, model, api_key)
        elif self.provider.lower() == "openrouter":
            return self._call_openrouter(prompt, model, api_key)
        else:
            return {
                "selected_files": [],
                "reasoning": f"Error: Unknown provider '{self.provider}'",
                "confidence": 0,
                "clarification_needed": True,
                "raw_response": "Unknown provider"
            }
    
    def _call_openai(self, prompt: str, model: str, api_key: str) -> Dict[str, Any]:
        """
        Call OpenAI API.
        
        Args:
            prompt: Prompt to send
            model: Model name
            api_key: API key
            
        Returns:
            Response dictionary
        """
        try:
            import openai
            
            client = openai.OpenAI(
                api_key=api_key,
                base_url=self.config.get("openai_base_url") or "https://api.openai.com/v1"
            )
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI agent that analyzes manifest files and determines which rule files should be loaded. Always respond with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=self.config["temperature"],
                timeout=self.config["api_timeout"]
            )
            
            raw_response = response.choices[0].message.content
            return {
                "selected_files": [],
                "reasoning": "",
                "confidence": 0,
                "clarification_needed": False,
                "raw_response": raw_response
            }
            
        except ImportError:
            return {
                "selected_files": [],
                "reasoning": "Error: openai package not installed. Install with: pip install openai",
                "confidence": 0,
                "clarification_needed": True,
                "raw_response": "openai package missing"
            }
        except Exception as e:
            return {
                "selected_files": [],
                "reasoning": f"Error calling OpenAI API: {str(e)}",
                "confidence": 0,
                "clarification_needed": True,
                "raw_response": f"API error: {str(e)}"
            }
    
    def _call_anthropic(self, prompt: str, model: str, api_key: str) -> Dict[str, Any]:
        """
        Call Anthropic API.
        
        Args:
            prompt: Prompt to send
            model: Model name
            api_key: API key
            
        Returns:
            Response dictionary
        """
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=api_key)
            
            response = client.messages.create(
                model=model,
                max_tokens=4096,
                temperature=self.config["temperature"],
                system="You are an AI agent that analyzes manifest files and determines which rule files should be loaded. Always respond with valid JSON.",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            raw_response = response.content[0].text
            return {
                "selected_files": [],
                "reasoning": "",
                "confidence": 0,
                "clarification_needed": False,
                "raw_response": raw_response
            }
            
        except ImportError:
            return {
                "selected_files": [],
                "reasoning": "Error: anthropic package not installed. Install with: pip install anthropic",
                "confidence": 0,
                "clarification_needed": True,
                "raw_response": "anthropic package missing"
            }
        except Exception as e:
            return {
                "selected_files": [],
                "reasoning": f"Error calling Anthropic API: {str(e)}",
                "confidence": 0,
                "clarification_needed": True,
                "raw_response": f"API error: {str(e)}"
            }
    
    def _call_openrouter(self, prompt: str, model: str, api_key: str) -> Dict[str, Any]:
        """
        Call OpenRouter API (OpenAI-compatible).
        
        Args:
            prompt: Prompt to send
            model: Model name
            api_key: API key
            
        Returns:
            Response dictionary
        """
        try:
            import openai
            
            base_url = self.config.get("openrouter_base_url", "https://openrouter.ai/api/v1")
            
            client = openai.OpenAI(
                api_key=api_key,
                base_url=base_url,
                default_headers={
                    "HTTP-Referer": "https://github.com/cursor-workspace-init",  # Optional: for OpenRouter analytics
                    "X-Title": "Cursor Workspace Init Validation"  # Optional: for OpenRouter analytics
                }
            )
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI agent that analyzes manifest files and determines which rule files should be loaded. Always respond with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
                temperature=self.config["temperature"],
                timeout=self.config["api_timeout"]
            )
            
            raw_response = response.choices[0].message.content
            return {
                "selected_files": [],
                "reasoning": "",
                "confidence": 0,
                "clarification_needed": False,
                "raw_response": raw_response
            }
            
        except ImportError:
            return {
                "selected_files": [],
                "reasoning": "Error: openai package not installed. Install with: pip install openai",
                "confidence": 0,
                "clarification_needed": True,
                "raw_response": "openai package missing"
            }
        except Exception as e:
            return {
                "selected_files": [],
                "reasoning": f"Error calling OpenRouter API: {str(e)}",
                "confidence": 0,
                "clarification_needed": True,
                "raw_response": f"API error: {str(e)}"
            }
    
    def extract_confidence(self, response_text: str) -> Optional[int]:
        """
        Extract confidence level from response text.
        
        Args:
            response_text: Response text from AI
            
        Returns:
            Confidence level (0-100) or None
        """
        # Try to find confidence in JSON
        json_match = re.search(r'"confidence"\s*:\s*(\d+)', response_text)
        if json_match:
            return int(json_match.group(1))
        
        # Try to find confidence in text
        text_match = re.search(r'confidence[:\s]+(\d+)', response_text, re.IGNORECASE)
        if text_match:
            return int(text_match.group(1))
        
        return None
    
    def parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse AI response to extract structured data.
        
        Args:
            response_text: Raw response from AI
            
        Returns:
            Parsed response dictionary
        """
        # Try to extract JSON from response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group(0))
                return {
                    "selected_files": parsed.get("selected_files", []),
                    "reasoning": parsed.get("reasoning", ""),
                    "confidence": parsed.get("confidence", 0),
                    "clarification_needed": parsed.get("clarification_needed", False),
                    "raw_response": response_text
                }
            except json.JSONDecodeError:
                pass
        
        # Fallback: extract files from text
        files = re.findall(r'level\d+[-\w]*\.mdc', response_text)
        
        return {
            "selected_files": list(set(files)),
            "reasoning": response_text[:500],  # First 500 chars
            "confidence": self.extract_confidence(response_text) or 0,
            "clarification_needed": "clarification" in response_text.lower() or "?" in response_text,
            "raw_response": response_text
        }
    
    def run_single_test(self, scenario: Dict[str, Any], format_type: str, run_number: int) -> Dict[str, Any]:
        """
        Run a single test.
        
        Args:
            scenario: Scenario dictionary
            format_type: 'baseline' or 'enhanced'
            run_number: Test run number (1-10)
            
        Returns:
            Test result dictionary
        """
        scenario_id = scenario["scenario_id"]
        context = scenario["context"]
        expected_files = scenario["expected_files"]
        
        # Load manifest
        manifest = self.load_manifest(scenario_id, format_type)
        
        # Create prompt
        prompt = self.create_prompt(manifest, context, format_type)
        
        # Call AI agent
        start_time = time.time()
        ai_response = self.call_ai_agent(prompt)
        end_time = time.time()
        
        # Parse response
        parsed_response = self.parse_ai_response(ai_response.get("raw_response", ""))
        
        # Calculate accuracy
        selected_files = set(parsed_response.get("selected_files", []))
        expected_files_set = set(expected_files)
        
        correct_files = selected_files.intersection(expected_files_set)
        incorrect_files = selected_files - expected_files_set
        missing_files = expected_files_set - selected_files
        
        accuracy = len(correct_files) / len(expected_files_set) * 100 if expected_files_set else 0
        
        # Build result
        result = {
            "scenario_id": scenario_id,
            "format_type": format_type,
            "run_number": run_number,
            "timestamp": datetime.now().isoformat(),
            "selected_files": list(selected_files),
            "expected_files": expected_files,
            "correct_files": list(correct_files),
            "incorrect_files": list(incorrect_files),
            "missing_files": list(missing_files),
            "accuracy": accuracy,
            "confidence": parsed_response.get("confidence", 0),
            "reasoning": parsed_response.get("reasoning", ""),
            "clarification_needed": parsed_response.get("clarification_needed", False),
            "decision_time": end_time - start_time,
            "raw_response": parsed_response.get("raw_response", "")
        }
        
        return result
    
    def run_all_tests(self, num_runs: int = 10, format_type: Optional[str] = None):
        """
        Run all tests for all scenarios.
        
        Args:
            num_runs: Number of runs per scenario (default 10)
            format_type: 'baseline', 'enhanced', or None for both
        """
        scenarios = self.load_scenarios()
        
        results = {
            "baseline": [],
            "enhanced": []
        }
        
        format_types = ["baseline", "enhanced"] if format_type is None else [format_type]
        
        for fmt_type in format_types:
            print(f"\nRunning {fmt_type} tests...")
            for scenario in scenarios:
                scenario_id = scenario["scenario_id"]
                print(f"  Testing {scenario_id}...", end=" ", flush=True)
                
                for run_num in range(1, num_runs + 1):
                    result = self.run_single_test(scenario, fmt_type, run_num)
                    results[fmt_type].append(result)
                    
                    # Show quick stats for first run of each scenario
                    if run_num == 1:
                        acc = result.get('accuracy', 0)
                        conf = result.get('confidence', 0)
                        files_count = len(result.get('selected_files', []))
                        print(f"[acc:{acc:.0f}% conf:{conf:.0f}% files:{files_count}]", end=" ", flush=True)
                    
                    # Save incrementally after each scenario completes (so progress isn't lost)
                    if run_num == num_runs:
                        results_path = self.results_dir / f"{fmt_type}_results.json"
                        with open(results_path, 'w') as f:
                            json.dump(results[fmt_type], f, indent=2)
                
                print("✓")
            
            # Final save after each format completes
            results_path = self.results_dir / f"{fmt_type}_results.json"
            with open(results_path, 'w') as f:
                json.dump(results[fmt_type], f, indent=2)
            print(f"Saved {fmt_type} results to {results_path} ({len(results[fmt_type])} tests)")
            
            # Show summary stats
            if results[fmt_type]:
                avg_acc = sum(r.get('accuracy', 0) for r in results[fmt_type]) / len(results[fmt_type])
                avg_conf = sum(r.get('confidence', 0) for r in results[fmt_type]) / len(results[fmt_type])
                placeholder_count = sum(1 for r in results[fmt_type] if "Placeholder" in str(r.get('raw_response', '')))
                print(f"  Summary: {avg_acc:.1f}% avg accuracy, {avg_conf:.1f}% avg confidence")
                if placeholder_count > 0:
                    print(f"  ⚠️  WARNING: {placeholder_count} placeholder responses detected!")
                else:
                    print(f"  ✅ All responses appear to be real API calls")
        
        return results


if __name__ == "__main__":
    # Get paths
    validation_dir = Path(__file__).parent
    scenarios_path = validation_dir / "test_scenarios.json"
    baseline_dir = validation_dir / "baseline_manifests"
    enhanced_dir = validation_dir / "enhanced_manifests"
    results_dir = validation_dir / "results"
    
    # Create runner
    runner = ValidationRunner(scenarios_path, baseline_dir, enhanced_dir, results_dir)
    
    # Validate configuration before running
    is_valid, missing = validate_config()
    if not is_valid:
        print("\n❌ Configuration Error:")
        print(f"Missing required configuration: {', '.join(missing)}")
        print("\nTo configure:")
        print("1. Copy env.example to .env")
        print("2. Set your API keys in .env file")
        print("3. Or set environment variables directly")
        print("\nExample:")
        print("  export OPENAI_API_KEY='sk-your-key-here'")
        print("  export LLM_PROVIDER='openai'")
        print("  export LLM_MODEL='gpt-4'")
    else:
        print("\n✅ Configuration valid")
        print(f"Provider: {runner.provider}")
        print(f"Model: {get_model(runner.provider)}")
        print("\nTo run tests, use one of these methods:")
        print("\n1. Interactive script (recommended):")
        print("   python3 tests/validation/run_validation.py")
        print("\n2. Direct Python:")
        print("   python3 -c \"from tests.validation.validation_runner import ValidationRunner; from pathlib import Path;")
        print("   vd = Path('tests/validation'); runner = ValidationRunner(vd/'test_scenarios.json', vd/'baseline_manifests', vd/'enhanced_manifests', vd/'results'); runner.run_all_tests(num_runs=1)\"")
        print("\n3. Uncomment the line below in this file to run automatically")
        # Uncomment to run automatically:
        # runner.run_all_tests(num_runs=1)  # Start with 1 run for testing

