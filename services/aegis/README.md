# Aegis - Guardião de Qualidade e Segurança

**Versão**: 0.1.0 (MVP1 Completo)

Aegis é o guardião de qualidade e segurança da plataforma Atlas. Bloqueia regressões de qualidade e segurança **antes** do deploy através de scans automatizados.

## Características

- **CLI completa**: `aegis scan`, `aegis persist`
- **Scanners reais**:
  - **Ruff**: Lint Python rápido e moderno
  - **Black**: Verificação de formatação
  - **detect-secrets**: Detecção de secrets hardcoded
- **Baseline delta**: Compara findings com baseline, bloqueia apenas novos
- **Persistência MongoDB**: Armazena histórico de scans
- **Pre-commit hook**: Verificações rápidas antes do commit
- **CI/CD**: GitHub Actions para gate em PRs
- **Instalação global**: Via pipx para uso em qualquer projeto

## Instalação

### Pré-requisitos

- Python 3.11+
- Poetry (desenvolvimento) ou pipx (instalação global)

### Instalação Global (Recomendado)

Para usar Aegis em qualquer projeto:

```bash
cd services/aegis
./install.sh
```

Ou via Makefile:

```bash
cd services/aegis
make install-global
```

Depois da instalação:

```bash
aegis scan --repo . --output -
```

### Instalação Local (Desenvolvimento)

No diretório do serviço:

```bash
cd services/aegis
poetry install
poetry run aegis scan --repo . --output -
```

## Uso

### Scan Básico

```bash
aegis scan --repo . --commit HEAD --output -
```

### Scan com Scanners Específicos

```bash
aegis scan --scanners ruff,secrets --fail-on HIGH
```

### Scan com Baseline Delta

```bash
# Criar baseline inicial
aegis scan --output baseline.json

# Scan comparando com baseline (só falha em novos findings)
aegis scan --baseline baseline.json
```

### Persistir Report no MongoDB

```bash
aegis scan --output report.json
aegis persist --input-file report.json --mongo-uri "mongodb://localhost:27017"
```

### Opções Disponíveis

**aegis scan**:
- `--repo PATH`: Caminho do repositório (default: `.`)
- `--commit REF`: Commit/ref sendo escaneado (default: `HEAD`)
- `--output FILE`: Arquivo de saída (`-` para stdout)
- `--fail-on SEVERITY`: Falhar se finding >= severity (default: `HIGH`)
- `--baseline FILE`: Arquivo JSON com fingerprints aceitos
- `--scanners LIST`: Lista separada por vírgulas (default: `ruff,black,secrets`)

**aegis persist**:
- `--input-file FILE`: Report JSON (`-` para stdin)
- `--mongo-uri URI`: Connection string (overrides `MONGO_URI` env)

## Integração

### Pre-commit Hook

Adicione ao `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: aegis-scan
        name: Aegis scan
        entry: aegis scan --repo . --commit HEAD --output -
        language: system
        types: [python]
        pass_filenames: false
```

Instale:

```bash
pre-commit install
```

### GitHub Actions

Exemplo de workflow:

```yaml
name: Aegis Scan

on: [pull_request]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install Aegis
        run: pipx install path/to/aegis/dist/*.whl
      - name: Run scan
        run: aegis scan --repo . --commit ${{ github.sha }}
```

## Scanners

### Ruff (Lint)

- **Propósito**: Lint Python (substituto de flake8, pylint)
- **Severidades**: Erros → MEDIUM, Segurança → HIGH, Warnings → LOW
- **Performance**: ~100ms para projetos médios

### Black (Format)

- **Propósito**: Verificação de formatação
- **Severidade**: LOW
- **Modo**: Check-only (não reformata)

### detect-secrets (Secrets)

- **Propósito**: Detectar secrets hardcoded
- **Severidade**: CRITICAL
- **Tipos**: API keys, tokens, senhas, connection strings

## Helpers

- `./run.sh` — wrapper para `poetry run aegis` (ex.: `./run.sh scan --repo .`)
- `Makefile` com alvos:
  - `make install` — instala dependências localmente
  - `make install-global` — instala globalmente via pipx
  - `make test` — roda testes
  - `make scan` — executa scan no projeto
  - `make run ARGS='...'` — executa comando customizado

## Documentação

- [IMPLEMENTATION.md](IMPLEMENTATION.md): Documentação técnica completa
- [docs/DECISIONS.md](docs/DECISIONS.md): Decisões de design e trade-offs
- [MVP_VALIDATION.md](MVP_VALIDATION.md): Análise de estado do MVP

## Testes

```bash
cd services/aegis
poetry run pytest -v
```

**Status**: 8 testes passando, cobertura de modelos, CLI, repositories e events.

## MVP1 Status ✅

Lista de funcionalidades implementadas:

- [x] **Modelo de domínio** — `Policy`, `Rule`, `Scan`, `Finding`, `Baseline`, `Waiver`
- [x] **CLI completa** — `scan` e `persist` com Typer
- [x] **Scanners reais** — Ruff, Black, detect-secrets
- [x] **Baseline delta** — Comparação de findings
- [x] **Persistência MongoDB** — `MongoReportRepository`
- [x] **Pre-commit hook** — Verificações rápidas
- [x] **CI/CD** — GitHub Actions workflow
- [x] **Instalador global** — Makefile e install.sh
- [x] **Testes** — Unitários com 100% de aprovação
- [x] **Documentação** — README, IMPLEMENTATION, DECISIONS
- [x] **Integrações de eventos** — Stubs para Mnemosyne e EyeOfHorusOps

## Roadmap

### MVP2 (Próximos Passos)

- [ ] **Waivers CRUD**: Comandos `waiver create|list|revoke`
- [ ] **Aplicar waivers** durante scan (skip findings cobertos)
- [ ] **Export/import baselines**: Persistência e versionamento
- [ ] **Publishers reais**: Eventos para Mnemosyne e EyeOfHorusOps
- [ ] **Scanners adicionais**: bandit (SAST), pip-audit (dependências)
- [ ] **Testes E2E**: Integração completa

### MVP3 (Evoluções)

- [ ] **Políticas como código**: YAML/JSON versionado
- [ ] **Painel web**: Visualização de scans e tendências
- [ ] **Learning mode**: Não bloqueia, apenas reporta
- [ ] **Auto-remediation**: Fixes automáticos quando possível
- [ ] **Métricas**: Dashboards e alertas
- [ ] **Multi-linguagem**: Go, Rust, TypeScript, Java

## Arquitetura

Aegis segue Clean Architecture:

```
src/aegis/
├── models.py          # Domain (entidades puras)
├── cli.py             # Application (casos de uso)
├── adapters/          # Infrastructure (I/O)
│   ├── mongo_repository.py
│   └── events.py
└── scanners/          # Infrastructure (tools)
    ├── base.py
    ├── ruff_scanner.py
    ├── black_scanner.py
    └── secrets_scanner.py
```

Veja [IMPLEMENTATION.md](IMPLEMENTATION.md) para detalhes completos.

## Contribuindo

### Adicionar Novo Scanner

1. Criar `src/aegis/scanners/meu_scanner.py`
2. Herdar de `Scanner` e implementar `scan()` e `name`
3. Registrar em `cli.py`
4. Adicionar testes

Ver [IMPLEMENTATION.md](IMPLEMENTATION.md) para detalhes.

## Troubleshooting

### Scanner não encontrado

```
Finding: ruff-not-found - Ruff binary not found in PATH
```

**Solução**: `pip install ruff` ou garantir que está no PATH

### MongoDB não conecta

```
EnvironmentError: MONGO_URI is required
```

**Solução**: `export MONGO_URI="mongodb://localhost:27017"` ou passar `--mongo-uri`

## Licença

Projeto interno Atlas Platform

## Autores

- Gabriela (implementação)
- Claude Code (assistência)

---

**Status**: ✅ MVP1 Completo e pronto para uso!
