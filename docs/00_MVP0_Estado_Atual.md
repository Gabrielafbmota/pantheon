# 00 — MVP0: Estado Atual

## Estado atual
A plataforma **PANTHEON** está em **MVP0**: há documentação, padrões e decisões, mas **nenhum serviço implementado**.

## Objetivo do MVP0
- Reduzir risco técnico antes do código
- Consolidar arquitetura e contratos
- Definir NFRs e padrões de governança
- Preparar execução incremental (MVP1)

## Stack alvo (padrão do ecossistema)
- Python + FastAPI
- Clean Architecture (domain/application/infrastructure/presentation)
- MongoDB (Motor async)
- Docker
- GitHub Actions
- OpenTelemetry (logs, traces, métricas)

## Princípios
- 12-Factor App (config por env, logs em stdout, processos stateless)
- Segurança by-default (OWASP, segredos fora do repositório)
- Idempotência e auditoria como requisitos, não “nice-to-have”
