# 12 — Interfaces e Contratos entre Sistemas

## Padrão de evento (envelope)
- `id` (uuid)
- `name` (string)
- `version` (int ou string semver)
- `occurredAt` (UTC ISO8601)
- `producer` (service name)
- `correlationId`
- `payload` (json)
- `schemaRef` (opcional)

## Contratos principais (exemplos)
- AtlasForge → Pantheon/Mnemosyne:
  - `project.v1.generated`
  - `project.v1.upgraded`
- Aegis → Pantheon/Mnemosyne/EyeOps:
  - `quality.v1.scan_completed`
  - `quality.v1.violation_detected`
- EyeOps → Mnemosyne:
  - `incident.v1.opened`
  - `incident.v1.closed`
- Mnemosyne → Pantheon:
  - `knowledge.v1.ingested`

## APIs (MVP1) — sugestão mínima
- Pantheon
  - `GET /services`
  - `POST /services`
  - `GET /events`
- Mnemosyne
  - `POST /ingest`
  - `GET /search?q=...`
- EyeOps
  - `GET /services/{name}/logs`
  - `POST /incidents`
- Aegis (CLI/CI primário; API opcional)
