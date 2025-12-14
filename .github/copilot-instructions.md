<!-- Instruções curtas e acionáveis para agentes (Copilot/GitHub AI) trabalhando neste repositório -->
# Instruções para Copilot — Atlas Complete Kit (conciso)

Obrigado por ajudar com o Atlas. Abaixo estão fatos e ações específicos do projeto que tornam você imediatamente produtivo.

## Visão geral (ler primeiro)
- Este repositório define a plataforma interna **Atlas**; o componente principal aqui é **AtlasForge** (`services/atlasforge`) — um gerador zero-click de projetos FastAPI seguindo Clean Architecture.
- Restrições principais: Python 3.11+, Poetry, Clean Architecture (domain/application/infrastructure/presentation), eventos versionados (ex.: `user.v1.created`). Consulte `.claude/CLAUDE.md` para a racional completa.

## Locais-chave para leitura (ordem recomendada)
- `.claude/CLAUDE.md` — arquitetura canônica, convenções e regras da plataforma
- `services/atlasforge/IMPLEMENTATION.md` — notas de implementação, comandos e exemplos detalhados
- `services/atlasforge/README.md` — comandos rápidos e status do serviço
- `src/atlasforge/` — código fonte (domain, application, infrastructure, presentation)
- `tests/` — testes unitários e de integração; cobertura HTML em `services/atlasforge/htmlcov/`

## Fluxos e comandos de desenvolvimento (copiar/colar)
- Instalar dependências: `cd services/atlasforge && poetry install`
- Rodar todos os testes: `poetry run pytest`
- Rodar um teste unitário específico: `poetry run pytest tests/unit/path/to_test.py::TestClass::test_name -q`
- Rodar testes de integração: `poetry run pytest tests/integration/ -q`
- Type-check: `poetry run mypy src/`
- Lint & format: `poetry run ruff check src/` e `poetry run black src/ --check`
- Rodar CLI (parcial): `poetry run atlasforge generate <nome>` (CLI em MVP, prefira uso programático para testes)
- Rodar app FastAPI gerado: `uvicorn src.<service>.api.main:app --reload --port 8000`

## Convenções e padrões específicos do projeto
- Clean Architecture obrigatória: não coloque lógica de negócio em `api/`; use `domain/`, `application/`, `infrastructure/adapters/` e `ports` para inversão de dependência.
- Value objects são imutáveis e validam-se na construção (veja `src/atlasforge/domain/value_objects/*`). Exemplos: `ProjectName`, `ModuleName`, `TemplateVersion`.
- Convenção de nomes: `ProjectName` = kebab-case (3–63 chars); pacotes Python = snake_case.
- `ModuleName`: somente lower alphanumeric, até 32 chars.
- Templates Jinja2 com filtros customizados (`snake_case`, `pascal_case`, `kebab_case`) em `src/atlasforge/templates/`.
- Projects gerados incluem `.atlasforge/manifest.json` com checksums SHA256 (use `JSONManifestRepository`).

## Pontos de atenção & integrações
- Observabilidade: **todos** os serviços devem expor `GET /health` e `GET /metrics` e ter instrumentação OpenTelemetry.
- Persistência: padrão MongoDB; `MONGO_URI` via variável de ambiente.
- Integrações externas (placeholders) — Aegis, Mnemosyne, EyeOfHorusOps: confirmar contrato antes de implementar.

> Observação importante: **sempre responda ao autor e gere documentação em Português (pt-br)**, salvo indicação explícita em contrário.

## Exemplos úteis (copiar/colar)

1) Value Object (exemplo mínimo)

```python
from dataclasses import dataclass
from atlasforge.domain.exceptions.validation import ValidationException

@dataclass(frozen=True)
class ModuleName:
	value: str

	def __post_init__(self) -> None:
		if not self.value.isalnum() or not self.value.islower() or len(self.value) > 32:
			raise ValidationException("ModuleName inválido: deve ser lowercase alphanumeric, max 32 chars")

	def __str__(self) -> str:
		return self.value
```

2) Use Case (esqueleto)

```python
from dataclasses import dataclass
from atlasforge.domain.ports.filesystem_port import IFileSystemPort

@dataclass
class MyUseCase:
	filesystem: IFileSystemPort

	def execute(self, input_data):
		# lógica do caso de uso
		pass
```

3) Uso programático de `GenerateProjectUseCase` (teste rápido)

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

templates_dir = Path("src/atlasforge/templates")
filesystem = LocalFileSystemAdapter()
template_engine = Jinja2TemplateEngine(templates_dir)
checksum = SHA256ChecksumAdapter()
manifest_repo = JSONManifestRepository(filesystem)

generate = GenerateProjectUseCase(
	filesystem=filesystem,
	template_engine=template_engine,
	checksum=checksum,
	manifest_repo=manifest_repo
)

spec = ProjectSpec(
	project_name=ProjectName("my-service"),
	template_version=TemplateVersion("1.0.0"),
	modules=frozenset()
)

result = generate.execute(spec, Path("/tmp"))
print(result)
```

4) Checklist de PR / CI (exemplos de comandos a incluir)

```bash
# Executar testes
poetry run pytest

# Lint e formatação
poetry run ruff check src/
poetry run black src/ --check

# Type checking
poetry run mypy src/

# Cobertura (opcional)
poetry run pytest --cov=src/atlasforge --cov-report=term-missing
```

### Checklist de PR / CI (detalhado) ✅

- Obrigatório em cada PR:
	- Rodar todos os testes (unit + integration): `poetry run pytest`
	- Rodar lint e format-check: `poetry run ruff check src/` e `poetry run black src/ --check`
	- Rodar type-check: `poetry run mypy src/`
	- Verificar cobertura mínima (quando aplicável) e não reduzir coverage sem justificativa
	- Executar testes específicos de integração para mudanças que afetam geração/template
	- Atualizar `services/<servico>/implementacoes/*.md` quando houver mudança de comportamento ou contrato

- Recomendações de revisão:
	- Peça revisão de alguém familiar com `domain/` e `application/` se houver lógica de negócio
	- Peça revisão de infraestrutura/ops para mudanças em observabilidade ou deployment

- Exemplo mínimo de GitHub Actions job (`.github/workflows/ci.yml`):

```yaml
name: CI

on: [push, pull_request]

jobs:
	test:
		runs-on: ubuntu-latest
		strategy:
			matrix:
				python: [3.11]
		steps:
			- uses: actions/checkout@v4
			- name: Set up Python
				uses: actions/setup-python@v4
				with:
					python-version: ${{ matrix.python }}
			- name: Install dependencies
				run: |
					pip install poetry
					poetry install -n
			- name: Lint
				run: poetry run ruff check src/
			- name: Format check
				run: poetry run black src/ --check
			- name: Type check
				run: poetry run mypy src/
			- name: Tests
				run: poetry run pytest -q
```

### Exemplo de teste de integração — geração básica 🔧

Coloque este exemplo em `tests/integration/test_full_generation.py`. O teste demonstra o uso programático do `GenerateProjectUseCase` e valida o resultado básico (sucesso e presença do manifest e de arquivos gerados).

```python
import tempfile
from pathlib import Path

from atlasforge.domain.entities.project_spec import ProjectSpec
from atlasforge.domain.value_objects.project_name import ProjectName
from atlasforge.domain.value_objects.template_version import TemplateVersion
from atlasforge.application.use_cases.generate_project import GenerateProjectUseCase
from atlasforge.infrastructure.filesystem.local_filesystem_adapter import LocalFileSystemAdapter
from atlasforge.infrastructure.templating.jinja2_engine import Jinja2TemplateEngine
from atlasforge.infrastructure.checksum.sha256_checksum import SHA256ChecksumAdapter
from atlasforge.infrastructure.persistence.json_manifest_repository import JSONManifestRepository


class TestFullProjectGeneration:
		def test_generate_basic_project(self, tmp_path: Path):
				templates_dir = Path("src/atlasforge/templates")
				filesystem = LocalFileSystemAdapter()
				template_engine = Jinja2TemplateEngine(templates_dir)
				checksum = SHA256ChecksumAdapter()
				manifest_repo = JSONManifestRepository(filesystem)

				generate = GenerateProjectUseCase(
						filesystem=filesystem,
						template_engine=template_engine,
						checksum=checksum,
						manifest_repo=manifest_repo,
				)

				spec = ProjectSpec(
						project_name=ProjectName("my-service"),
						template_version=TemplateVersion("1.0.0"),
						modules=frozenset(),
				)

				# Use tmp_path (pytest fixture) as output
				result = generate.execute(spec, tmp_path)

				assert result.success is True
				assert result.total_files > 0

				# Verifica que o manifest foi criado
				manifest_path = tmp_path / ".atlasforge" / "manifest.json"
				assert manifest_path.exists()

				# Verifica arquivo chave do projeto gerado
				assert (tmp_path / "my-service" / "pyproject.toml").exists()

```

Comando para rodar apenas esse teste:

```bash
poetry run pytest tests/integration/test_full_generation.py::TestFullProjectGeneration::test_generate_basic_project -q
```

## Quando pedir orientação antes de mudar
- Mudanças em nomes de eventos, esquemas de eventos ou contratos públicos
- Troca de banco, modelo de autenticação, ou alterações que afetem múltiplos serviços

---
Se algo estiver incompleto ou você quiser exemplos adicionais (ex.: geração de template de módulo, exemplo de PR completo), diga-me e eu itero nesta mesma base.
