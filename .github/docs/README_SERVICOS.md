# Guia Rápido dos Serviços (Aegis, AtlasForge, Mnemosyne, EyeOfHorusOps)

## Aegis
- **Run**: `cd services/aegis && poetry install && poetry run aegis scan --repo . --output -`
- **.env** (exemplo):
  ```
  MONGO_URI=mongodb://localhost:27017
  ```
- **Curl** (scan via CLI somente; persist):
  ```bash
  aegis scan --repo . --commit HEAD --output report.json
  aegis persist --input-file report.json --mongo-uri "$MONGO_URI"
  ```

## AtlasForge
- **Run**: `cd services/atlasforge && poetry install && poetry run atlasforge generate my-service --modules mongo,otel,auth,jobs`
- **.env** (para projetos gerados):
  ```
  API_KEY=change-me
  MONGO_URI=mongodb://localhost:27017
  OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
  ```
- **Curl** (projeto gerado padrão):
  ```bash
  curl http://localhost:8000/health
  ```

## Mnemosyne
- **Run**: `cd services/mnemosyne && poetry install && MNEMO_DISABLE_OTEL=1 uvicorn mnemosyne.presentation.api.main:app --reload`
- **.env**:
  ```
  MNEMO_PERSISTENCE=mongo   # ou memory
  MNEMO_MONGO_URI=mongodb://localhost:27017
  MNEMO_MONGO_DB=mnemosyne
  MNEMO_S3_BUCKET=mnemo-raw   # opcional
  MNEMO_API_KEY=change-me
  MNEMO_DISABLE_OTEL=1        # desliga OTEL no dev
  ```
- **Curl**:
  ```bash
  curl -X POST http://localhost:8000/ingestions \
    -H "Content-Type: application/json" -H "X-API-Key: $MNEMO_API_KEY" \
    -d '[{"external_id":"1","source":{"id":"aegis","name":"Aegis","type":"aegis"},"content":"Incident A","tags":[{"key":"sev1"}],"taxonomy":["incidents"]}]'

  curl "http://localhost:8000/search?text=Incident&taxonomy=incidents" -H "X-API-Key: $MNEMO_API_KEY"
  ```

## EyeOfHorusOps
- **Run**: `cd services/eyeofhorusops && poetry install && EYEOPS_DISABLE_OTEL=1 uvicorn eyeofhorusops.presentation.api.main:app --reload`
- **.env**:
  ```
  EYEOPS_PERSISTENCE=mongo   # ou memory
  MONGO_URI=mongodb://localhost:27017
  MONGO_DB=eyeofhorusops
  LOKI_URL=http://localhost:3100
  EYEOPS_API_KEY=change-me
  EYEOPS_DISABLE_OTEL=1
  ```
- **Curl**:
  ```bash
  # Registrar serviço
  curl -X POST http://localhost:8000/services -H "Content-Type: application/json" \
    -H "X-API-Key: $EYEOPS_API_KEY" -H "X-Roles: ops" \
    -d '{"id":"svc-1","name":"payments","env":"prod","owners":["sre@acme"]}'

  # Ingerir log
  curl -X POST http://localhost:8000/logs/svc-1 -H "Content-Type: application/json" \
    -H "X-API-Key: $EYEOPS_API_KEY" -H "X-Roles: service" \
    -d '{"message":"restart","level":"info","trace_id":"t-1"}'

  # Criar incidente e executar runbook
  curl -X POST http://localhost:8000/incidents -H "Content-Type: application/json" \
    -H "X-API-Key: $EYEOPS_API_KEY" -H "X-Roles: ops" \
    -d '{"service_id":"svc-1","severity":"sev1","summary":"db down","actor":"oncall"}'
  ```
