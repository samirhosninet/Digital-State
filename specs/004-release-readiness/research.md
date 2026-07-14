# Research: Release Readiness Hardening

## Decision 1: Platform-Independent Test Path Resolution
- **Decision:** Resolve paths dynamically relative to test file (`__file__`) location using `os.path.dirname` instead of absolute paths.
- **Rationale:** Ensures that test suites can run successfully on any developer machine or remote CI environment (Windows, Linux, macOS).
- **Alternatives Considered:** Using environment variables to set source root, rejected because it requires extra user configuration before running tests.

## Decision 2: Empty Initial Agent Registry
- **Decision:** Ensure `digitalstate init` initializes `.specify/agents.json` as an empty dictionary `{}` instead of auto-populating mock keys.
- **Rationale:** Aligns with core security architecture: user must explicitly register agents with actual cryptographic keys using `digitalstate register`.
- **Alternatives Considered:** Writing default keys, rejected as it violates Prime's constraint: "Do not create fake cryptographic keys."
