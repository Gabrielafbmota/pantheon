# 09 — Mnemosyne

## Propósito
Transformar dados brutos em conhecimento estruturado, versionado e pesquisável.

## Pipeline obrigatório
1. Fetch — coleta
2. Normalize — formato canônico
3. Enrich — tags/classificação/metadados
4. Summarize — manual/assistido
5. Persist — estruturado + bruto
6. Index — busca textual e futura semântica

## Modelo conceitual
- KnowledgeEntry
- Source
- Tag
- Taxonomy/Classification
- Metadata
- AuditTrail / Version
- IngestionRun

## MVP1
- API: ingest, search, reprocess, audit
- Fingerprint determinístico (deduplicação)
- Versionamento imutável (novas versões, não overwrite)
- Persistência pluggable: memória ou MongoDB
- Armazenamento bruto opcional em S3 (URI anexada em versões)
- Auditoria por runId + métricas OTEL (opt-in)
- Eventos (planejado):
  - `knowledge.v1.ingested`
  - `knowledge.v1.version_created`

## Estado atual
| Área                     | Status | Observações                                     |
|--------------------------|--------|-------------------------------------------------|
| API FastAPI              | ✅      | Rotas ingest/search/reprocess/audit             |
| Persistência             | ✅      | In-memory e MongoDB                             |
| Indexador                | ✅      | In-memory e Mongo-backed                        |
| Storage bruto            | ✅      | S3 opcional (desligado se sem bucket)           |
| Segurança                | ✅      | API Key opcional via header `X-API-Key`         |
| Observabilidade          | ✅      | Contadores OTEL com fallback no-op              |
| Integração eventos       | 🚧     | Hooks prontos, publishers ainda não acoplados   |

## Evoluções
- Busca híbrida (BM25 + embeddings)
- RAG com evidência (citações)
- Recomendação automática
