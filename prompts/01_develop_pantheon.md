# Prompt — Desenvolver Pantheon (Orquestrador)

Você é um assistente especialista em plataformas internas (Python/FastAPI, Clean Architecture, MongoDB, eventos).

Quero implementar o **Pantheon** como orquestrador do ecossistema (AtlasForge/Aegis/Mnemosyne/EyeOfHorusOps).

Requisitos:
- Sem monólito: apenas catálogo/governança/contratos
- Catálogo de serviços e eventos versionados
- Validação mínima de payload por JSON Schema
- Auditoria de alterações
- Observabilidade (OTEL) e endpoints /health e /metrics

Siga o fluxo:
1) Propor estrutura de pastas (Clean Architecture).
2) Definir entidades e ports.
3) Implementar MVP1 incrementalmente com testes.
4) Explicar trade-offs e riscos.
