<!-- GitHub Copilot instructions for codegen agents -->
# 🧭 Instruções rápidas para agentes (GitHub Copilot)

Estas instruções ajudam um agente a ser produtivo rapidamente neste repositório. Siga estritamente as convenções existentes e cite arquivos de referência quando fizer mudanças.

## Visão geral (big picture)
- Plataforma Atlas: repositório de documentação + implementações para pequenos serviços (~Clean Architecture). Principais serviços: `atlasforge` (gerador), `aegis` (scans), `mnemosyne`, `eyeofhorusops`.
- Padrão arquitetural: Clean Architecture (domain → application → adapters/infrastructure → api/presentation). Ex.: `services/atlasforge/src/atlasforge/`.

## Onde olhar primeiro
- Arquitetura e decisões: `.claude/CLAUDE.md` e `docs/`.
- Implementação de cada serviço: `services/<service>/README.md` (ex.: `services/atlasforge/README.md`, `services/aegis/README.md`).
- CLI e casos de uso: `presentation/cli/` e `application/use_cases/` (ex.: `GenerateProjectUseCase` em `services/atlasforge/src/atlasforge/application/use_cases/generate_project.py`).

## Comandos e workflows importantes
- Desenvolvimento / ambiente: `poetry install` ou `make install-dev` (ver `services/*/Makefile`).
- Testes: `make test` ou `poetry run pytest` (ex.: `services/atlasforge/Makefile`).
- Qualidade: `make lint` (Ruff), `make format` (Black), `make type-check` (Mypy), `make quality` para tudo junto.
- Instalação global de CLIs: `pipx install .` ou via `make install-global` (ex.: `services/atlasforge/Makefile`).
- Exemplos de execução: `atlasforge generate my-service` e `aegis scan --repo . --output -`.

## Convenções de código e padrões do projeto
- Estrutura: usar camadas `domain`, `application`, `infrastructure/adapters`, `presentation/api`.
- Imutabilidade e value objects: muitos modelos usam dataclasses frozen e validação em value objects (veja `domain/value_objects`).
- CLI: Typer + Rich para saída (ex.: `services/atlasforge/src/atlasforge/presentation/cli/main.py`).
- Templates: Jinja2 para scaffolding do `atlasforge` (veja `services/atlasforge/src/atlasforge/templates/`).
- Manifestos e checksums: projetos gerados têm `.atlasforge/manifest.json` com checksums SHA256 (`TemplateManifest` entity).

## Integrações e variáveis de ambiente
- MongoDB: `MONGO_URI` é chave para conexões (ex.: `services/aegis` persiste reports). Não hardcodear secrets.
- Observabilidade: endpoints `/health` e `/metrics` e uso de OpenTelemetry (consistente entre serviços; documentado em `.claude/CLAUDE.md`).
- Eventos versionados: padrão `<dominio>.v<versao>.<acao>` (ex.: `user.v1.created`).

## CI / PR / Pre-commit
- Jobs de exemplo: `services/aegis/.github/workflows/aegis-scan.yml` (rodar `poetry install` e `aegis scan`).
- Pre-commit: projetos usam hooks (ex.: instruções em `services/aegis/README.md`).

## Exemplos concretos ao modificar código (faça isto sempre)
1. Se adicionar uma nova CLI command: atualize `presentation/cli` + `Makefile` de dev + README do serviço + adicione testes em `tests/`.
2. Ao modificar esquema de eventos: documente o novo evento e a versão; adicione exemplos em `docs/`.
3. Ao tocar persistência: siga o adapter pattern (`adapters/mongo_repository.py`) e escreva testes unitários e de integração.

## O que evitar
- Não mude contratos de eventos sem versionar.
- Não introduza novos padrões globais sem documentação e aprovação (consulte `docs/` e `.claude/CLAUDE.md`).

## Perguntas & lugares para confirmar contexto
- Antes de decisões que afetam vários serviços, abra uma issue ou consulte `docs/DECISIONS.md` e o autor responsável pelo serviço (veja `services/<service>/README.md`).

---
Se esta instrução estiver incompleta, diga quais áreas quer que eu detalhe (ex.: padrões de testes, pipeline CI, ou templates Jinja específicos) — eu atualizo o arquivo com exemplos adicionais. ✅

## Snippets úteis (copiar/colar) 🚀
Pequenos trechos práticos para tarefas comuns — copie e cole onde precisar.

### Setup de ambiente
```bash
python -m venv .venv && source .venv/bin/activate
python -m pip install --upgrade pip
poetry install
```

### Executar / desenvolver localmente
```bash
# Gerar um projeto de exemplo com AtlasForge
cd services/atlasforge
poetry run atlasforge generate demo-service --output /tmp

# Rodar um serviço FastAPI gerado
cd /tmp/demo-service
poetry install
poetry run uvicorn src.my_service.presentation.api.main:app --reload
```

### Testes & cobertura
```bash
# Rodar todos os testes
make test

# Cobertura
poetry run pytest --cov=src/ --cov-report=term-missing --cov-report=html

# Testes unit / integration separados (quando aplicável)
make test-unit
make test-integration
```

### Qualidade de código
```bash
make lint        # Ruff
make format      # Black
make type-check  # Mypy
make quality     # Tudo junto
```

### Build & instalação global (pipx)
```bash
# AtlasForge (instala globalmente)
cd services/atlasforge && make install-global

# Aegis (build + pipx)
cd services/aegis && poetry build
pipx install --force dist/aegis-*.whl
```

### Execução rápida (Aegis)
```bash
# Via Poetry (desenvolvimento)
cd services/aegis && poetry run aegis scan --repo . --commit HEAD --output -

# Via instalação global (pipx)
aegis scan --repo . --output -
```

### Exemplo de step para GitHub Actions
```yaml
- name: Install (Poetry)
	run: |
		python -m pip install --upgrade pip
		pip install poetry
		cd services/aegis
		poetry install --no-interaction
- name: Run aegis scan (Poetry)
	run: |
		cd services/aegis
		poetry run aegis scan --repo ${{ github.repository }} --commit ${{ github.sha }} --output -
```

### Exemplo de pre-commit hook (Aegis)
```yaml
repos:
	- repo: local
		hooks:
			- id: aegis-scan
				name: Aegis scan
				entry: aegis scan --repo . --commit HEAD --output -
				language: system
				pass_filenames: false
```

> Observação: quer que eu adicione equivalentes para PowerShell/Windows, comandos de debug (ex.: VS Code attach, breakpoints), ou mais variações de CI? 
