#!/bin/bash
#
# init-cursorworkspace.sh
# Shell script wrapper for the /init-cursorworkspace command
#
# Usage: Clone the cursor-workspace-init repo, then run this script from your project directory
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Find the tool's directory (where this script is located)
# This script should be in the root of the cloned cursor-workspace-init repository
SCRIPT_PATH="${BASH_SOURCE[0]}"
if [[ -L "$SCRIPT_PATH" ]]; then
    # Resolve symlinks
    SCRIPT_PATH="$(readlink -f "$SCRIPT_PATH")"
fi
TOOL_ROOT="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"

# Current working directory (where user runs the command - this is the project to initialize)
WORKSPACE_ROOT="$(pwd)"

# Default values
ANALYZE_CODEBASE=true
SKIP_VALIDATION=false

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
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --no-analyze          Skip codebase analysis if projectFile.md exists"
            echo "  --skip-validation     Skip validation step"
            echo "  --help, -h             Show this help message"
            echo ""
            echo "This script initializes a Cursor workspace in the current directory by:"
            echo "  1. Analyzing codebase (or loading existing projectFile.md)"
            echo "  2. Creating/updating projectFile.md"
            echo "  3. Fetching templates from GitHub"
            echo "  4. Populating templates with project context"
            echo "  5. Generating .cursor workspace files"
            echo "  6. Validating generated workspace"
            echo "  7. Generating report"
            echo ""
            echo "The tool source code should be cloned to: ${TOOL_ROOT}"
            exit 0
            ;;
        *)
            echo -e "${RED}Error: Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 is not installed or not in PATH${NC}"
    exit 1
fi

# Check if tool's dev/src directory exists
DEV_SRC_DIR="${TOOL_ROOT}/dev/src"
if [[ ! -d "$DEV_SRC_DIR" ]]; then
    echo -e "${RED}Error: Tool source code not found at ${DEV_SRC_DIR}${NC}"
    echo ""
    echo "Please ensure you have cloned the cursor-workspace-init repository."
    echo "Expected structure:"
    echo "  ${TOOL_ROOT}/dev/src/"
    echo "  ${TOOL_ROOT}/init-cursorworkspace.sh"
    exit 1
fi

# Set Python path to include tool's source
export PYTHONPATH="${DEV_SRC_DIR}:${PYTHONPATH:-}"

# Run the initialization workflow on the current directory
echo -e "${BLUE}🚀 Initializing Cursor workspace in: ${WORKSPACE_ROOT}${NC}"
echo ""

# Execute Python script
python3 -c "
import sys
from pathlib import Path

# Add tool's dev/src to path
sys.path.insert(0, r'${DEV_SRC_DIR}')

from commands.init_cursorworkspace import run_init_workflow

# Run the initialization workflow on the current working directory
results = run_init_workflow(
    project_root=r'${WORKSPACE_ROOT}',
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
