import shutil
import subprocess
from pathlib import Path
import sys

"""Utility script to (re)generate API documentation stubs for all Evennia modules.

This script uses ``sphinx-apidoc`` to crawl the *evennia* source tree and create
``.rst`` stubs under ``docs/source/api/``.  It then converts those files to
MyST‐compatible Markdown via :pymod:`docs.pylib.api_rst2md` so they blend into the
existing documentation build.

Usage (from project root)::

    python -m docs.pylib.generate_api_stubs

The Makefile target ``make api-stubs`` will call this automatically.
"""

# Paths ---------------------------------------------------------------------
PROJ_ROOT = Path(__file__).resolve().parents[2]  # /workspace
API_DIR = PROJ_ROOT / "docs" / "source" / "api"
SRC_DIR = PROJ_ROOT / "evennia"


def _run(cmd: list[str]):
    """Run *cmd* and abort if it fails."""
    print("[api-stubs]", " ".join(cmd))
    ret = subprocess.call(cmd)
    if ret != 0:
        print("Command failed, aborting.")
        sys.exit(ret)


def _clean_api_dir():
    """Remove existing *md*/*rst* files to avoid stale pages."""
    for ext in ("*.md", "*.rst"):
        for path in API_DIR.glob(ext):
            path.unlink()


def build_stubs():
    """Generate the fresh API stubs and convert them to Markdown."""
    _clean_api_dir()

    # 1. Run sphinx-apidoc
    _run([
        "sphinx-apidoc",
        "-f",  # overwrite
        "-e",  # put each module file on its own page (separate)
        "-o",
        str(API_DIR),
        str(SRC_DIR),
        "--no-toc",  # we don't want per-module toctrees
    ])

    # 2. Convert .rst -> .md for MyST-Parser
    from docs.pylib.api_rst2md import _rst2md

    for rst_file in API_DIR.glob("*.rst"):
        _rst2md(str(rst_file))

    print("[api-stubs] 👍  Finished generating API stubs -> docs/source/api/")


if __name__ == "__main__":
    build_stubs()