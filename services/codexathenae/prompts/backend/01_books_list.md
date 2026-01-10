# Backend • Fluxo 01 — Listagem de livros (`GET /books`)

## Objetivo
Implementar listagem paginada e filtrável de livros, preservando a collection `books` e sem acoplar leitura.

## Entradas
- Query params: `page`, `limit`, `q`, `author`, `genre`, `has_isbn`
- Headers: `X-Request-Id` opcional

## Saídas esperadas
- Endpoint FastAPI + caso de uso `ListBooks`
- Repository Motor com índices
- Testes `pytest` cobrindo paginação e filtros

## Restrições / Regras
- Clean Architecture (domain/application/infrastructure/presentation)
- Pydantic v2
- Evitar N+1
- Segurança: validação de parâmetros e limites máximos (ex.: limit<=100)

## Tarefas
1) Criar DTOs de request/response
2) Implementar use case
3) Implementar repository Motor
4) Criar rota e dependências
5) Adicionar índices recomendados e docs
6) Testes unit/integration (mock + mongodb fixture)

## Critérios de pronto
- Passa em `pytest`
- Retorna `items`, `page`, `limit`, `total`
- Performance aceitável em 10k livros

## Índices recomendados
- `isbn` (sparse + unique)
- `_fingerprint`
- `_title_norm`
- `authors`
- `genre`
- `created_at`
- Índice de texto em `title`, `description`, `authors` para busca simples
