# Backend • Fluxo 06 — Highlights (`POST /highlights`, `GET /highlights/{book_id}`)

## Objetivo
Criar e listar highlights com locator EPUB/PDF, desacoplados do Book.

## Entradas
- Payload: book_id, text, note?, locator_type, locator_value

## Saídas esperadas
- Persistência em `highlights`
- Listagem paginada
- Testes: criação, validação locator_type

## Restrições / Regras
- locator_type ∈ {epub_cfi, pdf_page}
- text tamanho máximo (ex.: 10k)
- Sanitização básica

## Tarefas
1) DTOs
2) Use case CreateHighlight/ListHighlights
3) Repo
4) Routes
5) Testes

## Critérios de pronto
- CRUD básico funcionando
- Protegido por auth
