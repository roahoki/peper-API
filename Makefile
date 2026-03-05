# ─── Paths ────────────────────────────────────────────────────────────────────
PYTHON  := .venv/bin/python
UVICORN := .venv/bin/uvicorn
RUFF    := .venv/bin/ruff
CZ      := .venv/bin/cz

# ─── Phony targets ────────────────────────────────────────────────────────────
.PHONY: help install install-dev dev lint fix format check commit bump changelog clean

# Default target
help:
	@echo ""
	@echo "  Usage: make <target>"
	@echo ""
	@echo "  Setup"
	@echo "    install        Install production dependencies into .venv"
	@echo "    install-dev    Install dev/tooling dependencies into .venv"
	@echo ""
	@echo "  Development"
	@echo "    dev            Run the FastAPI server with hot-reload"
	@echo ""
	@echo "  Quality"
	@echo "    lint           Check code with ruff (no changes)"
	@echo "    fix            Auto-fix lint issues with ruff"
	@echo "    format         Format code with ruff formatter"
	@echo "    check          lint + format check (CI-friendly, no changes)"
	@echo ""
	@echo "  Commits & versioning"
	@echo "    commit         Open commitizen interactive commit prompt"
	@echo "    bump           Bump version based on commit history"
	@echo "    changelog      Generate / update CHANGELOG.md"
	@echo ""
	@echo "  Misc"
	@echo "    clean          Remove __pycache__ and .ruff_cache"
	@echo ""

# ─── Setup ────────────────────────────────────────────────────────────────────
install:
	python3 -m venv .venv
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

install-dev: install
	$(PYTHON) -m pip install -r requirements-dev.txt

# ─── Development ──────────────────────────────────────────────────────────────
dev:
	$(UVICORN) src.main:app --reload --host 0.0.0.0 --port 8000

# ─── Quality ──────────────────────────────────────────────────────────────────
lint:
	$(RUFF) check .

fix:
	$(RUFF) check --fix .

format:
	$(RUFF) format .

# Runs both lint and format-check without modifying files (safe for CI)
check:
	$(RUFF) check .
	$(RUFF) format --check .

# ─── Commits & versioning ─────────────────────────────────────────────────────
commit:
	$(CZ) commit

bump:
	$(CZ) bump --changelog

changelog:
	$(CZ) changelog

# ─── Misc ─────────────────────────────────────────────────────────────────────
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache"  -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleaned."
