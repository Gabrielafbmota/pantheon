# 02 — Roadmap (MVPs e evolução)

## MVP1 — Fundação (produto usável)
### Pantheon
- Catálogo de sistemas + registry (metadados básicos)
- Catálogo de eventos e versionamento (documentação + validação simples)
- Convenções globais (logging, tracing, IDs de correlação)

### AtlasForge
- CLI completo: gerar projeto + módulos + upgrade (dry-run)
- Templates híbridos (estrutura em código + conteúdo em templates)
- Geração de configs de integração (placeholders reais)

### Aegis
- Pre-commit rápido (lint/format/secrets) + CI gate
- Modelo de Findings (severity, baseline, waivers com expiração)
- Emissão de eventos de violação

### Mnemosyne
- API de ingestão básica + persistência MongoDB
- Pipeline: fetch/normalize/enrich/persist/index (texto)
- Deduplicação por fingerprint e auditoria por run

### EyeOfHorusOps
- Coleta/visualização de logs por serviço
- Health + status board
- Incidentes manuais + timeline

## MVP2 — Integração e governança
- Eventos assinados/validados por schema
- Dashboards unificados (quality + incidents + knowledge)
- Waivers e baselines com governança
- Reprocessamento e reindexação robustos (Mnemosyne)
- Runbooks “approve-to-run” (EyeOfHorusOps)

## MVP3 — Maturidade e IA assistiva
- Busca híbrida + embeddings (Mnemosyne)
- RAG com evidência e citações
- Auto-remediação limitada (allowlist + cooldown + auditoria)
- Recomendação de ações (quality/ops/knowledge) com trilha de auditoria
