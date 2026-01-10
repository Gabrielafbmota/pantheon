# Frontend • Tela 02 — Biblioteca (grid de cards)

## Objetivo
Implementar grid paginado com busca e filtros.

## Entradas
- API: GET /books?page&limit&q&author&genre
- UI: search input + filtros

## Saídas esperadas
- Grid de cards (imagem, título, autor)
- Paginação
- Navegação para detalhes

## Restrições / Regras
- Debounce na busca
- Imagem com fallback
- Persistir filtros no URL (react-router-dom)

## Tarefas
1) Criar store `booksStore`
2) Hook `useBooksList`
3) Componentes Card/Grid
4) Paginação e querystring

## Critérios de pronto
- UX fluida
- Sem chamadas duplicadas
