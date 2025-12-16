# 07 — AtlasForge

## Propósito
Gerar projetos backend “nascidos corretos”: Clean Architecture, 12-factor, OTEL e CI/CD.

## Decisões de implementação (confirmadas)
- Local: `services/atlasforge/`
- Dependências: Poetry
- MVP1: CLI completo (geração + módulos + upgrade)
- Integrações: placeholders reais (Aegis/Mnemosyne/EyeOfHorusOps)
- Templates: híbrido (estrutura em código + conteúdo em templates)

## Clean Architecture
- domain: ProjectSpec, TemplateManifest, PatchSet
- application: GenerateProject, UpgradeProject
- infrastructure: filesystem, templating, git adapter
- presentation: CLI

## MVP1
- `init`: gerar projeto FastAPI padrão
- `add module`: ativar módulos (mongo, events, otel, aegis)
- `upgrade`: aplicar patchset com dry-run
- `report`: report de diffs e versões

## Contratos emitidos
- `project.v1.generated`
- `project.v1.upgraded`
- `project.v1.module_enabled`
