.PHONY: help install install-dev install-global uninstall test lint format type-check clean build

help: ## Show this help message
	@echo "AtlasForge - Makefile commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies with Poetry
	poetry install

install-dev: ## Install with dev dependencies
	poetry install --with dev

install-global: ## Install globally using pipx (accessible from anywhere)
	@echo "🔧 Installing AtlasForge globally with pipx..."
	pipx install --force .
	@echo "✅ AtlasForge installed globally!"
	@echo "📍 You can now run 'atlasforge' from anywhere"
	@atlasforge version

uninstall: ## Uninstall global installation
	@echo "🗑️  Uninstalling AtlasForge..."
	pipx uninstall atlasforge
	@echo "✅ AtlasForge uninstalled"

reinstall: ## Reinstall global version (useful during development)
	@echo "🔄 Reinstalling AtlasForge..."
	pipx reinstall atlasforge
	@echo "✅ AtlasForge reinstalled!"

test: ## Run all tests
	poetry run pytest

test-unit: ## Run only unit tests
	poetry run pytest tests/unit/

test-integration: ## Run only integration tests
	poetry run pytest tests/integration/

test-cov: ## Run tests with coverage report
	poetry run pytest --cov=src/atlasforge --cov-report=term-missing --cov-report=html

lint: ## Run linter (Ruff)
	poetry run ruff check src/ tests/

lint-fix: ## Run linter with auto-fix
	poetry run ruff check src/ tests/ --fix

format: ## Format code with Black
	poetry run black src/ tests/

format-check: ## Check code formatting
	poetry run black src/ tests/ --check

type-check: ## Run type checking with MyPy
	poetry run mypy src/

quality: lint format-check type-check ## Run all quality checks

clean: ## Clean build artifacts and cache
	rm -rf build/ dist/ *.egg-info
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

build: clean ## Build package with Poetry
	poetry build

# Development workflow
dev-setup: install-dev ## Complete development setup
	@echo "✅ Development environment ready!"
	@echo "Run 'make test' to verify installation"

# Quick commands
check: quality test ## Run all checks (quality + tests)

# Example usage
demo: ## Generate example project in /tmp
	poetry run atlasforge generate demo-service --output /tmp
	@echo "✅ Demo project created at /tmp/demo-service"
