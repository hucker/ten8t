#!/usr/bin/env zsh
#
# Documentation and Metrics Generator
# Generates documentation files, metrics, and builds the README
#

# Provide some useful feedback in script output.
error_handler() {
    echo "=== ERROR REPORT ==="
    echo "Error occurred on line: $1"
    echo "Command that failed: $2"
    echo "Exit status: $3"

    exit $3
}

# Use the error handler with multiple context variables
trap 'error_handler $LINENO "$BASH_COMMAND" $?' ERR



# Define base directories
DOCS_DIR="."                   # Current directory (docs folder)
PROJECT_ROOT=".."              # Parent directory (project root)
SRC_DIR="${PROJECT_ROOT}/src/ten8t"
SNIPPETS_DIR="${DOCS_DIR}/snippets"  # Folder for generated partial files for README.md

# Error handling - exit on any error
setopt ERR_EXIT
setopt PIPE_FAIL

# Define required dependencies
REQUIRED_TOOLS=("python" "radon" "make")
REQUIRED_SCRIPTS=(
    "${SRC_DIR}/cli/ten8t_cli.py"
    "${SRC_DIR}/rich_ten8t/rich_demo.py"
    "${DOCS_DIR}/qc_radon.py"
    "${DOCS_DIR}/insert_files.py"
    "${DOCS_DIR}/add_badges.py"
)
dir
# Check for required tools
echo "Checking required external tools..."
for tool in "${REQUIRED_TOOLS[@]}"; do
    command -v "$tool" >/dev/null 2>&1 || {
        echo "$tool is required but not installed. Aborting."
        exit 1
    }
done

# Check for required scripts
echo "Checking required project scripts..."
for script in "${REQUIRED_SCRIPTS[@]}"; do
    if [[ ! -f "$script" ]]; then
        echo "Required script $script not found. Aborting."
        exit 1
    fi
done

# Create snippets directory if it doesn't exist
mkdir -p ${SNIPPETS_DIR}

# Status messages and improved organization
echo "Generating help documentation..."
python ${SRC_DIR}/cli/ten8t_cli.py --help > ${SNIPPETS_DIR}/help.txt
python ${SRC_DIR}/rich_ten8t/rich_demo.py > ${SNIPPETS_DIR}/rich_demo.txt

echo "Generating example results..."
(
  cd ${SRC_DIR}/cli || exit 1
  python ten8t_cli.py --json=${DOCS_DIR}/snippets/result.json --pkg=../examples/file_system
)

echo "Generating code metrics..."
radon cc --json   ${SRC_DIR}/t*.py > ${SNIPPETS_DIR}/radon_cc.json
radon mi --json   ${SRC_DIR}/t*.py > ${SNIPPETS_DIR}/radon_mi.json
radon hal --json  ${SRC_DIR}/t*.py > ${SNIPPETS_DIR}/radon_hal.json
python ${DOCS_DIR}/qc_radon.py

echo "Generating README and documentation..."
python ${DOCS_DIR}/insert_files.py --output=${PROJECT_ROOT}/README.md ${PROJECT_ROOT}/README.md
python ${DOCS_DIR}/add_badges.py

echo "Building HTML documentation..."
cd ${DOCS_DIR}
make clean
make html

echo "Documentation generation complete!"
