# Backend • Fluxo 04 — Progresso de leitura (`POST /reading/progress`)

## Objetivo
Persistir progresso de leitura por usuário+livro (idempotente) para EPUB/PDF.

## Entradas
- Payload: book_id, percent, epub_cfi?, pdf_page?, pdf_scroll_y?
- Auth: user_id no token

## Saídas esperadas
- Upsert em `reading_progress`
- Resposta com estado salvo
- Testes cobrindo validações e upsert

## Restrições / Regras
- percent entre 0 e 100
- updated_at UTC-aware
- Conflito: server wins por updated_at (ou aceitar client timestamp validado)

## Tarefas
1) DTOs + validações
2) Use case UpsertReadingProgress
3) Repo Motor com índice único (user_id, book_id)
4) Route + auth dependency
5) Testes

## Critérios de pronto
- Upsert consistente
- Índice único criado
- Validações corretas
