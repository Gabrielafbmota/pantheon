# 07 — AtlasForge

## Propósito
Gerar projetos backend “nascidos corretos”: Clean Architecture, 12-factor, OTEL e CI/CD.

## Decisões de implementação (confirmadas)
- Local: `services/atlasforge/`
- Dependências: Poetry
- MVP1: CLI completo (geração + módulos + upgrade)
- Integrações: placeholders reais (Aegis/Mnemosyne/EyeOfHorusOps)
- Templates: híbrido (estrutura em código + conteúdo em templates)

## Estado atual (MVP)
| Área                | Status        | Observações                                         |
|---------------------|---------------|-----------------------------------------------------|
| CLI (generate/inspect/validate) | ✅ Completo   | Idempotente, manifest com checksums                |
| Módulos base        | ✅ Mongo, OTEL, Events, Auth, Jobs | Renderização real + testes de geração            |
| Clean Architecture  | ✅            | 4 camadas, separação rígida                         |
| Instalação global   | ✅            | pipx / install.sh / Makefile                        |
| Integrações Atlas   | 🚧 Parcial    | Placeholders para Aegis/Mnemosyne/EyeOfHorusOps     |
| Upgrade seguro      | ❌ Pendente    | Patch set + dry-run ainda não implementados         |

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

## Próximos passos
- Finalizar upgrade seguro (diff/patch/dry-run).
- Adicionar integração de eventos reais com Pantheon/Mnemosyne.
- Expandir módulos (ex.: cache, jobs distribuídos) e cobertura de testes >80%.
