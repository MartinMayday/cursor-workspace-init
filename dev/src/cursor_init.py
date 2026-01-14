#!/usr/bin/env python3
"""
Cursor Init: Main entry point for workspace initialization.

This script provides three core capabilities:
1. Analyze existing repositories and auto-generate cursor workspace files
2. Conduct interactive AI-powered interview for new projects
3. Generate best practices scaffolding for new projects
"""

import argparse
import os
import sys
from pathlib import Path


def detect_project_type(repo_path: str = ".") -> str:
    """
    Detect if we're in an existing repository or new project.
    
    Args:
        repo_path: Path to the repository/project directory
        
    Returns:
        'existing' if repository detected, 'new' otherwise
    """
    repo_path = Path(repo_path).resolve()
    
    # Check for common repository indicators
    indicators = [
        '.git',
        'package.json',
        'pyproject.toml',
        'requirements.txt',
        'Cargo.toml',
        'go.mod',
        'pom.xml',
        'build.gradle',
        'tsconfig.json',
        'Makefile',
        'CMakeLists.txt',
    ]
    
    for indicator in indicators:
        if (repo_path / indicator).exists():
            return 'existing'
    
    # Check if directory has any source files
    source_patterns = ['*.py', '*.js', '*.ts', '*.java', '*.go', '*.rs', '*.cpp', '*.c']
    for pattern in source_patterns:
        if list(repo_path.glob(f'**/{pattern}')):
            return 'existing'
    
    return 'new'


def route_to_script(project_type: str, args: argparse.Namespace):
    """
    Route to appropriate script based on project type and arguments.
    
    Args:
        project_type: 'existing' or 'new'
        args: Parsed command line arguments
    """
    if args.scaffold:
        # Force scaffolding generation
        from scripts.generate_scaffolding import generate_scaffolding
        generate_scaffolding(args.output or ".")
        return
    
    if args.new or project_type == 'new':
        # New project interview flow
        from scripts.interactive_interview import run_interview
        context = run_interview()
        if context:
            from generators.workspace_generator import generate_workspace_files
            output_path = args.output or "."
            generate_workspace_files(context, output_path)
        return
    
    if project_type == 'existing':
        # Existing repository analysis
        try:
            from scripts.analyze_existing_repo import analyze_repository, generate_workspace_files
            repo_path = args.path or "."
            context = analyze_repository(repo_path)
            if context:
                output_path = args.output or repo_path
                # Check if existing workspace should be enhanced
                enhance_mode = not args.overwrite if hasattr(args, 'overwrite') else True
                generate_workspace_files(context, output_path, enhance_mode=enhance_mode)
        except Exception as e:
            import traceback
            print(f"Error during analysis: {e}")
            traceback.print_exc()
            raise
        return


def main():
    """Main entry point for cursor_init command."""
    parser = argparse.ArgumentParser(
        description='Initialize Cursor workspace files for existing repositories or new projects',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  cursor_init                    # Auto-detect and analyze existing repo
  cursor_init --new              # Start new project interview
  cursor_init --scaffold         # Generate new project scaffolding
  cursor_init --path /path/to/repo  # Analyze specific repository
  cursor_init --output /path/to/output  # Specify output directory
        """
    )
    
    parser.add_argument(
        '--new',
        action='store_true',
        help='Force new project flow (interactive interview)'
    )
    
    parser.add_argument(
        '--scaffold',
        action='store_true',
        help='Generate new project scaffolding'
    )
    
    parser.add_argument(
        '--path',
        type=str,
        help='Path to repository or project directory (default: current directory)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Output directory for generated files (default: same as --path or current directory)'
    )
    
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='Overwrite existing workspace files instead of enhancing them'
    )
    
    args = parser.parse_args()
    
    # Determine project type
    repo_path = args.path or "."
    project_type = detect_project_type(repo_path)
    
    print(f"Detected project type: {project_type}")
    
    # Route to appropriate script
    try:
        route_to_script(project_type, args)
    except ImportError as e:
        print(f"Error: Required module not found: {e}", file=sys.stderr)
        print("Please ensure all dependencies are installed and modules are available.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

