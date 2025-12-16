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
- API: ingest e search
- Fingerprint determinístico (deduplicação)
- Versionamento imutável (novas versões, não overwrite)
- Auditoria por runId
- Eventos:
  - `knowledge.v1.ingested`
  - `knowledge.v1.version_created`

## Evoluções
- Busca híbrida (BM25 + embeddings)
- RAG com evidência (citações)
- Recomendação automática
