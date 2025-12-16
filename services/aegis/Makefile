POETRY ?= poetry

.PHONY: install test scan run install-global uninstall-global

install:
	@echo "Installing dependencies with Poetry"
	$(POETRY) install

test:
	@echo "Running tests with Poetry"
	$(POETRY) run pytest -q

scan:
	@echo "Run aegis scan via Poetry"
	$(POETRY) run aegis scan --repo . --commit HEAD --output -

run:
	@echo "Run arbitrary aegis command: e.g. make run ARGS='scan --repo . --output -'"
	$(POETRY) run aegis $(ARGS)

install-global:
	@echo "Installing Aegis globally via pipx"
	@if ! command -v pipx >/dev/null 2>&1; then \
		echo "ERROR: pipx is not installed. Please install it first:"; \
		echo "  python -m pip install --user pipx"; \
		echo "  python -m pipx ensurepath"; \
		exit 1; \
	fi
	@echo "Building package..."
	$(POETRY) build
	@echo "Installing with pipx..."
	pipx install --force dist/aegis-0.1.0-py3-none-any.whl
	@echo ""
	@echo "✅ Aegis installed globally!"
	@echo "You can now run: aegis scan --repo . --output -"

uninstall-global:
	@echo "Uninstalling Aegis from pipx"
	pipx uninstall aegis || true
