# EyeOfHorusOps

Camada de observabilidade e operação centralizada (MVP) com FastAPI e Clean Architecture. Funcionalidades cobertas:
- Registry de serviços (com env, owners, endpoints, config de logging/health/Otel)
- Auth + RBAC básico via API Key e roles em header
- Ingest e busca de logs centralizados por serviço/env/trace_id/correlation_id
- Health check simples por serviço (HTTP GET opcional)
- Incidentes manuais e a partir de sinais/alertas, com timeline imutável
- Runbooks controlados com allowlist/cooldown, aprovação explícita e auditoria
- Observabilidade via OTEL (desabilitado por padrão para dev) e hardening para Mongo/Loki

## Como rodar
1. Instale dependências  
   - Poetry: `poetry install`  
   - Ou pip: `pip install -r requirements.txt`
2. Configure persistência real (default Mongo + Loki)
   - Exija `MONGO_URI` (ex.: `mongodb://localhost:27017`) e opcional `MONGO_DB` (default `eyeofhorusops`)
   - Exija `LOKI_URL` (ex.: `http://localhost:3100`)
   - Para rodar totalmente in-memory (sem Mongo/Loki), use `EYEOPS_PERSISTENCE=memory`
   - Para desativar OTEL no dev: `EYEOPS_DISABLE_OTEL=1` (default)
   - Para proteger rotas: defina `EYEOPS_API_KEY` e envie `X-API-Key` + `X-Roles` (`ops`, `admin`, `service`)
3. Suba a API local  
   - Poetry: `poetry run uvicorn eyeofhorusops.presentation.api.main:app --reload`  
   - Pip: `uvicorn eyeofhorusops.presentation.api.main:app --reload`
3. Exercite endpoints (exemplos):
   ```bash
   # Registrar serviço
   curl -X POST http://localhost:8000/services -H "Content-Type: application/json" -H "X-API-Key: $EYEOPS_API_KEY" -H "X-Roles: ops" -d '{
     "id":"svc-1","name":"payments","env":"prod","owners":["sre@acme"],"health_url":"http://localhost:8080/health"
   }'

   # Ingerir log
   curl -X POST http://localhost:8000/logs/svc-1 -H "Content-Type: application/json" -d '{
     "message":"container restarted","level":"warn","trace_id":"t-123","correlation_id":"c-456","env":"prod"
   }'

   # Buscar logs
   curl "http://localhost:8000/logs?service_id=svc-1&trace_id=t-123"

   # Abrir incidente manual
   curl -X POST http://localhost:8000/incidents -H "Content-Type: application/json" -d '{
     "service_id":"svc-1","severity":"sev1","summary":"latência alta","actor":"oncall"
   }'

   # Registrar ação de runbook
   curl -X POST http://localhost:8000/runbooks/actions -H "Content-Type: application/json" -d '{
     "id":"restart","name":"Restart service","description":"noop restart",
     "allowed_params":["reason"],"cooldown_seconds":300
   }'

   # Executar runbook
   curl -X POST http://localhost:8000/runbooks/execute -H "Content-Type: application/json" -d '{
     "service_id":"svc-1","incident_id":"<incident_id>","action_id":"restart",
     "params":{"reason":"recover"}, "actor":"oncall"
   }'

   # Aprovar runbook bloqueado
   curl -X POST http://localhost:8000/runbooks/approve -H "Content-Type: application/json" -H "X-API-Key: $EYEOPS_API_KEY" -H "X-Roles: admin" -d '{
     "job_id":"<job_id>","approver":"admin","note":"ok to proceed"
   }'
   ```

## Decisões e trade-offs
- Clean Architecture: domínio + casos de uso + adaptadores (in-memory). Repositórios podem ser trocados por Loki/CloudWatch, Prometheus e bancos persistentes.
- Guardrails: runbooks exigem ação allowlisted, params validados e cooldown por serviço+ação. Aprovação manual marcada como `requires_approval` (MVP2: gateway de aprovação).
- Timeline imutável e correlação: cada incidente armazena eventos e sinais com `trace_id` e `correlation_id` quando enviados.
- Health: check HTTP com timeout curto; se falhar, status `degraded` com detalhe de erro.
- Segurança: API Key simples + roles em header; adequado para PoC, recomenda-se provider de identidade antes de produção.
