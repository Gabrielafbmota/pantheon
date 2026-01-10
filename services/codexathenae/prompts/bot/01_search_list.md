# Bot • Fluxo 01 — Buscar/Listar livros

## Objetivo
Implementar comandos para buscar e listar livros usando apenas a API.

## Entradas
- Comandos: /buscar <q>, /listar (pag)
- API: GET /books?q=

## Saídas esperadas
- Resposta formatada (título + autor + id)
- Paginação simples
- Tratamento de erro

## Restrições / Regras
- Bot NÃO acessa DB
- Timeouts e retries com backoff
- Não logar dados sensíveis

## Tarefas
1) Cliente httpx
2) Handlers python-telegram-bot
3) Formatação
4) Testes (unittest) com httpx mock

## Critérios de pronto
- Funciona com API offline/online
- Mensagens claras
