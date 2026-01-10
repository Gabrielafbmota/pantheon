# Bot • Fluxo 03 — Detalhes do livro

## Objetivo
Mostrar detalhes do livro pelo ID.

## Entradas
- Comando: /detalhes <id>
- API: GET /books/{id}

## Saídas esperadas
- Mensagem formatada + link (se houver)
- Fallback para descrição truncada

## Restrições / Regras
- Limitar tamanho
- Sanitizar markdown

## Tarefas
1) Handler
2) Render
3) Testes

## Critérios de pronto
- Sem erros de formatação
- Respeita limites do Telegram
