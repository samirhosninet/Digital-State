# Quickstart: Release Readiness Validation

This guide defines the run scenarios to verify the correctness of the release readiness implementation.

## Run Scenario 1: Isolated Local Venv Installation
- **Prerequisites:** Python 3.11+ is installed.
- **Run command:**
  ```powershell
  python -m venv test-venv
  test-venv\Scripts\pip install .
  test-venv\Scripts\digitalstate init
  test-venv\Scripts\digitalstate doctor
  ```
- **Expected Outcome:** The package builds and installs, initializing the workspace successfully with all pass checks.

## Run Scenario 2: Remote Repository Installation
- **Prerequisites:** Internet access.
- **Run command:**
  ```bash
  pip install git+https://github.com/samirhosninet/Digital-State.git
  digitalstate init
  digitalstate doctor
  ```
- **Expected Outcome:** Remote installation resolves correctly and commands are executable in system PATH.
