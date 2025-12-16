# Prompt — Desenvolver Mnemosyne

Você é especialista em pipelines de conhecimento (FastAPI, MongoDB, auditoria).

Quero implementar o **Mnemosyne** com pipeline:
Fetch → Normalize → Enrich → Summarize → Persist → Index

MVP1:
- API de ingestão e busca textual
- Deduplicação por fingerprint determinístico
- Versionamento imutável e auditoria por runId
- Eventos `knowledge.*`

Siga o fluxo:
1) Modelo de dados e estados
2) Pipeline e reprocessamento idempotente
3) Indexação e busca
4) Observabilidade e testes
