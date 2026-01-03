#!/bin/bash
# Build and publish G13 Linux driver to PyPI
#
# Usage:
#   ./publish.sh          # Build and upload to PyPI
#   ./publish.sh test     # Build and upload to TestPyPI
#   ./publish.sh build    # Build only, no upload

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Determine action
ACTION="${1:-upload}"

echo -e "${GREEN}=== G13 Linux PyPI Build Script ===${NC}"

# Check for required tools
check_tools() {
    echo -e "${YELLOW}Checking required tools...${NC}"
    
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Error: python3 is required${NC}"
        exit 1
    fi
    
    if ! python3 -c "import build" &> /dev/null; then
        echo -e "${YELLOW}Installing build tool...${NC}"
        pip install build
    fi
    
    if ! python3 -c "import twine" &> /dev/null; then
        echo -e "${YELLOW}Installing twine...${NC}"
        pip install twine
    fi
    
    echo -e "${GREEN}All tools available${NC}"
}

# Clean previous builds
clean() {
    echo -e "${YELLOW}Cleaning previous builds...${NC}"
    rm -rf build/
    rm -rf dist/
    rm -rf *.egg-info/
    rm -rf src/*.egg-info/
    echo -e "${GREEN}Clean complete${NC}"
}

# Build the package
build_package() {
    echo -e "${YELLOW}Building package...${NC}"
    python3 -m build
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Build successful!${NC}"
        echo ""
        echo "Built files:"
        ls -la dist/
    else
        echo -e "${RED}Build failed!${NC}"
        exit 1
    fi
}

# Check the package
check_package() {
    echo -e "${YELLOW}Checking package with twine...${NC}"
    python3 -m twine check dist/*
}

# Upload to PyPI
upload_pypi() {
    echo -e "${YELLOW}Uploading to PyPI...${NC}"
    echo -e "${RED}WARNING: This will upload to the REAL PyPI!${NC}"
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python3 -m twine upload dist/*
        echo -e "${GREEN}Upload complete!${NC}"
    else
        echo "Upload cancelled."
    fi
}

# Upload to TestPyPI
upload_testpypi() {
    echo -e "${YELLOW}Uploading to TestPyPI...${NC}"
    python3 -m twine upload --repository testpypi dist/*
    echo -e "${GREEN}Upload to TestPyPI complete!${NC}"
    echo ""
    echo "Install from TestPyPI with:"
    echo "  pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ g13-linux"
}

# Main execution
check_tools
clean
build_package
check_package

case "$ACTION" in
    "build")
        echo -e "${GREEN}Build complete. Package ready in dist/${NC}"
        ;;
    "test")
        upload_testpypi
        ;;
    "upload"|*)
        upload_pypi
        ;;
esac

echo ""
echo -e "${GREEN}Done!${NC}"
