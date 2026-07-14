"""Root conftest.py — ensures correct import paths for all test environments."""
import sys
import os

# Add src/ and project root to Python path for kernel, framework, and integrations imports
project_root = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(project_root, "src")

for path in [project_root, src_dir]:
    if path not in sys.path:
        sys.path.insert(0, path)
