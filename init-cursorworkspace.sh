#!/bin/bash
#
# init-cursorworkspace.sh
# Shell script wrapper for the /init-cursorworkspace command
#
# This script can be used standalone or called by the Cursor IDE slash command
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Default values
ANALYZE_CODEBASE=true
SKIP_VALIDATION=false
PROJECT_ROOT_ARG=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --no-analyze)
            ANALYZE_CODEBASE=false
            shift
            ;;
        --skip-validation)
            SKIP_VALIDATION=true
            shift
            ;;
        --project-root)
            PROJECT_ROOT_ARG="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --no-analyze          Skip codebase analysis if projectFile.md exists"
            echo "  --skip-validation     Skip validation step"
            echo "  --project-root PATH    Specify project root directory"
            echo "  --help, -h             Show this help message"
            echo ""
            echo "This script initializes a Cursor workspace by:"
            echo "  1. Analyzing codebase (or loading existing projectFile.md)"
            echo "  2. Creating/updating projectFile.md"
            echo "  3. Fetching templates from GitHub"
            echo "  4. Populating templates with project context"
            echo "  5. Generating .cursor workspace files"
            echo "  6. Validating generated workspace"
            echo "  7. Generating report"
            exit 0
            ;;
        *)
            echo -e "${RED}Error: Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Determine project root
if [[ -n "$PROJECT_ROOT_ARG" ]]; then
    PROJECT_ROOT="$(cd "$PROJECT_ROOT_ARG" && pwd)"
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 is not installed or not in PATH${NC}"
    exit 1
fi

# Check if dev/src directory exists
DEV_SRC_DIR="${PROJECT_ROOT}/dev/src"
if [[ ! -d "$DEV_SRC_DIR" ]]; then
    echo -e "${RED}Error: dev/src directory not found at ${DEV_SRC_DIR}${NC}"
    echo "Please run this script from the project root or specify --project-root"
    exit 1
fi

# Set Python path
export PYTHONPATH="${DEV_SRC_DIR}:${PYTHONPATH:-}"

# Run the initialization workflow
echo -e "${BLUE}🚀 Initializing Cursor workspace...${NC}"
echo ""

cd "$PROJECT_ROOT"

# Build Python command arguments
PYTHON_ARGS=()
if [[ "$ANALYZE_CODEBASE" == "false" ]]; then
    PYTHON_ARGS+=(--no-analyze)
fi
if [[ "$SKIP_VALIDATION" == "true" ]]; then
    PYTHON_ARGS+=(--skip-validation)
fi
if [[ -n "$PROJECT_ROOT_ARG" ]]; then
    PYTHON_ARGS+=(--project-root "$PROJECT_ROOT")
fi

# Execute Python script
python3 -c "
import sys
from pathlib import Path

# Add dev/src to path
sys.path.insert(0, str(Path('${DEV_SRC_DIR}')))

from commands.init_cursorworkspace import run_init_workflow

# Run the initialization workflow
results = run_init_workflow(
    project_root='${PROJECT_ROOT}',
    analyze_codebase=${ANALYZE_CODEBASE},
    skip_validation=${SKIP_VALIDATION}
)

if results['success']:
    print('✅ Workspace initialization completed successfully!')
    if results.get('report_path'):
        print(f\"📄 Report: {results['report_path']}\")
    if results.get('project_file_path'):
        print(f\"📝 Project file: {results['project_file_path']}\")
    sys.exit(0)
else:
    print('❌ Workspace initialization failed!')
    for error in results.get('errors', []):
        print(f\"  - {error}\")
    sys.exit(1)
"

EXIT_CODE=$?

if [[ $EXIT_CODE -eq 0 ]]; then
    echo ""
    echo -e "${GREEN}✅ Done!${NC}"
else
    echo ""
    echo -e "${RED}❌ Failed!${NC}"
fi

exit $EXIT_CODE
