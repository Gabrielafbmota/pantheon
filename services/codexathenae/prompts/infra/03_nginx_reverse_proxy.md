# Infra • Fluxo 03 — Nginx reverse proxy (subpath)

## Objetivo
Configurar Nginx para servir frontend e API em subpaths no Pi (ex.: /codexathenae).

## Entradas
- Domínio/Tailscale
- Subpaths

## Saídas esperadas
- Config Nginx com headers e CORS
- Websocket se necessário

## Restrições / Regras
- Segurança: headers, rate limit
- TLS se houver

## Tarefas
1) Criar server block
2) Proxy_pass API
3) Static frontend
4) Testar

## Critérios de pronto
- Rotas funcionam com basename
- Sem mixed content
