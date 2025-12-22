# 04 — Backlog Scrum (Épicos, histórias, critérios)

## Épico: Pantheon Orchestrator
### História: Catálogo de sistemas
**Como** engenheira, **quero** registrar sistemas com metadados (nome, owner, envs) **para** ter visão unificada.
**Aceite**
- CRUD básico via API
- Auditoria de alterações
- Versionamento de contrato da API

### História: Catálogo de eventos
**Aceite**
- Lista de eventos e schemas por versão
- Validação de payloads no publish (mínimo)

---

## Épico: AtlasForge
### História: Gerar projeto FastAPI padrão
**Aceite**
- Estrutura Clean Architecture
- Config 12-factor
- Dockerfile + GH Actions
- Instrumentação OTEL mínima

### História: Upgrade seguro (dry-run)
**Aceite**
- Relatório de diffs
- Sem sobrescrever customizações sem conflito explícito

---

## Épico: Aegis
### História: Pre-commit rápido
**Aceite**
- Tempo alvo baixo (rápido)
- Relatório local amigável

### História: CI gate por delta
**Aceite**
- Baseline suportado
- Bloqueio apenas de novos findings

---

## Épico: Mnemosyne
### História: Ingestão e deduplicação
**Aceite**
- Fingerprint determinístico
- Run auditável (runId)

---

## Épico: EyeOfHorusOps
### História: Logs por serviço
**Aceite**
- Filtrar por service/env
- Paginação e janela temporal
