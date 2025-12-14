Você é um assistente especialista em qualidade de código,
segurança de software e automação de pipelines.

Quero implementar um sistema chamado Aegis.

Objetivo:
Criar um guardião de qualidade e segurança que impeça código ruim,
inseguro ou inconsistente de ser commitado ou implantado.

Papel do sistema:
- Executar validações locais (pre-commit)
- Atuar como gate obrigatório em CI/CD
- Centralizar policies versionadas (policy-as-code)
- Produzir relatórios auditáveis e eventos para outros sistemas

Stack:
- Python
- CLI obrigatória
- Integração com pre-commit
- Integração com GitHub Actions
- Persistência: MongoDB
- Arquitetura: Clean Architecture

Modelo conceitual:
- Policy
- Rule
- Scan
- Finding
- Severity (INFO → CRITICAL)
- Baseline
- Waiver (com expiração)

Requisitos obrigatórios:
- Policies versionadas e auditáveis
- Gates por estágio:
  - pre-commit (rápido)
  - CI em PR
  - main/release
- Bloqueio por delta (findings novos vs baseline)
- Waivers obrigatoriamente com:
  - justificativa
  - owner
  - data de expiração
- CRITICAL nunca pode passar sem aprovação explícita

Ferramentas esperadas:
- Lint / format
- Secrets scan
- Dependency audit
- SAST básico

Integrações:
- Mnemosyne: publicar relatórios como KnowledgeEntry
- EyeOfHorusOps: disparar eventos de violação crítica
- AtlasForge: ser injetado automaticamente nos projetos gerados

Requisitos não funcionais:
- Execução determinística
- Idempotência por repo + commit
- Logs estruturados
- Relatórios persistidos (metadados + bruto)

Siga este fluxo:
1. Definir modelo de policy e severidade.
2. Implementar pre-commit MVP.
3. Implementar CI gate MVP.
4. Persistir relatórios e emitir eventos.
5. Explicar decisões e trade-offs.
