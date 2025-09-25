#!/bin/bash
# Setup scaffold files based on project type

set -e

PROJECT_TYPE="${1:-cli}"
PACKAGE_NAME="${2:-package}"
INCLUDE_API="${3:-false}"

echo "Setting up ${PROJECT_TYPE} scaffold for ${PACKAGE_NAME}..."

case "${PROJECT_TYPE}" in
  "cli")
    # Copy CLI scaffold files (default)
    if [ -f "scaffolds/cli/cli.py" ]; then
      cp scaffolds/cli/cli.py "src/${PACKAGE_NAME}/cli.py"
      echo "  ✓ Created src/${PACKAGE_NAME}/cli.py"
    fi
    ;;
    
  "package")
    # Copy package scaffold files
    if [ -f "scaffolds/package/client.py" ]; then
      cp scaffolds/package/client.py "src/${PACKAGE_NAME}/client.py"
      echo "  ✓ Created src/${PACKAGE_NAME}/client.py"
    fi
    ;;
    
  "daemon")
    # Copy daemon scaffold files
    if [ -f "scaffolds/daemon/daemon.py" ]; then
      cp scaffolds/daemon/daemon.py "src/${PACKAGE_NAME}/daemon.py"
      echo "  ✓ Created src/${PACKAGE_NAME}/daemon.py"
    fi
    if [ -f "scaffolds/daemon/__main__.py" ]; then
      cp scaffolds/daemon/__main__.py "src/${PACKAGE_NAME}/__main__.py"
      echo "  ✓ Created src/${PACKAGE_NAME}/__main__.py"
    fi
    
    # If include_api is true, also copy API files
    if [ "${INCLUDE_API}" = "true" ]; then
      echo "  Including API in daemon..."
      if [ -f "scaffolds/api/api.py" ]; then
        cp scaffolds/api/api.py "src/${PACKAGE_NAME}/api.py"
        echo "  ✓ Created src/${PACKAGE_NAME}/api.py"
      fi
    fi
    ;;
    
  *)
    echo "Unknown project type: ${PROJECT_TYPE}"
    exit 1
    ;;
esac

# Clean up scaffolds directory if it exists
if [ -d "scaffolds" ]; then
  rm -rf scaffolds
  echo "  ✓ Cleaned up scaffold templates"
fi

echo "Scaffold setup complete!"
