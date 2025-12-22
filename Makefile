# Global helpers to install all Pantheon services at once.
SHELL := /bin/bash

.PHONY: install-all install-atlasforge install-aegis install-eyeofhorusops install-mnemosyne

install-all: install-atlasforge install-aegis install-eyeofhorusops install-mnemosyne

install-atlasforge:
	cd services/atlasforge && ./install.sh

install-aegis:
	cd services/aegis && ./install.sh

install-eyeofhorusops:
	cd services/eyeofhorusops && { command -v poetry >/dev/null 2>&1 && poetry install || pip install -r requirements.txt; }

install-mnemosyne:
	cd services/mnemosyne && { command -v poetry >/dev/null 2>&1 && poetry install || pip install -r requirements.txt; }
