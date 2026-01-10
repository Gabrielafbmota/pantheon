# Bot • Fluxo 02 — Adicionar livro por ISBN

## Objetivo
Adicionar livro por ISBN via API (que faz dedupe/enrichment).

## Entradas
- Comando: /adicionar_isbn 978...
- API: POST /books

## Saídas esperadas
- Confirmação com título e id
- Se duplicado, avisar

## Restrições / Regras
- Validar ISBN (10/13)
- Não floodar API

## Tarefas
1) Validação
2) Request POST
3) Mensagens
4) Testes

## Critérios de pronto
- Não duplica
- Mensagens úteis
