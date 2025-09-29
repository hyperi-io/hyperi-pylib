#!/bin/bash
# Setup scaffold files based on project type

set -e

PROJECT_TYPE="${1:-cli}"
PACKAGE_NAME="${2:-package}"
INCLUDE_API="${3:-false}"
MODE="${4:-install}"  # install|check

echo "Setting up ${PROJECT_TYPE} scaffold for ${PACKAGE_NAME}} (mode=${MODE})..."

plan_copy() {
  local src="$1"; shift
  local dst="$1"; shift
  if [ -f "${src}" ]; then
    echo "  plan: copy ${src} -> ${dst}"
  fi
}

do_copy() {
  local src="$1"; shift
  local dst="$1"; shift
  if [ -f "${src}" ]; then
    cp "${src}" "${dst}"
    echo "  ✓ Created ${dst}"
  fi
}

case "${PROJECT_TYPE}" in
  "cli")
    # Copy CLI scaffold files (default)
    if [ "${MODE}" = "check" ]; then
      plan_copy "scaffolds/cli/cli.py" "src/${PACKAGE_NAME}/cli.py"
    else
      do_copy "scaffolds/cli/cli.py" "src/${PACKAGE_NAME}/cli.py"
    fi
    ;;
    
  "package")
    # Copy package scaffold files
    if [ "${MODE}" = "check" ]; then
      plan_copy "scaffolds/package/client.py" "src/${PACKAGE_NAME}/client.py"
    else
      do_copy "scaffolds/package/client.py" "src/${PACKAGE_NAME}/client.py"
    fi
    ;;
    
  "daemon")
    # Copy daemon scaffold files
    if [ "${MODE}" = "check" ]; then
      plan_copy "scaffolds/daemon/daemon.py" "src/${PACKAGE_NAME}/daemon.py"
      plan_copy "scaffolds/daemon/__main__.py" "src/${PACKAGE_NAME}/__main__.py"
    else
      do_copy "scaffolds/daemon/daemon.py" "src/${PACKAGE_NAME}/daemon.py"
      do_copy "scaffolds/daemon/__main__.py" "src/${PACKAGE_NAME}/__main__.py"
    fi
    
    # If include_api is true, also copy API files
    if [ "${INCLUDE_API}" = "true" ]; then
      echo "  Including API in daemon..."
      if [ "${MODE}" = "check" ]; then
        plan_copy "scaffolds/api/api.py" "src/${PACKAGE_NAME}/api.py"
      else
        do_copy "scaffolds/api/api.py" "src/${PACKAGE_NAME}/api.py"
      fi
    fi
    ;;
    
  *)
    echo "Unknown project type: ${PROJECT_TYPE}"
    exit 1
    ;;
esac

# Clean up scaffolds directory if it exists (only in install mode)
if [ "${MODE}" != "check" ] && [ -d "scaffolds" ]; then
  rm -rf scaffolds
  echo "  ✓ Cleaned up scaffold templates"
fi

echo "Scaffold setup complete!"
