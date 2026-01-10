# Backend • Fluxo 03 — Importação do JSON (`POST /import/books` + script CLI)

## Objetivo
Implementar importação de `codexathenae.books.json` via endpoint protegido e também via script CLI (idempotente).

## Entradas
- Arquivo JSON local (CLI)
- Upload opcional via API

## Saídas esperadas
- Import summary: total/inserted/updated/skipped
- Logs por livro (isbn/title)
- Testes de importação (amostra pequena)

## Restrições / Regras
- Preservar dados existentes
- Upsert por ISBN; sem ISBN, por fingerprint
- Nunca apagar livros

## Tarefas
1) Criar use case ImportBooksFromJson
2) Implementar script `scripts/import_books.py`
3) Implementar endpoint `/import/books` (admin)
4) Validar schema do JSON
5) Testes: itens válidos/ inválidos / duplicados

## Critérios de pronto
- Import repete sem duplicar
- Relatório final correto
- Erros não interrompem lote (registrar e seguir)
