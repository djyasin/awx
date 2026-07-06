#!/bin/bash
# Apply security patches to pip's vendored dependencies.
# These patches mitigate vulnerabilities where no upstream fix is available yet.
# Each patch file should be named after its CVE and removed when upstream fixes land.
#
# Usage: apply_pip_patches.sh <patches_dir> <python_executable>
#   patches_dir:       Directory containing .patch files
#   python_executable: Python executable whose pip should be patched
#                      (e.g., /var/lib/awx/venv/awx/bin/python3.12 or python3.12)
set -euo pipefail

PATCH_DIR_ARG="${1:?Usage: $0 <patches_dir> <python_executable>}"
PYTHON_EXE="${2:?Usage: $0 <patches_dir> <python_executable>}"

if [ ! -d "$PATCH_DIR_ARG" ]; then
    echo "WARNING: Patches directory $PATCH_DIR_ARG not found -- skipping"
    exit 0
fi
PATCH_DIR="$(cd "$PATCH_DIR_ARG" && pwd)"

# Locate distlib inside pip's vendored packages
DISTLIB_DIR=$("$PYTHON_EXE" -c "import pip._vendor.distlib; import os; print(os.path.dirname(pip._vendor.distlib.__file__))" 2>/dev/null) || {
    echo "WARNING: Could not locate pip._vendor.distlib via $PYTHON_EXE -- skipping patches"
    exit 0
}

if [ ! -d "$DISTLIB_DIR" ]; then
    echo "WARNING: distlib directory not found at $DISTLIB_DIR -- skipping patches"
    exit 0
fi

applied=0
for patch_file in "$PATCH_DIR"/*.patch; do
    [ -f "$patch_file" ] || continue
    patch_name="$(basename "$patch_file")"
    echo "Applying patch: $patch_name to $DISTLIB_DIR"
    if (cd "$DISTLIB_DIR" && patch -p1 --forward --batch < "$patch_file"); then
        echo "  Applied: $patch_name"
        applied=$((applied + 1))
    else
        # patch --forward returns exit code 1 both when the patch is already
        # applied and when it genuinely fails to match.  In either case we
        # log and continue rather than aborting the build.
        echo "  Skipped: $patch_name (already applied or does not match)"
    fi
done

echo "Pip patches complete: $applied applied"
