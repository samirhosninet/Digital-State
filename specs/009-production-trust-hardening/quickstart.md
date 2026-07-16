# Validation Quickstart: Production Trust Hardening

1. Create a fresh supported workspace and install the built package by its public install path.
2. Initialize it and run `digitalstate doctor`; verify a missing Hermes runtime is reported as `unavailable`, not live.
3. Register roles using generated supported public keys. Submit valid and deliberately invalid signatures; only valid authorized submissions may change state.
4. Modify an audit record or state record in a disposable workspace. Verify integrity fails closed; run recovery with a valid named source and verify preservation plus recovery evidence.
5. Run the release gate from a clean tree. Confirm its bundle names the revision, artifact, environment, mandatory checks, and a final decision.
6. Repeat with a dirty file or secret-like test fixture and confirm the release gate returns `NOT_READY` before packaging/publishing.
