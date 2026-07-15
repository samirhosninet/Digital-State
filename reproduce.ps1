# reproduction script for Digital State native Hermes integration verification
$ErrorActionPreference = "Stop"

# Prepend known paths to ensure local environment runs cleanly
$env:PATH = "C:\Users\I-Master\AppData\Local\hermes\bin;C:\Users\I-Master\AppData\Local\hermes\git\cmd;C:\Users\I-Master\AppData\Local\hermes\hermes-agent\venv\Scripts;" + $env:PATH
$env:no_proxy = "127.0.0.1,localhost"

Write-Host "=== 1. Running test suite (pytest) ==="
.venv\Scripts\python.exe -m pytest tests/

Write-Host "=== 2. Running hook contract verification ==="
C:\Users\I-Master\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe scripts/verify_hook_contract.py

Write-Host "=== 3. Running security boundaries verification ==="
C:\Users\I-Master\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe scripts/verify_security_boundaries.py

Write-Host "=== 4. Running digitalstate doctor check ==="
.venv\Scripts\python.exe -m digital_state.cli.cli doctor

Write-Host "=== All verification steps passed. ==="
