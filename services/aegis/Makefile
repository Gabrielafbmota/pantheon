POETRY ?= poetry

.PHONY: install test scan run

install:
	@echo "Installing dependencies with Poetry (in service dir)"
	cd $(dir) && $(POETRY) install

test:
	@echo "Running tests with Poetry"
	cd services/aegis && poetry run pytest services/aegis/tests -q

scan:
	@echo "Run aegis scan via Poetry"
	cd services/aegis && poetry run aegis scan --repo . --commit HEAD --output -

run:
	@echo "Run arbitrary aegis command: e.g. make run ARGS='scan --repo . --output -'"
	cd services/aegis && poetry run aegis $(ARGS)
