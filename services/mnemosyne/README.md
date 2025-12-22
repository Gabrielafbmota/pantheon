# Mnemosyne

Mnemosyne é a memória viva do ecossistema: transforma eventos, relatórios, documentos e incidentes em conhecimento estruturado, versionado e pesquisável. Este MVP usa Python + FastAPI, Clean Architecture e suporta persistência MongoDB + S3 opcional para o bruto, com indexador persistente e auditoria de runs.

## Como codar e rodar
1. **Instale dependências**
   - Com Poetry: `poetry install`
   - Ou com pip: `pip install -r requirements.txt`
2. **Rodar testes**: `pytest` (6 testes)
3. **Subir API local** (padrão: armazenamento in-memory; defina variáveis para habilitar backends reais):
   - Com Poetry: `poetry run uvicorn mnemosyne.presentation.api.main:app --reload`
   - Ou pip: `uvicorn mnemosyne.presentation.api.main:app --reload`
4. **Fluxo principal**: use os casos de uso em `mnemosyne/application/use_cases` (ingest, search, reprocess). A API deve apenas orquestrar esses casos.

### Variáveis de ambiente
- `MNEMO_PERSISTENCE=mongo|memory` (default `memory`)
- `MNEMO_MONGO_URI` e `MNEMO_MONGO_DB` para MongoDB
- `MNEMO_S3_BUCKET` para armazenar conteúdo bruto em S3 (opcional)
- `MNEMO_API_KEY` para habilitar autenticação via header `X-API-Key`
- `MNEMO_DISABLE_OTEL=1` para desabilitar OTEL (default para dev)

## Fluxo implementado (MVP1)
1. **Fetch**: recebe documentos brutos com origem identificada.
2. **Normalize**: limpa conteúdo, uniformiza metadados e resolve taxonomias.
3. **Enrich**: gera fingerprint sha256, acrescenta tags herdadas e sinalizações básicas.
4. **Summarize**: produz um resumo curto (ou aceita resumo manual enviado).
5. **Persist**: salva de forma imutável, cria versões e registra auditoria por `run_id` (Mongo ou memória).
6. **Index**: mantém um índice textual persistente (Mongo) ou in-memory com filtros.
7. **Observabilidade**: métricas/traços prontos para OTLP, com contador de ingests e buscas.

## Conceitos de domínio
- **KnowledgeEntry**: entidade principal contendo versões imutáveis.
- **Source**: descreve a origem (Aegis, EyeOfHorusOps, AtlasForge, etc.).
- **Tag / Taxonomy**: enriquecimento e classificação.
- **Version**: captura fingerprint, resumo, conteúdo normalizado e metadados.
- **AuditTrail**: eventos por etapa do pipeline e status agregado.
- **IngestionRun**: input + resultado, usado para idempotência e reprocessamento.

## Casos de uso expostos
- `POST /ingestions`: executa o pipeline completo.
- `POST /reprocess/{run_id}`: reprocessa um `run` anterior de forma idempotente.
- `GET /search`: busca textual com filtros (tags, taxonomia, tipo de origem).

## Decisões técnicas
- **Clean Architecture**: entidades e serviços de domínio desacoplados de FastAPI.
- **Idempotência**: `run_id` é armazenado; reruns retornam o mesmo resultado sem duplicar versões.
- **Deduplicação**: fingerprint é calculado a partir do conteúdo normalizado; versões só são criadas quando o fingerprint muda.
- **Versões imutáveis**: `Version` é append-only dentro de `KnowledgeEntry`.
- **Auditoria**: cada etapa grava eventos em `AuditTrail`, vinculados ao `run_id` e ao documento.
- **Busca**: índice em memória com filtros; interface permite substituição por MongoDB/Atlas Search.

## Próximos passos
- Persistência avançada (GridFS), compressão e TTL configurável.
- Enriquecimento semântico e embeddings para RAG.
- Guardrails para resumos assistidos.
