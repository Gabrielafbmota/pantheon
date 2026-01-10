# Infra • Fluxo 02 — GitHub Actions CI

## Objetivo
Adicionar pipeline de CI para lint/test/build.

## Entradas
- Python: ruff + pytest
- Docker build multi-arch opcional

## Saídas esperadas
- Workflow `ci.yml`
- Cache de deps

## Restrições / Regras
- Fail-fast
- Sem segredos no repo

## Tarefas
1) Criar workflow
2) Adicionar ruff config
3) Rodar pytest

## Critérios de pronto
- Pipeline verde
- Artefatos gerados quando necessário
