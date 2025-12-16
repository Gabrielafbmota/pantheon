# Mnemosyne

Mnemosyne é a memória viva do ecossistema: transforma eventos, relatórios, documentos e incidentes em conhecimento estruturado, versionado e pesquisável. Este MVP usa Python + FastAPI, Clean Architecture e armazenamento em memória (com contratos prontos para MongoDB/S3).

## Fluxo implementado (MVP1)
1. **Fetch**: recebe documentos brutos com origem identificada.
2. **Normalize**: limpa conteúdo, uniformiza metadados e resolve taxonomias.
3. **Enrich**: gera fingerprint sha256, acrescenta tags herdadas e sinalizações básicas.
4. **Summarize**: produz um resumo curto (ou aceita resumo manual enviado).
5. **Persist**: salva de forma imutável, cria versões e registra auditoria por `run_id`.
6. **Index**: mantém um índice textual simples para busca com filtros.

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
- Persistência MongoDB e armazenamento bruto (GridFS/S3).
- Enriquecimento semântico e embeddings para RAG.
- Guardrails para resumos assistidos.
