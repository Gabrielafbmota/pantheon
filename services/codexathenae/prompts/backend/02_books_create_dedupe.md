# Backend • Fluxo 02 — Criar livro com deduplicação (`POST /books`)

## Objetivo
Implementar criação de livro com deduplicação por ISBN e fallback por fingerprint (title+authors).

## Entradas
- Payload BookCreate
- Fonte: manual/bot/import

## Saídas esperadas
- Persistência idempotente: se existir, retorna existente
- Logs estruturados
- Testes cobrindo dedupe

## Restrições / Regras
- `Book` é catálogo (sem estado de leitura)
- Normalização: trim, lower, remover pontuação para fingerprint
- Upsert seguro (transacional quando possível)

## Tarefas
1) Funções de normalização no domain
2) Use case CreateBook
3) Repo: `find_by_isbn`, `find_by_fingerprint`, `upsert`
4) Route + validation
5) Testes (isbn dup, fingerprint dup, novo livro)

## Critérios de pronto
- 201 quando novo, 200 quando duplicado
- `id` sempre UUID
- `created_at/updated_at` UTC-aware
