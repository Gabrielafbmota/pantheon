Você é um assistente especialista em desenvolvimento backend
(Python, FastAPI, Clean Architecture, DevOps e automação de projetos).

Quero implementar um sistema chamado AtlasForge.

Objetivo:
Criar um gerador de projetos “zero-click”, capaz de criar e atualizar
projetos backend padronizados, prontos para produção, com governança,
qualidade e observabilidade desde o primeiro commit.

Papel do sistema:
- Gerar projetos FastAPI com Clean Architecture
- Eliminar decisões repetitivas de setup
- Garantir que todo projeto já nasça integrado ao Aegis, Mnemosyne e EyeOfHorusOps
- Permitir upgrades seguros de projetos existentes

Stack:
- Backend: Python
- CLI principal (obrigatório)
- API FastAPI (opcional, para uso remoto)
- Arquitetura: Clean Architecture
- Integrações: GitHub, Docker, GitHub Actions
- Observabilidade: OpenTelemetry (logs sempre ativos)

Requisitos obrigatórios:
- Estrutura fixa por camadas: domain / application / infrastructure / presentation
- Manifesto do template (template_name, template_version, módulos ativados)
- Geração idempotente (mesmo input → mesmo output)
- Upgrade por patch sets com dry-run e relatório de conflitos
- Nenhum arquivo do usuário pode ser sobrescrito silenciosamente

Funcionalidades principais:
- Gerar novo projeto FastAPI padrão
- Ativar módulos via ProjectSpec (Mongo, eventos, jobs, auth, OTEL)
- Injetar:
  - pipeline CI padrão
  - hooks do Aegis
  - padrões de logging e tracing
- Atualizar projetos existentes mantendo customizações

Integrações:
- Aegis: hooks de pre-commit e workflow CI
- Mnemosyne: publicação de ADRs e decisões como KnowledgeEntry
- EyeOfHorusOps: labels, logs estruturados e tracing padrão

Requisitos não funcionais:
- Determinístico
- Testável
- Auditável
- Compatível com ARM64
- Documentado

Siga este fluxo:
1. Propor estrutura de pastas.
2. Definir ProjectSpec e Template Manifest.
3. Implementar geração de projeto (MVP1) com testes.
4. Implementar upgrade seguro.
5. Explicar decisões técnicas e trade-offs.
