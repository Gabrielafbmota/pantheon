# 05 — Requisitos Não Funcionais (NFRs)

## Segurança (OWASP + plataforma)
- Secrets apenas por env (nunca hardcode)
- Sanitização de logs (redação de tokens/URI)
- Dependências auditáveis (supply chain)
- Privilégio mínimo (IAM/roles) quando em AWS

## Observabilidade
- Logs estruturados (JSON) em stdout
- Correlation ID em todas as requisições/eventos
- Tracing distribuído via OpenTelemetry
- Métricas RED (Rate, Errors, Duration) por serviço

## Confiabilidade
- Idempotência em ingestão e eventos
- Reprocessamento suportado (Mnemosyne)
- Retentiva configurável (logs e knowledge raw)

## Escalabilidade
- Processamento assíncrono quando aplicável
- Particionamento por serviço/run/time em coleções e índices

## Auditoria
- Trilhas de auditoria para:
  - geração/upgrade (AtlasForge)
  - scans/findings/waivers (Aegis)
  - ingest runs (Mnemosyne)
  - incidentes/runbooks (EyeOfHorusOps)
