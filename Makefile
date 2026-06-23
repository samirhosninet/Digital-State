# Digital State Makefile
# Unified command targets for Windows (PowerShell) and POSIX (Linux/macOS)

.PHONY: test validate install promote clean help smoke-test

# Configuration
PYTHON := python3
SHELL := /bin/bash

## test — Run pytest suite
# Usage: make test
test:
	@echo "Running pytest suite..."
	$(PYTHON) -m pytest tests/ -v --tb=short

## validate — Run structural and config validation
# Usage: make validate
validate:
	@echo "Running validate-final.ps1..."
	powershell -File scripts/validate-final.ps1

## install — Run full installer
# Usage: make install
install:
	@echo "Running full installer..."
	powershll -File scripts/install.ps1

## install-simple — Run streamlined installer
# Usage: make install-simple
install-simple:
	@echo "Running simple installer..."
	powershell -File scripts/install-simple.ps1

## uninstall — Remove all installed Digital State artifacts
# Usage: make uninstall
uninstall:
	@echo "Running uninstaller..."
	powershell -File scripts/uninstall.ps1

## promote — Promote a blocked (review-required) card to review
# Usage: make promote ID=<card_id>
promote:
	@if [ -z "$(ID)" ]; then echo "Usage: make promote ID=<card_id>"; exit 1; fi
	bash scripts/promote-to-review.sh $(ID)

## smoke-test — Run Hermes CLI smoke tests (requires Hermes)
# Usage: make smoke-test
smoke-test:
	@echo "Running Hermes CLI smoke tests..."
	$(PYTHON) -m pytest tests/test_smoke_hermes_cli.py -v --tb=short -rx

## lint — Run basic validation checks
# Usage: make lint
lint:
	@echo "Running structural validation..."
	$(PYTHON) tests/test_validate_final.py
	$(PYTHON) tests/test_version_sync.py
	$(PYTHON) tests/test_concurrency_cap.py

## clean — Remove __pycache__ and temporary files
# Usage: make clean
clean:
	@echo "Removing Python cache..."
	rm -rf tests/__pycache__
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete

## help — Show all available targets
# Usage: make help
help:
	@echo "Digital State Makefile targets:"
	@echo "  test        — Run pytest suite (test_version_sync, test_concurrency_cap, ...)"
	@echo "  validate    — Run validate-final.ps1 structural checks"
	@echo "  install     — Run full installer (scripts/install.ps1)"
	@echo "  install-simple — Run streamlined installer"
	@echo "  uninstall   — Remove all installed Digital State artifacts"
	@echo "  promote     — Promote blocked card to review: make promote ID=<card_id>"
	@echo "  smoke-test  — Run Hermes CLI smoke tests (requires hermes)"
	@echo "  lint        — Run all validation checks"
	@echo "  clean       — Remove Python cache and temporary files"
	@echo "  help        — Show this help message"
	@echo ""
	@echo "NOTE: On Windows, use 'make -f Makefile <target>' with Git Bash / MSYS."
	@echo "      For PowerShell, run scripts/ directly."