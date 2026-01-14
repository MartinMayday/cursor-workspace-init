"""
Command orchestrator for `/init-cursorworkspace` slash command.

Orchestrates the full workflow: analysis → projectFile.md → template fetch → population → validation → reporting
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional

from utils.logger import get_logger
from generators.project_file_manager import (
    create_project_file, 
    update_project_file, 
    project_file_exists,
    validate_project_file
)
from generators.context_extractor import extract_context_from_project_file, validate_context
from generators.template_fetcher import fetch_templates, get_template_content
from generators.template_engine import replace_placeholders, validate_replacements
from validators.workspace_validator import WorkspaceValidator
from generators.report_generator import generate_report


def run_init_workflow(project_root: Optional[str] = None, 
                     analyze_codebase: bool = True,
                     skip_validation: bool = False) -> Dict[str, Any]:
    """
    Run the complete initialization workflow.
    
    Args:
        project_root: Project root directory (default: current directory)
        analyze_codebase: Whether to analyze codebase if projectFile.md doesn't exist
        skip_validation: Skip validation step
        
    Returns:
        Dictionary with workflow results and paths
    """
    if project_root is None:
        project_root = Path.cwd()
    else:
        project_root = Path(project_root).resolve()
    
    logger = get_logger()
    results = {
        'project_root': str(project_root),
        'project_file_path': None,
        'templates_fetched': False,
        'files_generated': [],
        'validation_results': None,
        'report_path': None,
        'success': False,
        'errors': [],
    }
    
    try:
        # Step 1: Check/create projectFile.md
        logger.start_operation('project_file_management')
        
        if project_file_exists(project_root) and analyze_codebase:
            # projectFile.md exists but user wants to re-analyze
            logger.info('project_file_management', 'projectFile.md exists but re-analyzing codebase as requested')
            from scripts.analyze_existing_repo import analyze_repository
            analysis_context = analyze_repository(str(project_root))
            project_file_path = create_project_file(analysis_context, project_root)
            context = analysis_context
            logger.info('project_file_management', f'Updated projectFile.md from codebase analysis: {project_file_path}')
        elif project_file_exists(project_root):
            # projectFile.md exists - skip analysis and use it directly
            logger.info('project_file_management', 'projectFile.md already exists - skipping analysis')
            context = extract_context_from_project_file(project_root)
            project_file_path = Path(project_root) / 'projectFile.md'
            logger.info('project_file_management', f'Loaded context from existing projectFile.md: {project_file_path}')
        else:
            # projectFile.md doesn't exist - analyze codebase and create it
            if not analyze_codebase:
                raise ValueError("projectFile.md does not exist and analyze_codebase is False")
            
            logger.info('project_file_management', 'projectFile.md not found - analyzing codebase to create it')
            from scripts.analyze_existing_repo import analyze_repository
            analysis_context = analyze_repository(str(project_root))
            project_file_path = create_project_file(analysis_context, project_root)
            context = analysis_context
            logger.info('project_file_management', f'Created projectFile.md from codebase analysis: {project_file_path}')
        
        # Validate project file
        is_valid, errors = validate_project_file(project_root)
        if not is_valid:
            logger.warning('project_file_validation', f'Project file validation issues: {errors}')
            results['errors'].extend(errors)
        
        results['project_file_path'] = str(project_file_path)
        logger.end_operation('project_file_management', 'success', {
            'project_file_path': str(project_file_path)
        })
        
        # Step 2: Fetch templates from GitHub
        logger.start_operation('template_fetching')
        try:
            templates = fetch_templates()
            logger.info('template_fetching', f'Fetched {len(templates)} templates')
            results['templates_fetched'] = True
            logger.end_operation('template_fetching', 'success', {
                'template_count': len(templates)
            })
        except Exception as e:
            logger.error('template_fetching', 'Failed to fetch templates', e)
            results['errors'].append(f'Template fetching failed: {str(e)}')
            logger.end_operation('template_fetching', 'error', {'error': str(e)})
            raise
        
        # Step 3: Populate templates with context
        logger.start_operation('template_population')
        
        # Validate context
        is_valid, missing = validate_context(context)
        if not is_valid:
            logger.warning('context_validation', f'Missing context variables: {missing}')
        
        # Generate workspace files using existing workspace generator
        from generators.workspace_generator import generate_workspace_files
        generate_workspace_files(context, str(project_root), enhance_mode=True)
        
        logger.end_operation('template_population', 'success')
        
        # Step 4: Validate generated workspace
        if not skip_validation:
            logger.start_operation('workspace_validation')
            try:
                validator = WorkspaceValidator(project_root)
                validation_results = validator.validate_all()
                summary = validator.get_summary()
                
                results['validation_results'] = {
                    'summary': summary,
                    'results': [r.to_dict() for r in validation_results]
                }
                
                logger.end_operation('workspace_validation', 
                                   'success' if summary['all_passed'] else 'warning',
                                   summary)
            except Exception as e:
                logger.error('workspace_validation', 'Validation failed', e)
                results['errors'].append(f'Validation failed: {str(e)}')
                logger.end_operation('workspace_validation', 'error', {'error': str(e)})
        
        # Step 5: Generate report
        logger.start_operation('report_generation')
        try:
            if not skip_validation and results['validation_results']:
                from validators.workspace_validator import ValidationResult
                # Reconstruct ValidationResult objects from dictionaries
                validation_results = []
                for r_dict in results['validation_results']['results']:
                    result = ValidationResult(
                        scenario_name=r_dict['scenario_name'],
                        status=r_dict['status'],
                        message=r_dict.get('message', ''),
                        details=r_dict.get('details', {})
                    )
                    validation_results.append(result)
                report_path = generate_report(validation_results, context, project_root)
            else:
                # Generate summary report even if validation was skipped
                from generators.report_generator import generate_summary_report
                summary = {'total': 0, 'passed': 0, 'failed': 0, 'errors': 0, 
                          'skipped': 0, 'success_rate': 100, 'all_passed': True}
                report_path = generate_summary_report(summary, project_root)
            
            results['report_path'] = str(report_path)
            logger.end_operation('report_generation', 'success', {
                'report_path': str(report_path)
            })
        except Exception as e:
            logger.error('report_generation', 'Report generation failed', e)
            results['errors'].append(f'Report generation failed: {str(e)}')
            logger.end_operation('report_generation', 'error', {'error': str(e)})
        
        results['success'] = len(results['errors']) == 0
        
    except Exception as e:
        logger.critical('init_workflow', 'Workflow failed', e)
        results['errors'].append(f'Workflow failed: {str(e)}')
        results['success'] = False
    
    return results


def main():
    """Main entry point for command execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Initialize Cursor workspace')
    parser.add_argument('--project-root', type=str, help='Project root directory')
    parser.add_argument('--no-analyze', action='store_true', 
                       help='Skip codebase analysis if projectFile.md exists')
    parser.add_argument('--skip-validation', action='store_true',
                       help='Skip validation step')
    
    args = parser.parse_args()
    
    results = run_init_workflow(
        project_root=args.project_root,
        analyze_codebase=not args.no_analyze,
        skip_validation=args.skip_validation
    )
    
    if results['success']:
        print("✅ Workspace initialization completed successfully!")
        if results['report_path']:
            print(f"📄 Report: {results['report_path']}")
    else:
        print("❌ Workspace initialization failed!")
        for error in results['errors']:
            print(f"  - {error}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
