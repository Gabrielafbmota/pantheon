# AtlasForge - Guia de Implementação e Uso

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Arquitetura](#arquitetura)
- [Instalação](#instalação)
- [Como Usar](#como-usar)
- [Como Testar](#como-testar)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Status de Implementação](#status-de-implementação)
- [Desenvolvimento](#desenvolvimento)
- [Próximos Passos](#próximos-passos)

---

## Visão Geral

**AtlasForge** é um gerador de projetos "zero-click" para criar projetos backend FastAPI com Clean Architecture, prontos para produção desde o primeiro commit.

### Características Principais

- ✅ **Geração de Projetos**: Cria projetos FastAPI completos com Clean Architecture
- ✅ **Idempotência**: Mesmo input → mesmo output (garantido)
- ✅ **Manifest Tracking**: Rastreia todos os arquivos com checksums SHA256
- ✅ **Template Engine**: Jinja2 com filtros customizados (snake_case, pascal_case, kebab_case)
- ✅ **Clean Architecture**: 4 camadas (domain/application/infrastructure/presentation)
- 🚧 **Sistema de Módulos**: Suporte para mongo, otel, events, auth, jobs (planejado)
- 🚧 **Upgrade Seguro**: Detecção de conflitos e dry-run (planejado)

---

## Arquitetura

### Clean Architecture com 4 Camadas

```
services/atlasforge/
├── src/atlasforge/
│   ├── domain/              # ✅ Lógica de negócio pura
│   │   ├── value_objects/  # Auto-validáveis, imutáveis
│   │   ├── entities/        # ProjectSpec, TemplateManifest, Module
│   │   ├── ports/           # Interfaces (dependency inversion)
│   │   └── services/        # ConflictDetector, ModuleResolver
│   │
│   ├── application/         # ✅ Casos de uso
│   │   └── use_cases/      # GenerateProjectUseCase
│   │
│   ├── infrastructure/      # ✅ Adaptadores
│   │   ├── filesystem/     # LocalFileSystemAdapter
│   │   ├── templating/     # Jinja2TemplateEngine
│   │   ├── checksum/       # SHA256ChecksumAdapter
│   │   └── persistence/    # JSONManifestRepository
│   │
│   ├── presentation/        # ✅ CLI
│   │   └── cli/            # Typer CLI
│   │
│   └── templates/           # ✅ Templates Jinja2
│       └── base/           # Template FastAPI base
│
└── tests/
    ├── unit/               # ✅ 63 testes (100% passing)
    └── integration/        # ✅ 7 testes (100% passing)
```

### Princípios Implementados

1. **Immutability**: Todas as entidades são frozen dataclasses
2. **Self-validation**: Value objects validam-se na criação
3. **Dependency Inversion**: Portas definem contratos, adapters implementam
4. **Idempotency**: Mesmo ProjectSpec sempre gera mesmo projeto

---

## Instalação

### Pré-requisitos

- Python 3.11 ou 3.12
- Poetry (gerenciador de dependências)

### Passos

```bash
# 1. Navegar para o diretório do AtlasForge
cd services/atlasforge

# 2. Instalar dependências com Poetry
poetry install

# 3. Verificar instalação
poetry run atlasforge version
```

**Saída esperada**:
```
AtlasForge version 1.0.0
```

---

## Como Usar

### Gerar um Projeto Novo

```bash
# Sintaxe básica
poetry run atlasforge generate <nome-do-projeto>

# Exemplo
poetry run atlasforge generate my-service
```

**Nota**: CLI ainda em MVP0 - comando `generate` não está totalmente funcional. Para testar a geração, use os testes de integração ou a API programática.

### API Programática (Recomendado para MVP0)

```python
from pathlib import Path
from atlasforge.domain.entities.project_spec import ProjectSpec
from atlasforge.domain.value_objects.project_name import ProjectName
from atlasforge.domain.value_objects.template_version import TemplateVersion
from atlasforge.application.use_cases.generate_project import GenerateProjectUseCase
from atlasforge.infrastructure.filesystem.local_filesystem_adapter import LocalFileSystemAdapter
from atlasforge.infrastructure.templating.jinja2_engine import Jinja2TemplateEngine
from atlasforge.infrastructure.checksum.sha256_checksum import SHA256ChecksumAdapter
from atlasforge.infrastructure.persistence.json_manifest_repository import JSONManifestRepository

# Setup
templates_dir = Path("src/atlasforge/templates")
filesystem = LocalFileSystemAdapter()
template_engine = Jinja2TemplateEngine(templates_dir)
checksum = SHA256ChecksumAdapter()
manifest_repo = JSONManifestRepository(filesystem)

# Criar use case
generate = GenerateProjectUseCase(
    filesystem=filesystem,
    template_engine=template_engine,
    checksum=checksum,
    manifest_repo=manifest_repo
)

# Criar spec
spec = ProjectSpec(
    project_name=ProjectName("my-service"),
    template_version=TemplateVersion("1.0.0"),
    modules=frozenset()
)

# Gerar projeto
result = generate.execute(spec, Path("/tmp"))

# Resultado
print(f"Success: {result.success}")
print(f"Files created: {result.total_files}")
print(f"Duration: {result.duration_seconds:.2f}s")
```

### Estrutura do Projeto Gerado

```
my-service/
├── pyproject.toml          # Configuração Poetry
├── README.md               # Documentação
├── Dockerfile              # Container
├── .gitignore              # Git ignore
├── src/
│   └── my_service/        # Snake_case para pacotes Python
│       ├── __init__.py
│       ├── domain/        # Lógica de negócio pura
│       ├── application/   # Casos de uso
│       ├── infrastructure/# Adaptadores
│       └── presentation/  # API FastAPI
│           └── api/
│               └── main.py  # Entry point
├── tests/
│   ├── conftest.py
│   └── test_api.py
└── .atlasforge/
    └── manifest.json      # Tracking de arquivos
```

### Endpoints do Projeto Gerado

- `GET /` - Root endpoint
- `GET /health` - Health check (readiness + liveness)
- `GET /metrics` - Prometheus metrics (placeholder)

---

## Como Testar

### Rodar Todos os Testes

```bash
# Todos os testes (unit + integration)
poetry run pytest

# Apenas testes unitários
poetry run pytest tests/unit/

# Apenas testes de integração
poetry run pytest tests/integration/

# Com cobertura
poetry run pytest --cov=src/atlasforge --cov-report=term-missing
```

### Testes Unitários (Value Objects)

```bash
# Testar value objects específicos
poetry run pytest tests/unit/domain/test_module_name.py -v
poetry run pytest tests/unit/domain/test_project_name.py -v
poetry run pytest tests/unit/domain/test_checksum.py -v
poetry run pytest tests/unit/domain/test_template_version.py -v
poetry run pytest tests/unit/domain/test_file_path.py -v
```

### Testes de Integração

```bash
# Teste de geração completa
poetry run pytest tests/integration/test_full_generation.py::TestFullProjectGeneration::test_generate_basic_project -v

# Teste de manifest tracking
poetry run pytest tests/integration/test_full_generation.py::TestFullProjectGeneration::test_manifest_contains_all_files -v

# Teste de validação Python
poetry run pytest tests/integration/test_full_generation.py::TestFullProjectGeneration::test_generated_project_is_valid_python -v
```

### Verificar Qualidade do Código

```bash
# Linting (Ruff)
poetry run ruff check src/

# Formatação (Black)
poetry run black src/ --check

# Type checking (MyPy)
poetry run mypy src/
```

---

## Estrutura do Projeto

### Domain Layer (Núcleo)

#### Value Objects
- **ModuleName**: Nomes de módulos (lowercase, alphanumeric, max 32 chars)
- **ProjectName**: Nomes de projetos (kebab-case, 3-63 chars)
- **Checksum**: SHA256 checksums (64 hex chars)
- **TemplateVersion**: Semantic versioning (MAJOR.MINOR.PATCH)
- **FilePath**: Paths relativos (POSIX format)

#### Entities
- **ProjectSpec**: Especificação imutável de geração (frozen dataclass)
- **TemplateManifest**: Tracking de arquivos com checksums
- **Module**: Capacidades modulares com dependências
- **GenerationResult**: Resultado de geração com metadata

#### Ports (Interfaces)
- **IFileSystemPort**: Operações de filesystem
- **ITemplateEnginePort**: Renderização de templates
- **IChecksumPort**: Cálculo de checksums
- **IManifestRepositoryPort**: Persistência de manifests
- **IModulePort**: Carregamento de módulos

#### Services
- **ConflictDetector**: Detecção de modificações de usuário
- **ModuleResolver**: Ordenação topológica de dependências

### Infrastructure Layer (Adapters)

- **LocalFileSystemAdapter**: Filesystem usando pathlib
- **Jinja2TemplateEngine**: Templates com filtros customizados
- **SHA256ChecksumAdapter**: Checksums SHA256
- **JSONManifestRepository**: Manifests em JSON

### Application Layer (Use Cases)

- **GenerateProjectUseCase**: Orquestra geração completa

### Templates

```
templates/
└── base/
    ├── template.yaml       # Metadata
    └── project/           # Arquivos do template
        ├── pyproject.toml.j2
        ├── README.md.j2
        ├── Dockerfile.j2
        ├── src/
        │   └── {{project_name|snake_case}}/
        │       ├── domain/
        │       ├── application/
        │       ├── infrastructure/
        │       └── presentation/
        │           └── api/
        │               └── main.py.j2
        └── tests/
            ├── conftest.py.j2
            └── test_api.py.j2
```

---

## Status de Implementação

### ✅ Fase 1: Fundação (COMPLETA)

- ✅ Value Objects (5/5) - 95%+ cobertura
- ✅ Entities (3/3) - ProjectSpec, TemplateManifest, Module
- ✅ Ports (5/5) - Todas as interfaces definidas
- ✅ Services (2/2) - ConflictDetector, ModuleResolver
- ✅ Exceptions (4/4) - Hierarquia completa
- ✅ **63 testes unitários** (100% passing)

### ✅ Fase 2: Geração Core (COMPLETA)

- ✅ Infrastructure Adapters (4/4)
- ✅ Template Base FastAPI
- ✅ GenerateProjectUseCase
- ✅ **7 testes de integração** (100% passing)

### 🚧 Fase 3: CLI + Módulos (PARCIAL)

- ✅ CLI básico (Typer)
- 🚧 Comandos funcionais
- ❌ Sistema de módulos completo
- ❌ Templates de módulos (mongo, otel, events, auth, jobs)

### ❌ Fase 4: Upgrade Seguro (NÃO INICIADA)

- ❌ PatchGenerator
- ❌ UpgradeProjectUseCase
- ❌ Dry-run mode

### ❌ Fase 5: Integrações (NÃO INICIADA)

- ❌ AegisIntegration
- ❌ MnemosyneIntegration
- ❌ EyeOpsIntegration

### ❌ Fase 6: Executável (NÃO INICIADA)

- ❌ PyInstaller build
- ❌ Cross-platform testing

---

## Desenvolvimento

### Adicionar Novo Value Object

```python
# src/atlasforge/domain/value_objects/my_value.py
from dataclasses import dataclass
from atlasforge.domain.exceptions.validation import ValidationException

@dataclass(frozen=True)
class MyValue:
    value: str

    def __post_init__(self) -> None:
        # Validação
        if not self.value:
            raise ValidationException("Value cannot be empty")

    def __str__(self) -> str:
        return self.value
```

### Adicionar Novo Use Case

```python
# src/atlasforge/application/use_cases/my_use_case.py
from dataclasses import dataclass
from atlasforge.domain.ports.filesystem_port import IFileSystemPort

@dataclass
class MyUseCase:
    filesystem: IFileSystemPort

    def execute(self, input: MyInput) -> MyOutput:
        # Lógica do caso de uso
        pass
```

### Adicionar Novo Template

```
templates/
└── modules/
    └── my_module/
        ├── module.yaml
        ├── dependencies.txt
        └── files/
            └── infrastructure/
                └── my_adapter.py.j2
```

---

## Métricas de Qualidade

### Testes

```
✅ 70 testes totais
   - 63 testes unitários (100% passing)
   - 7 testes de integração (100% passing)

⚡ Tempo de execução: ~2s
🧪 Cobertura geral: 54%
📊 Cobertura domain: 70%+
🎯 Cobertura use cases: 99%
```

### Código

```
📁 Arquivos Python: 50+
📝 Linhas de código: ~3,000
🔧 Dependências: 15 (prod + dev)
🐍 Python: 3.11-3.12
```

---

## Comandos Úteis

### Desenvolvimento

```bash
# Instalar dependências
poetry install

# Ativar ambiente virtual
poetry shell

# Adicionar nova dependência
poetry add <package>

# Remover dependência
poetry remove <package>
```

### Testes

```bash
# Rodar testes
poetry run pytest

# Com verbose
poetry run pytest -v

# Com coverage
poetry run pytest --cov

# Parar no primeiro erro
poetry run pytest -x

# Rodar teste específico
poetry run pytest tests/unit/domain/test_project_name.py::TestProjectName::test_valid_project_name
```

### Qualidade

```bash
# Ruff (linting)
poetry run ruff check src/
poetry run ruff check src/ --fix  # Auto-fix

# Black (formatting)
poetry run black src/
poetry run black src/ --check     # Check only

# MyPy (type checking)
poetry run mypy src/
```

### CLI

```bash
# Versão
poetry run atlasforge version

# Generate (placeholder)
poetry run atlasforge generate my-service

# Help
poetry run atlasforge --help
```

---

## Próximos Passos

### Curto Prazo (Fase 3)

1. **Implementar CLI funcional**:
   - Comando `generate` completo
   - Comando `validate`
   - Comando `inspect`

2. **Sistema de Módulos**:
   - ModulePort implementation
   - Templates para mongo, otel, events
   - Resolução de dependências

3. **Testes CLI**:
   - Testes end-to-end do CLI
   - Validação de output

### Médio Prazo (Fase 4)

1. **Upgrade Seguro**:
   - PatchGenerator completo
   - UpgradeProjectUseCase
   - Dry-run mode

2. **Conflict Detection**:
   - Detecção de modificações
   - Relatório de conflitos
   - Resolução manual/automática

### Longo Prazo (Fases 5-6)

1. **Integrações**:
   - Aegis (pre-commit + CI)
   - Mnemosyne (ADRs)
   - EyeOfHorusOps (OTEL + logging)

2. **Executável**:
   - Build com PyInstaller
   - Distribuição cross-platform
   - GitHub Actions pipeline

---

## Contribuindo

### Workflow

1. Criar branch: `feat/<area>/<descricao>`
2. Implementar com testes
3. Rodar quality checks: `ruff`, `black`, `mypy`
4. Rodar testes: `pytest`
5. Commit: `<escopo>: <ação concisa>`

### Padrões

- **Clean Architecture**: Sempre respeitar camadas
- **Type Hints**: 100% do código
- **Testes**: Cobertura mínima 80%
- **Immutability**: Preferir frozen dataclasses

---

## Licença

Este projeto é parte do **Atlas Platform** - plataforma interna de desenvolvimento.

---

## Suporte

- **Documentação**: `/home/gabriela/workspace/atlas-forge/CLAUDE.md`
- **Plano**: `/home/gabriela/.claude/plans/transient-knitting-fountain.md`
- **Issues**: (GitHub quando disponível)

---

**Última atualização**: 2025-12-14
**Versão**: 1.0.0 (MVP0 → MVP1 em progresso)
**Status**: ✅ Fase 1-2 completas, 🚧 Fase 3 em andamento
