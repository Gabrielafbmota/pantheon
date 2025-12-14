# Aegis (MVP)

Aegis é um guardião de qualidade e segurança — MVP inicial.

- CLI: `aegis scan`
- Modelos: `Policy`, `Rule`, `Scan`, `Finding`, `Baseline`, `Waiver`
- Persistence: interfaces (stubs) para MongoDB

Como rodar (Poetry)
--------------------

Pré-requisitos: Python 3.11+ e Poetry instalado.

No diretório do serviço (`services/aegis`):

1. Instalar dependências:

```bash
cd services/aegis
poetry install
```

2. Executar o scanner (CLI):

```bash
poetry run aegis scan --repo . --commit HEAD --output -
```

3. Persistir um relatório (Mongo):

```bash
# defina MONGO_URI no ambiente ou passe --mongo-uri
poetry run aegis persist --input-file report.json --mongo-uri "mongodb://..."
```

Convenience:

- `./run.sh` — wrapper para `poetry run` (ex.: `./run.sh scan --repo . --output -`)
- `Makefile` com alvos `install`, `test`, `scan` e `run`.

Veja `docs/DECISIONS.md` para decisões de design e trade-offs.

To-Do (roadmap) ✅
------------------

Lista de tarefas e status atual do MVP:

- [x] **Design do modelo de domínio** — `Policy`, `Rule`, `Scan`, `Finding`, `Baseline`, `Waiver` (implementado)
- [x] **Implementar library core** — modelos Pydantic, validação, serialização (implementado)
- [x] **Criar CLI MVP** — `scan` e `persist` com Typer (implementado)
- [x] **Integração pre-commit** — hook rápido para `aegis scan` (implementado)
- [x] **CI Gate (GitHub Actions)** — workflow que roda `aegis scan` em PRs (implementado)
- [x] **Persistência MongoDB** — adapter básico `MongoReportRepository` (implementado)
- [x] **Integrações de eventos** — stubs para Mnemosyne e EyeOfHorusOps (implementado)
- [x] **Testes e CI** — testes unitários para modelos, CLI e adaptadores (implementado)
- [x] **Documentação e decisões** — `docs/DECISIONS.md` e README (implementado)
- [ ] **Explicação final e wrap up** — escrever seção de wrap-up com trade-offs, guia de uso e próximos passos (em progresso)

Se quiser, posso transformar os itens acima em issues/PRs separados para acompanhar o progresso no repositório (posso criar/escrever as issues para você).

Próximos passos (priorizados) ▶️
---------------------------------

Estes são os próximos itens que recomendo para levar o MVP a um produto utilizável em projetos:

- **Waivers** (prioridade alta)
	- Implementar CRUD de waivers com campos obrigatórios (justificativa, owner, expires_at).
	- Validar e aplicar waivers durante `scan` (skip/ignore findings cobertos) e expirar automaticamente.
	- Adicionar comandos CLI: `waiver create|list|revoke|approve` e integração com persistência no Mongo.

- **Baselines** (prioridade alta)
	- Permitir export/import de baselines (fingerprints) e storage em MongoDB.
	- Supportar comparação de delta (novos findings vs baseline) em CI e pre-commit.

- **Scanners adicionais (detectors)** (prioridade média)
	- Integrar `detect-secrets` (secrets), `pip-audit` ou `safety` (dependências) e `bandit` (SAST) como módulos opcionais.
	- Fazer adaptadores para rodar em pre-commit (rápidos) e em CI (com mais profundidade).

- **Política como código e versionamento de policies** (prioridade média)
	- Definir schema de `policy` versionado e garantir auditabilidade (metadados + histórico).

- **Integrações e eventos** (prioridade média)
	- Implementar publishers reais para Mnemosyne (KnowledgeEntry) e EyeOfHorusOps (eventos) com retries e auth.

- **Operacional e qualidade** (prioridade baixa)
	- Documentação de uso (ex.: exemplos de `pre-commit` e workflow de PR), testes de integração e E2E, e um job CI que constrói e publica artefatos.

Se desejar, começo imediatamente pelo item de maior prioridade — **Waivers** — e gero issues/PRs correspondentes. Qual item você prefere priorizar? 
