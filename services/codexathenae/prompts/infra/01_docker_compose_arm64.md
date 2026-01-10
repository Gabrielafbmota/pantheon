# Infra • Fluxo 01 — Docker Compose arm64 (Raspberry Pi)

## Objetivo
Montar um docker-compose para backend+frontend e Mongo opcional, compatível com Raspberry Pi.

## Entradas
- Variáveis `.env`
- Ports 8000/5173

## Saídas esperadas
- `docker-compose.yml` + instruções
- Healthchecks
- Volumes

## Restrições / Regras
- Sem imagens x86-only
- Preferir imagens oficiais multi-arch
- Logs stdout

## Tarefas
1) Compose com profiles (mongo local vs atlas)
2) Healthchecks
3) Network isolada

## Critérios de pronto
- `docker compose up` funciona no Pi
- Backend sobe saudável
