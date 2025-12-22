## Serviço: AtlasForge
**Introdução**  
Gerador zero-click de projetos FastAPI com Clean Architecture, manifestos de arquivos e módulos opcionais (mongo, otel, events, auth, jobs).

**Objetivos**  
- Criar serviços prontos para produção em segundos.  
- Garantir idempotência e rastreabilidade por manifesto de checksums.  
- Padronizar arquitetura e qualidade desde o bootstrap.

**Features**  
- CLI `atlasforge` com comandos `generate`, `validate`, `inspect`, `version`.  
- Templates com 4 camadas (domain/application/infrastructure/presentation).  
- Dockerfile, testes, health checks e docs prontos.  
- Manifesto SHA256 de todos os arquivos.

**Organização de Pastas**  
- `services/atlasforge/src/atlasforge/` — domínio, aplicação, infraestrutura, CLI.  
- `services/atlasforge/templates/` — templates Jinja2 base.  
- `services/atlasforge/tests/` — unitários e integração.  
- `services/atlasforge/Makefile`, `install.sh`, `FEATURE_ANALYSIS.md`, `IMPLEMENTATION.md`.

**Como instalar**  
- Global: `cd services/atlasforge && ./install.sh` (ou `make install-global` ou `pipx install .`).  
- Dev: `cd services/atlasforge && poetry install` (ou `make install-dev`).

**Como rodar**  
- Gerar serviço: `atlasforge generate <nome> [--modules mongo,otel,events,auth,jobs] [--output DIR]`.  
- Validar projeto: `atlasforge validate <path>`.  
- Ver versão: `atlasforge version`.

**Curls de todos os endpoints**  
Não expõe endpoints HTTP (CLI apenas).

## Serviço: Aegis
**Introdução**  
Guardião de qualidade e segurança com CLI para lint, formatação e detecção de segredos, com baseline delta e persistência em Mongo.

**Objetivos**  
- Bloquear regressões de qualidade/segurança antes do deploy.  
- Padronizar scanners em CI/CD e pre-commit.  
- Persistir histórico de findings e permitir baselines delta.

**Features**  
- Comandos `aegis scan` e `aegis persist`.  
- Scanners reais: Ruff, Black, detect-secrets.  
- Baseline delta para aceitar findings conhecidos.  
- Persistência MongoDB opcional; integração via pipx/pre-commit/CI.

**Organização de Pastas**  
- `services/aegis/src/aegis/` — modelos, CLI, scanners, adapters.  
- `services/aegis/tests/` — testes de CLI, modelos e adapters.  
- `services/aegis/Makefile`, `install.sh`, `run.sh`, `IMPLEMENTATION.md`, `MVP_VALIDATION.md`.

**Como instalar**  
- Global: `cd services/aegis && ./install.sh` (ou `make install-global`).  
- Dev: `cd services/aegis && poetry install`.

**Como rodar**  
- Scan padrão: `poetry run aegis scan --repo . --commit HEAD --output -`.  
- Scan com baseline: `aegis scan --baseline baseline.json --output -`.  
- Persistir report: `aegis persist --input-file report.json --mongo-uri "<uri>"`.  
- Wrapper: `./run.sh scan --repo .`.

**Curls de todos os endpoints**  
Não expõe endpoints HTTP (CLI apenas).

## Serviço: EyeOfHorusOps
**Introdução**  
Camada de observabilidade e operações: registry de serviços, ingest/busca de logs, health, incidentes e runbooks com aprovação, construído em FastAPI.

**Objetivos**  
- Centralizar telemetria (logs) e visão de saúde dos serviços.  
- Gerir incidentes com timeline imutável e correlação.  
- Controlar execução de runbooks com guardrails e auditoria.

**Features**  
- Registry de serviços com metadados e config de OTEL/log/health.  
- Ingestão e busca de logs (Loki por padrão; fallback in-memory).  
- Health check opcional por serviço.  
- Incidentes manuais ou a partir de sinais/alertas.  
- Runbooks com allowlist, cooldown, aprovação e auditoria.  
- OTEL instrumentado; API Key + roles (ops, admin, service).

**Organização de Pastas**  
- `services/eyeofhorusops/src/eyeofhorusops/` — domain, application, infrastructure (mongo, loki), presentation (FastAPI).  
- `services/eyeofhorusops/tests/` — testes.  
- `services/eyeofhorusops/pyproject.toml`, `requirements.txt`.

**Como instalar**  
```bash
cd services/eyeofhorusops
poetry install            # ou: pip install -r requirements.txt
```

**Como rodar**  
- Variáveis: `MONGO_URI`, `MONGO_DB`, `LOKI_URL`; para in-memory use `EYEOPS_PERSISTENCE=memory`.  
- Auth opcional: `EYEOPS_API_KEY` e headers `X-API-Key` + `X-Roles`.  
- Subir API: `poetry run uvicorn eyeofhorusops.presentation.api.main:app --reload`.

**Curls de todos os endpoints**
```bash
export BASE_URL="http://localhost:8000"
export API_KEY="$EYEOPS_API_KEY"   # opcional
export ROLES="ops"                 # ops|admin|service

curl "$BASE_URL/health"
curl -X POST "$BASE_URL/services" -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" -H "X-Roles: $ROLES" \
  -d '{"id":"svc-1","name":"payments","env":"prod","owners":["sre@acme"],"health_url":"http://localhost:8080/health"}'
curl -H "X-API-Key: $API_KEY" -H "X-Roles: $ROLES" "$BASE_URL/services"
curl -H "X-API-Key: $API_KEY" -H "X-Roles: $ROLES" "$BASE_URL/services/svc-1"
curl -X POST "$BASE_URL/logs/svc-1" -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" -H "X-Roles: $ROLES" \
  -d '{"message":"container restarted","level":"warn","trace_id":"t-123","correlation_id":"c-456","env":"prod"}'
curl -H "X-API-Key: $API_KEY" -H "X-Roles: $ROLES" "$BASE_URL/logs?service_id=svc-1&trace_id=t-123"
curl "$BASE_URL/health/svc-1"
curl -X POST "$BASE_URL/incidents" -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" -H "X-Roles: ops" \
  -d '{"service_id":"svc-1","severity":"sev1","summary":"latência alta","actor":"oncall","trace_id":"t-123"}'
curl -X POST "$BASE_URL/alerts" -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" -H "X-Roles: ops" \
  -d '{"service_id":"svc-1","type":"metrics","severity":"sev2","message":"erro 5xx","trace_id":"t-123"}'
curl -H "X-API-Key: $API_KEY" -H "X-Roles: $ROLES" "$BASE_URL/incidents"
curl -H "X-API-Key: $API_KEY" -H "X-Roles: $ROLES" "$BASE_URL/incidents/<incident_id>"
curl -X POST "$BASE_URL/incidents/<incident_id>/status" -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" -H "X-Roles: ops" \
  -d '{"status":"resolved","note":"service recovered","actor":"oncall"}'
curl -X POST "$BASE_URL/runbooks/actions" -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" -H "X-Roles: admin" \
  -d '{"id":"restart","name":"Restart service","description":"noop","allowed_params":["reason"],"cooldown_seconds":300,"requires_approval":true}'
curl -H "X-API-Key: $API_KEY" -H "X-Roles: $ROLES" "$BASE_URL/runbooks/actions"
curl -X POST "$BASE_URL/runbooks/execute" -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" -H "X-Roles: ops" \
  -d '{"service_id":"svc-1","incident_id":"<incident_id>","action_id":"restart","params":{"reason":"recover"},"actor":"oncall"}'
curl -X POST "$BASE_URL/runbooks/approve" -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" -H "X-Roles: admin" \
  -d '{"job_id":"<job_id>","approver":"admin","note":"ok to proceed"}'
curl "$BASE_URL/metrics"
```

## Serviço: Mnemosyne
**Introdução**  
Memória viva do ecossistema: ingere eventos/relatórios, normaliza, enriquece, sumariza e indexa conhecimento com versões imutáveis e idempotência por run_id.

**Objetivos**  
- Registrar conhecimento operacional de forma estruturada e versionada.  
- Deduplicar conteúdos via fingerprint e permitir reprocessamento seguro.  
- Disponibilizar busca textual e por tags/taxonomia.

**Features**  
- Pipeline Ingest → Normalize → Enrich → Summarize → Persist → Index.  
- Backends: memória (default) ou MongoDB; armazenamento bruto opcional em S3.  
- API Key opcional para proteger endpoints.  
- Observabilidade OTEL pronta.

**Organização de Pastas**  
- `services/mnemosyne/src/mnemosyne/` — domain, application/use_cases, infraestrutura (persistence, storage, indexing), FastAPI.  
- `services/mnemosyne/tests/` — testes.  
- `services/mnemosyne/pyproject.toml`, `requirements.txt`.

**Como instalar**  
```bash
cd services/mnemosyne
poetry install            # ou: pip install -r requirements.txt
```

**Como rodar**  
- Variáveis: `MNEMO_PERSISTENCE=memory|mongo`, `MNEMO_MONGO_URI`, `MNEMO_MONGO_DB`; opcional `MNEMO_S3_BUCKET` para bruto; `MNEMO_API_KEY` para auth.  
- Subir API: `poetry run uvicorn mnemosyne.presentation.api.main:app --reload`.

**Curls de todos os endpoints**
```bash
export BASE_URL="http://localhost:8000"
export MNEMO_API_KEY="$MNEMO_API_KEY"   # opcional

curl "$BASE_URL/health"
curl -X POST "$BASE_URL/ingestions" -H "Content-Type: application/json" -H "X-API-Key: $MNEMO_API_KEY" \
  -d '[{"external_id":"rep-1","source":{"id":"aegis","name":"Aegis","type":"security"},"content":"resumo do scan","tags":[{"key":"severity","value":"high"}],"taxonomy":["security","python"],"summary":"scan de segurança"}]'
curl -H "X-API-Key: $MNEMO_API_KEY" "$BASE_URL/search?text=security&tags=severity:high&source_types=security"
curl -X POST -H "X-API-Key: $MNEMO_API_KEY" "$BASE_URL/reprocess/<run_id>"
curl -H "X-API-Key: $MNEMO_API_KEY" "$BASE_URL/runs/<run_id>"
```