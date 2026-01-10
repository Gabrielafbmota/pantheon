# Backend • Fluxo 05 — Sessões (`/reading/sessions/start|end`)

## Objetivo
Iniciar e finalizar sessões de leitura para alimentar métricas.

## Entradas
- start: book_id, device, source
- end: session_id

## Saídas esperadas
- Persistência em `reading_sessions`
- duration_seconds calculado
- Testes: start/end, end idempotente

## Restrições / Regras
- Uma sessão ativa por book/user (opcional)
- UTC-aware
- Não confiar no client clock sem validação

## Tarefas
1) Use cases StartSession/EndSession
2) Repo + índices
3) Routes
4) Testes

## Critérios de pronto
- duration calculada corretamente
- end repetido não quebra
