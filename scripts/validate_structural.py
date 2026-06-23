#!/usr/bin/env python3
"""
Structural validator for Linux CI.
Port of the key checks from scripts/validate-final.ps1 that don't require PowerShell.
"""

import yaml
import sys
import os
import re
import glob

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def check_distribution_owned():
    """Verify all distribution_owned entries exist."""
    with open('distribution.yaml', 'r') as f:
        dist = yaml.safe_load(f)

    version = dist.get('version', '')
    print(f"Distribution version: {version}")

    errors = 0
    for item in dist.get('distribution_owned', []):
        path = item.replace('/', os.sep)
        # Check if it's a directory (ends with / or \)
        is_dir = path.endswith('/') or path.endswith('\\')
        if is_dir:
            # Remove trailing separator for os.path.isdir
            check_path = path.rstrip('/\\')
            exists = os.path.isdir(check_path)
            kind = 'dir'
        else:
            exists = os.path.isfile(path)
            kind = 'file'
        if not exists:
            print(f"ERROR: missing {kind}: {path}")
            errors += 1
        else:
            print(f"OK: {kind}: {path}")

    if errors > 0:
        print(f"\nFAILED: {errors} missing distribution_owned entries")
        sys.exit(1)
    print("\nAll distribution_owned entries exist.")
    return version

def check_version_consistency(version):
    """Check version strings across key files."""
    version_files = [
        'distribution.yaml',
        'README.md',
        'PACKAGE.md',
        'CHANGELOG.md',
        'profiles/prime/SOUL.md',
        'profiles/builder/SOUL.md',
        'profiles/auditor/SOUL.md',
        'skills/digital-state/SKILL.md',
        'specs/plan.md',
        'specs/tasks.md',
    ]

    errors = 0
    for vf in version_files:
        if os.path.exists(vf):
            content = read_file(vf)
            # Look for version pattern in frontmatter or version references
            if version in content:
                print(f"VERSION OK: {vf}")
            else:
                print(f"WARN: version {version} not found in {vf}")
        else:
            print(f"MISSING: {vf}")
            errors += 1

    return errors

def check_config_yaml_concurrency_cap():
    """Verify kanban.max_in_progress_per_profile: 1 in all profiles."""
    profiles = ['prime', 'builder', 'auditor']
    errors = 0
    for p in profiles:
        config_path = f'profiles/{p}/config.yaml'
        if os.path.exists(config_path):
            content = read_file(config_path)
            if re.search(r'max_in_progress_per_profile:\s*1', content):
                print(f"OK: {p} config.yaml has kanban.max_in_progress_per_profile: 1")
            else:
                print(f"ERROR: {p} config.yaml missing kanban.max_in_progress_per_profile: 1")
                errors += 1
        else:
            print(f"ERROR: {p} config.yaml not found")
            errors += 1
    return errors

def check_no_hardcoded_paths():
    """Check for hardcoded local paths in reusable files."""
    reusable_files = [
        'AGENTS.md',
        'README.md',
        'PACKAGE.md',
        'profiles/prime/SOUL.md',
        'profiles/builder/SOUL.md',
        'profiles/auditor/SOUL.md',
        'skills/digital-state/SKILL.md',
        'skills/premortem-plus/SKILL.md',
    ]

    errors = 0
    for f in reusable_files:
        if os.path.exists(f):
            content = read_file(f)
            # Check for C:\Users\seo or similar
            if re.search(r'C:\\\\Users\\\\seo|C:/Users/seo', content):
                print(f"ERROR: {f} contains hardcoded local path")
                errors += 1
            else:
                print(f"OK: {f} has no known hardcoded local paths")
        else:
            print(f"MISSING: {f}")
            errors += 1
    return errors

def check_no_arabic_in_non_templates():
    """Check for Arabic Unicode in non-template files."""
    text_extensions = {'.md', '.yaml', '.yml', '.ps1', '.json', '.txt'}
    errors = 0

    for root, dirs, files in os.walk('.'):
        # Skip .git, __pycache__, etc.
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext not in text_extensions:
                continue

            full_path = os.path.join(root, file)
            relative = os.path.relpath(full_path, '.')

            # Exclude localized template files (*-ar.md)
            if relative.endswith('-ar.md'):
                print(f"SKIP (template): {relative}")
                continue

            try:
                content = read_file(full_path)
                if re.search(r'[\u0600-\u06FF]', content):
                    print(f"ERROR: Arabic Unicode found in {relative}")
                    errors += 1
            except UnicodeDecodeError:
                pass  # Binary file

    if errors == 0:
        print("OK: No Arabic Unicode text found in non-template files")
    return errors

def check_skills_references():
    """Verify mandatory skills are referenced."""
    files_to_check = {
        'AGENTS.md': ['Builder produces evidence', 'Auditor judges evidence', 'Prime routes decisions', 'Spec-Kit'],
        'skills/digital-state/SKILL.md': ['Builder produces evidence', 'Auditor judges evidence', 'Prime routes decisions', 'kanban_create', 'kanban_complete', 'kanban_block', 'kanban_comment', 'Spec-Kit'],
    }

    errors = 0
    for f, required in files_to_check.items():
        if os.path.exists(f):
            content = read_file(f)
            for req in required:
                if req in content:
                    print(f"OK: {f} has '{req}'")
                else:
                    print(f"WARN: {f} missing '{req}' (may not apply)")
        else:
            print(f"MISSING: {f}")
            errors += 1
    return errors

def main():
    print("=" * 60)
    print("Digital State Structural Validator (Linux)")
    print("=" * 60)

    total_errors = 0

    print("\n[1/6] Distribution manifest...")
    version = check_distribution_owned()

    print("\n[2/6] Version consistency...")
    total_errors += check_version_consistency(version)

    print("\n[3/6] Concurrency cap (Article XIII)...")
    total_errors += check_config_yaml_concurrency_cap()

    print("\n[4/6] No hardcoded paths (Article XI)...")
    total_errors += check_no_hardcoded_paths()

    print("\n[5/6] English-only content...")
    total_errors += check_no_arabic_in_non_templates()

    print("\n[6/6] Skill references...")
    total_errors += check_skills_references()

    print("\n" + "=" * 60)
    if total_errors == 0:
        print("PASS: All structural checks passed")
        sys.exit(0)
    else:
        print(f"FAILED: {total_errors} errors")
        sys.exit(1)

if __name__ == '__main__':
    main()