# RELEASE AUTOMATION GUIDE — DIGITAL STATE

This guide describes the automated public release pipeline, semantic tagging strategy, version bump procedures, artifact verification contracts, PyPI publication process, and emergency rollback procedures for **Digital State**.

---

## 1. Automated Release Pipeline Architecture

The automated release workflow is defined in [`.github/workflows/publish-release.yml`](file:///d:/Digital-State/.github/workflows/publish-release.yml) and is triggered automatically whenever a semantic version tag matching `v*` is pushed to GitHub.

```text
git push origin v1.16.0
           │
           ▼
┌────────────────────────────────────────────────────────┐
│ Job 1: build-and-verify                                │
│  • Extract version (1.16.0)                            │
│  • Build wheel (*.whl) & source distribution (*.tar.gz) │
│  • Verify wheel install in clean venv (version/install/doctor)
│  • Verify sdist install in clean venv (version/install/doctor)
│  • Run full pytest suite (172/172 PASS)                │
└──────────────────────────┬─────────────────────────────┘
                           │ (Must PASS 100%)
                           ▼
┌────────────────────────────────────────────────────────┐
│ Job 2: publish-github-release                          │
│  • Create GitHub Release "Digital State v1.16.0"      │
│  • Compute SHA256SUMS.txt                              │
│  • Attach *.whl, *.tar.gz, SHA256SUMS, README, docs    │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│ Job 3: publish-pypi                                    │
│  • Authenticate via PyPI Trusted Publisher (OIDC)      │
│  • Publish wheel and sdist to PyPI (digital-state)     │
│  • Skip existing versions to prevent duplicate errors │
└────────────────────────────────────────────────────────┘
```

---

## 2. Tag Strategy & Versioning Conventions

Digital State enforces **Semantic Versioning (SemVer 2.0)**:

- **Format:** `v<MAJOR>.<MINOR>.<PATCH>` (e.g., `v1.16.0`)
- **Tags Rule:**
  - `v1.16.0`: Production release tag.
  - `v1.16.1`: Patch release tag.
  - `v1.17.0`: Minor feature release tag.
- **Git Annotations:** All release tags must be annotated tags (`git tag -a v1.16.0 -m "Release description"`).

---

## 3. Version Bump Procedure

When preparing a new release:

1. **Update `pyproject.toml`:**
   ```toml
   [project]
   version = "1.16.1"
   ```

2. **Update `src/digital_state/__init__.py`:**
   ```python
   __version__ = "1.16.1"
   ```

3. **Update Release Documentation:**
   Add release notes to `RELEASE_NOTES.md` and commit:
   ```bash
   git add pyproject.toml src/digital_state/__init__.py RELEASE_NOTES.md
   git commit -m "chore(release): bump version to 1.16.1"
   git push origin main
   ```

4. **Tag & Trigger Automation:**
   ```bash
   git tag -a v1.16.1 -m "Digital State v1.16.1 Release"
   git push origin v1.16.1
   ```

---

## 4. Artifact Verification & Failure Contract

Before any release artifact is published to GitHub or PyPI, the pipeline creates isolated clean virtual environments and executes mandatory verification probes:

```bash
digitalstate version
digitalstate install
digitalstate doctor
```

- **Failure Contract:** If any command returns a non-zero exit code or fails health validation (`doctor != PASS`), the pipeline immediately halts and aborts publication.
- **Rollback Guarantee:** PyPI skip-existing protection ensures failed or partial releases do not pollute PyPI indexes.

---

## 5. Emergency Rollback Procedure

If a published release exhibits a critical flaw:

1. **PyPI Index Protection:** PyPI releases cannot be deleted or re-uploaded with the same version number.
2. **Issue Patch Release:** Revert offending changes, bump PATCH version (e.g., `v1.16.1`), and push a new release tag to trigger immediate automated publication.
3. **Mark Deprecated Release:** Mark the flawed tag in GitHub Releases as a pre-release or add an advisory in `RELEASE_NOTES.md`.

---

## 6. PyPI Trusted Publisher Authentication

PyPI authentication uses **OpenID Connect (OIDC) Trusted Publisher** authentication:

- **PyPI Environment:** `pypi`
- **Permissions:** `id-token: write`
- **Publisher Setting:** Configured in PyPI project settings mapping GitHub Repository `samirhosninet/Digital-State` to environment `pypi` and workflow `.github/workflows/publish-release.yml`.
