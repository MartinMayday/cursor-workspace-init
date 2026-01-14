"""
Workspace validator module.

Executes test scenarios for hooks and rules, generating validation reports.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime


class ValidationResult:
    """Represents a single validation test result."""
    
    def __init__(self, scenario_name: str, status: str, message: str = '', 
                 details: Optional[Dict[str, Any]] = None):
        self.scenario_name = scenario_name
        self.status = status  # 'pass', 'fail', 'skip', 'error'
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'scenario_name': self.scenario_name,
            'status': self.status,
            'message': self.message,
            'details': self.details,
            'timestamp': self.timestamp,
        }


class WorkspaceValidator:
    """
    Validates generated workspace files and rules.
    """
    
    def __init__(self, workspace_root: Path):
        """
        Initialize validator.
        
        Args:
            workspace_root: Root directory of workspace to validate
        """
        self.workspace_root = Path(workspace_root).resolve()
        self.results: List[ValidationResult] = []
    
    def validate_all(self) -> List[ValidationResult]:
        """
        Run all validation scenarios.
        
        Returns:
            List of validation results
        """
        self.results = []
        
        # Validate file structure
        self._validate_file_structure()
        
        # Validate rules files
        self._validate_rules_files()
        
        # Validate commands files
        self._validate_commands_files()
        
        # Validate template replacements
        self._validate_template_replacements()
        
        # Validate hooks (if present)
        self._validate_hooks()
        
        return self.results
    
    def _validate_file_structure(self):
        """Validate that required files exist."""
        required_files = [
            '.cursorrules',
            '.cursor/rules/rules_manifest.json',
            '.cursor/commands/commands_manifest.json',
        ]
        
        for file_path in required_files:
            full_path = self.workspace_root / file_path
            if full_path.exists():
                self.results.append(ValidationResult(
                    f'file_exists_{file_path.replace("/", "_")}',
                    'pass',
                    f'File exists: {file_path}'
                ))
            else:
                self.results.append(ValidationResult(
                    f'file_exists_{file_path.replace("/", "_")}',
                    'fail',
                    f'File missing: {file_path}'
                ))
    
    def _validate_rules_files(self):
        """Validate rules files are valid."""
        rules_dir = self.workspace_root / '.cursor' / 'rules'
        
        if not rules_dir.exists():
            self.results.append(ValidationResult(
                'rules_directory_exists',
                'fail',
                '.cursor/rules directory does not exist'
            ))
            return
        
        # Check rules manifest
        manifest_path = rules_dir / 'rules_manifest.json'
        if manifest_path.exists():
            try:
                manifest = json.loads(manifest_path.read_text())
                if isinstance(manifest, dict) and 'rules' in manifest:
                    self.results.append(ValidationResult(
                        'rules_manifest_valid',
                        'pass',
                        f'Rules manifest contains {len(manifest.get("rules", []))} rules'
                    ))
                else:
                    self.results.append(ValidationResult(
                        'rules_manifest_valid',
                        'fail',
                        'Rules manifest missing "rules" key'
                    ))
            except json.JSONDecodeError as e:
                self.results.append(ValidationResult(
                    'rules_manifest_valid',
                    'error',
                    f'Invalid JSON in rules manifest: {e}'
                ))
        
        # Check individual rule files
        rule_files = list(rules_dir.glob('*.mdc'))
        for rule_file in rule_files:
            content = rule_file.read_text()
            # Check for placeholder remnants
            if '<PLACEHOLDER:' in content:
                self.results.append(ValidationResult(
                    f'rule_file_{rule_file.name}_no_placeholders',
                    'fail',
                    f'Unreplaced placeholders found in {rule_file.name}'
                ))
            else:
                self.results.append(ValidationResult(
                    f'rule_file_{rule_file.name}_no_placeholders',
                    'pass',
                    f'No unreplaced placeholders in {rule_file.name}'
                ))
    
    def _validate_commands_files(self):
        """Validate commands files are valid."""
        commands_dir = self.workspace_root / '.cursor' / 'commands'
        
        if not commands_dir.exists():
            self.results.append(ValidationResult(
                'commands_directory_exists',
                'skip',
                '.cursor/commands directory does not exist (optional)'
            ))
            return
        
        # Check commands manifest
        manifest_path = commands_dir / 'commands_manifest.json'
        if manifest_path.exists():
            try:
                manifest = json.loads(manifest_path.read_text())
                if isinstance(manifest, dict) and 'commands' in manifest:
                    self.results.append(ValidationResult(
                        'commands_manifest_valid',
                        'pass',
                        f'Commands manifest contains {len(manifest.get("commands", []))} commands'
                    ))
                else:
                    self.results.append(ValidationResult(
                        'commands_manifest_valid',
                        'fail',
                        'Commands manifest missing "commands" key'
                    ))
            except json.JSONDecodeError as e:
                self.results.append(ValidationResult(
                    'commands_manifest_valid',
                    'error',
                    f'Invalid JSON in commands manifest: {e}'
                ))
        
        # Check individual command files
        command_files = list(commands_dir.glob('*.mdc'))
        for command_file in command_files:
            content = command_file.read_text()
            # Check for placeholder remnants
            if '<PLACEHOLDER:' in content:
                self.results.append(ValidationResult(
                    f'command_file_{command_file.name}_no_placeholders',
                    'fail',
                    f'Unreplaced placeholders found in {command_file.name}'
                ))
            else:
                self.results.append(ValidationResult(
                    f'command_file_{command_file.name}_no_placeholders',
                    'pass',
                    f'No unreplaced placeholders in {command_file.name}'
                ))
    
    def _validate_template_replacements(self):
        """Validate that all template placeholders have been replaced."""
        # Check .cursorrules
        cursorrules_path = self.workspace_root / '.cursorrules'
        if cursorrules_path.exists():
            content = cursorrules_path.read_text()
            if '<PLACEHOLDER:' in content:
                self.results.append(ValidationResult(
                    'cursorrules_no_placeholders',
                    'fail',
                    'Unreplaced placeholders found in .cursorrules'
                ))
            else:
                self.results.append(ValidationResult(
                    'cursorrules_no_placeholders',
                    'pass',
                    'No unreplaced placeholders in .cursorrules'
                ))
    
    def _validate_hooks(self):
        """Validate hooks if they exist."""
        hooks_dir = self.workspace_root / '.cursor' / 'hooks'
        
        if not hooks_dir.exists():
            self.results.append(ValidationResult(
                'hooks_directory_exists',
                'skip',
                '.cursor/hooks directory does not exist (optional)'
            ))
            return
        
        hook_files = list(hooks_dir.glob('*'))
        if hook_files:
            self.results.append(ValidationResult(
                'hooks_present',
                'pass',
                f'Found {len(hook_files)} hook file(s)'
            ))
        else:
            self.results.append(ValidationResult(
                'hooks_present',
                'skip',
                'Hooks directory exists but is empty'
            ))
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get validation summary.
        
        Returns:
            Summary dictionary with counts and status
        """
        total = len(self.results)
        passed = sum(1 for r in self.results if r.status == 'pass')
        failed = sum(1 for r in self.results if r.status == 'fail')
        errors = sum(1 for r in self.results if r.status == 'error')
        skipped = sum(1 for r in self.results if r.status == 'skip')
        
        return {
            'total': total,
            'passed': passed,
            'failed': failed,
            'errors': errors,
            'skipped': skipped,
            'success_rate': (passed / total * 100) if total > 0 else 0,
            'all_passed': failed == 0 and errors == 0,
        }
