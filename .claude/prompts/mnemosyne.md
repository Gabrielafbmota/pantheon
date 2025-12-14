Você é um assistente especialista em sistemas de ingestão de dados,
organização de conhecimento e arquitetura de memória técnica.

Quero implementar um sistema chamado Mnemosyne.

Objetivo:
Criar a memória viva do ecossistema, capaz de transformar dados brutos
(eventos, relatórios, documentos, incidentes) em conhecimento estruturado,
versionado e pesquisável.

Papel do sistema:
- Ingerir conhecimento de múltiplas fontes
- Normalizar, enriquecer e versionar conteúdo
- Manter histórico e rastreabilidade
- Servir como base para busca e IA (RAG no futuro)

Stack:
- Backend: Python + FastAPI
- Poetry
- Banco: MongoDB
- Storage bruto: S3 ou filesystem
- Arquitetura: Clean Architecture

Modelo de dados conceitual:
- KnowledgeEntry
- Source
- Tag
- Taxonomy
- Version
- AuditTrail
- IngestionRun

Pipeline obrigatório:
1. Fetch
2. Normalize
3. Enrich
4. Summarize (manual ou assistido)
5. Persist
6. Index

Requisitos obrigatórios:
- Deduplicação por fingerprint
- Versionamento imutável
- Reprocessamento idempotente
- Auditoria por runId
- Busca textual com filtros

Integrações:
- Aegis: relatórios e findings
- EyeOfHorusOps: incidentes e pós-mortem
- AtlasForge: ADRs e decisões de template

Evolução futura:
- Busca semântica
- Embeddings
- RAG com evidência e citações
- Resumos assistidos com guardrails

Siga este fluxo:
1. Definir modelo conceitual e estados.
2. Implementar pipeline MVP1.
3. Implementar busca e filtros.
4. Implementar auditoria e reprocessamento.
5. Explicar decisões técnicas.
