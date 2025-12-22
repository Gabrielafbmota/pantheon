# 11 — Modelo de Dados (MongoDB) + Índices sugeridos

> Objetivo: suportar auditoria, idempotência e crescimento contínuo.

## Coleções (mínimo)

### `pantheon.services`
- `_id` (uuid)
- `name`
- `owner`
- `envs` (prod/stage/dev)
- `endpoints` (api/base_url)
- `createdAt`, `updatedAt`
**Índices**
- `name` unique
- `owner`

### `pantheon.event_catalog`
- `_id`
- `eventName` (ex: `quality.v1.violation_detected`)
- `schemaVersion`
- `jsonSchema`
- `examples`
**Índices**
- `eventName` unique
- `eventName + schemaVersion` (se versionar separado)

### `aegis.scan_runs`
- `_id` (runId)
- `repo`, `ref`, `commitSha`
- `startedAt`, `finishedAt`
- `status`
**Índices**
- `repo + commitSha`
- `finishedAt` desc

### `aegis.findings`
- `_id`
- `runId`
- `fingerprint`
- `severity`
- `path`, `line`
- `ruleId`
**Índices**
- `runId`
- `fingerprint`
- `repo + fingerprint` (se armazenar repo)

### `mnemosyne.knowledge_entries`
- `_id` (entryId)
- `fingerprint`
- `source`
- `content`
- `tags`
- `version`
- `createdAt`
**Índices**
- `fingerprint`
- `tags`
- `createdAt`

### `mnemosyne.ingestion_runs`
- `_id` (runId)
- `sourceId`
- `startedAt`, `finishedAt`
- `status`
**Índices**
- `sourceId + startedAt`

### `eyeops.incidents`
- `_id` (incidentId)
- `service`
- `severity`
- `status`
- `openedAt`, `closedAt`
**Índices**
- `service + openedAt`
- `status`
