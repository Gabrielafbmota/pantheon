# Frontend • Tela 04 — Reader EPUB (Kallioreader)

## Objetivo
Implementar reader EPUB com epub.js, persistindo progresso offline-first.

## Entradas
- Arquivo EPUB via URL/file_id (definir)
- Eventos: locationChanged -> cfi+percent

## Saídas esperadas
- Reader com controles
- Persistência IndexedDB
- Sync POST /reading/progress

## Restrições / Regras
- Não travar UI
- Evitar flood: throttle 1-3s
- Resolver conflitos por updated_at

## Tarefas
1) Integrar epub.js
2) Criar `progressStore` + IndexedDB adapter
3) SyncQueue
4) API client
5) UX: fonte/tema

## Critérios de pronto
- Progresso salva local e sincroniza
- Retoma posição
