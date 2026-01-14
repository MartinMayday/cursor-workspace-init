"""
Report generator module.

Compiles validation results and generates markdown reports in artifacts directory.
"""

import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from validators.workspace_validator import ValidationResult


def generate_report(validation_results: List[ValidationResult],
                   context: Dict[str, Any],
                   project_root: Optional[str] = None,
                   output_dir: Optional[str] = None) -> Path:
    """
    Generate markdown report from validation results.
    
    Args:
        validation_results: List of validation results
        context: Project context dictionary
        project_root: Project root directory
        output_dir: Output directory for report (default: artifacts/reports/)
        
    Returns:
        Path to generated report file
    """
    if output_dir is None:
        artifacts_dir = os.getenv('CURSOR_ARTIFACTS_DIR', 'artifacts')
        output_dir = os.path.join(artifacts_dir, 'reports')
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Generate report filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = output_path / f'init-cursorworkspace-report-{timestamp}.md'
    
    # Calculate summary statistics
    total = len(validation_results)
    passed = sum(1 for r in validation_results if r.status == 'pass')
    failed = sum(1 for r in validation_results if r.status == 'fail')
    errors = sum(1 for r in validation_results if r.status == 'error')
    skipped = sum(1 for r in validation_results if r.status == 'skip')
    success_rate = (passed / total * 100) if total > 0 else 0
    all_passed = failed == 0 and errors == 0
    
    # Generate report content
    report_content = f"""# Cursor Workspace Initialization Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

| Metric | Value |
|--------|-------|
| Total Tests | {total} |
| Passed | {passed} |
| Failed | {failed} |
| Errors | {errors} |
| Skipped | {skipped} |
| Success Rate | {success_rate:.1f}% |
| **Overall Status** | **{'✅ PASSED' if all_passed else '❌ FAILED'}** |

## Project Context

- **Project Name**: {context.get('project_name', 'Unknown')}
- **Project Type**: {context.get('project_type', 'Unknown')}
- **Primary Language**: {context.get('primary_language', 'Unknown')}
- **Frameworks**: {', '.join(context.get('frameworks', [])) if context.get('frameworks') else 'None'}
- **Architecture**: {context.get('architecture', 'Unknown')}
- **Deployment Type**: {context.get('deployment_type', 'Unknown')}

## Validation Results

"""
    
    # Group results by category
    categories = {
        'File Structure': [],
        'Rules Files': [],
        'Commands Files': [],
        'Template Replacements': [],
        'Hooks': [],
        'Other': [],
    }
    
    for result in validation_results:
        scenario = result.scenario_name.lower()
        if 'file_exists' in scenario:
            categories['File Structure'].append(result)
        elif 'rule' in scenario:
            categories['Rules Files'].append(result)
        elif 'command' in scenario:
            categories['Commands Files'].append(result)
        elif 'placeholder' in scenario:
            categories['Template Replacements'].append(result)
        elif 'hook' in scenario:
            categories['Hooks'].append(result)
        else:
            categories['Other'].append(result)
    
    # Write results by category
    for category, results in categories.items():
        if not results:
            continue
        
        report_content += f"\n### {category}\n\n"
        report_content += "| Scenario | Status | Message |\n"
        report_content += "|----------|--------|----------|\n"
        
        for result in results:
            status_icon = {
                'pass': '✅',
                'fail': '❌',
                'error': '⚠️',
                'skip': '⏭️',
            }.get(result.status, '❓')
            
            report_content += f"| {result.scenario_name} | {status_icon} {result.status.upper()} | {result.message} |\n"
        
        report_content += "\n"
    
    # Add detailed results section
    report_content += "\n## Detailed Results\n\n"
    
    for result in validation_results:
        report_content += f"### {result.scenario_name}\n\n"
        report_content += f"- **Status**: {result.status.upper()}\n"
        report_content += f"- **Message**: {result.message}\n"
        report_content += f"- **Timestamp**: {result.timestamp}\n"
        
        if result.details:
            report_content += f"- **Details**:\n"
            for key, value in result.details.items():
                report_content += f"  - {key}: {value}\n"
        
        report_content += "\n"
    
    # Add recommendations section
    report_content += "\n## Recommendations\n\n"
    
    if all_passed:
        report_content += "✅ All validation tests passed! Your workspace is ready to use.\n\n"
    else:
        failed_results = [r for r in validation_results if r.status in ['fail', 'error']]
        report_content += "⚠️ Some validation tests failed. Please review the following:\n\n"
        
        for result in failed_results:
            report_content += f"- **{result.scenario_name}**: {result.message}\n"
            if result.details:
                for key, value in result.details.items():
                    report_content += f"  - {key}: {value}\n"
    
    report_content += f"\n---\n*Report generated by `/init-cursorworkspace` command*\n"
    
    # Write report file
    report_file.write_text(report_content, encoding='utf-8')
    
    return report_file


def generate_summary_report(validation_summary: Dict[str, Any],
                          project_root: Optional[str] = None,
                          output_dir: Optional[str] = None) -> Path:
    """
    Generate a brief summary report.
    
    Args:
        validation_summary: Summary dictionary from validator
        project_root: Project root directory
        output_dir: Output directory for report
        
    Returns:
        Path to generated report file
    """
    if output_dir is None:
        artifacts_dir = os.getenv('CURSOR_ARTIFACTS_DIR', 'artifacts')
        output_dir = os.path.join(artifacts_dir, 'reports')
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = output_path / f'init-cursorworkspace-summary-{timestamp}.md'
    
    report_content = f"""# Cursor Workspace Initialization Summary

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Validation Summary

- **Total Tests**: {validation_summary.get('total', 0)}
- **Passed**: {validation_summary.get('passed', 0)}
- **Failed**: {validation_summary.get('failed', 0)}
- **Errors**: {validation_summary.get('errors', 0)}
- **Skipped**: {validation_summary.get('skipped', 0)}
- **Success Rate**: {validation_summary.get('success_rate', 0):.1f}%
- **Status**: {'✅ PASSED' if validation_summary.get('all_passed', False) else '❌ FAILED'}

---
*Summary report generated by `/init-cursorworkspace` command*
"""
    
    report_file.write_text(report_content, encoding='utf-8')
    
    return report_file
