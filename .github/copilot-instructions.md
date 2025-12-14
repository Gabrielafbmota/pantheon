<!-- Instruções curtas e acionáveis para agentes (Copilot/GitHub AI) trabalhando neste repositório -->
# Instruções para Copilot — Atlas Complete Kit (ALINHADO ao `CLAUDE.md`)

Este arquivo resume as decisões arquiteturais, convenções e comandos essenciais do projeto — ele foi adaptado para espelhar o conteúdo de `CLAUDE.md` e servir como referência rápida para contribuições automáticas (Copilot/GitHub AI).

## 📘 Visão Geral (leia primeiro)

- **Atlas Complete Kit**: repositório de documentação, arquitetura e prompts para um ecossistema de serviços (AtlasForge, Aegis, Mnemosyne, EyeOfHorusOps).
- **Estado**: MVP0 — a plataforma ainda está em definição; este repositório documenta decisões, contratos e padrões.
- **Local principal de implementação**: `services/atlasforge/` (gerador zero-click de projetos FastAPI seguindo Clean Architecture).

## 🧭 Estrutura & conteúdo canônico

- `.claude/CLAUDE.md` — arquivo canônico com arquitetura, padrões e decisões. Use-o como referência primária.
- `prompts/` — prompts por sistema
- `docs/` — documentação arquitetural e planejamento
- `services/` — serviços quando implementados

## 🏗️ Padrões obrigatórios

- Clean Architecture (obrigatório):

```
src/<service>/
 ├── domain/         # Entidades, value objects, regras puras
 ├── application/    # Casos de uso e orquestração
 ├── adapters/       # Persistência, gateways, clients (ou infrastructure/)
 └── api/            # Endpoints FastAPI e schemas Pydantic
tests/               # Testes unitários e de integração
```

- Regras importantes:
  - Não coloque regras de negócio fora de `domain/`.
  - `application/` não conhece frameworks.
  - `api/` é camada de borda.
  - Dependências sempre apontam para dentro.

## ⚙️ Stack alvo

- Backend: Python + FastAPI
- Banco: MongoDB (connection string via `MONGO_URI`)
- Infra: Docker + GitHub Actions
- Observabilidade: OpenTelemetry (traces, métricas, logs)

## 🔁 Versionamento de eventos

Use o formato de evento versionado:

```
<dominio>.v<versao>.<acao>
```

Ex.: `user.v1.created`, `orders.v2.payment_succeeded`.

## 📋 Comandos de desenvolvimento (copiar/colar)

```bash
# Instalar dependências (ex.: atlasforge)
cd services/atlasforge && poetry install

# Testes
poetry run pytest

# Type checking
poetry run mypy src/

# Lint & format
poetry run ruff check src/
poetry run black src/ --check

# Rodar app (exemplo)
uvicorn src.<service>.api.main:app --reload --port 8000
```

## 🔧 Observabilidade mínima exigida

- Todos os serviços devem expor:
  - `GET /health` (readiness + liveness)
  - `GET /metrics` (Prometheus)
- Instrumentação OpenTelemetry (traces, métricas, logs estruturados).

## 🗄️ Convenções MongoDB

- Persistência via camada dedicada; documente índices e políticas de retenção.
- O cliente pode ser async (motor) ou PyMongo; `MONGO_URI` via env var.

## 🔐 Segurança

- Nunca hardcode secrets; use variáveis de ambiente.
- Não logar tokens, senhas ou connection strings.
- Seguir OWASP API Top 10.

## 🧪 Estratégia de testes

- Testes unitários obrigatórios; integração quando aplicável.
- Todos os testes devem rodar no CI.

## 🌱 Fluxo de desenvolvimento iterativo

1. Scaffold mínimo
2. Implementar casos de uso (domain + application)
3. Observabilidade
4. Testes
5. Endurecimento (qualidade e segurança)

## ✅ Checklist de PR / CI (único e obrigatório)

- Em cada PR:
  - Rodar todos os testes: `poetry run pytest`
  - Lint & format: `ruff`, `black`
  - Type-check: `mypy`
  - Executar testes de integração que afetem geração/template
  - Atualizar `services/<servico>/implementacoes/*.md` ao mudar contratos/comportamento

- Job de exemplo (CI): use Python 3.11, instale dependências com Poetry e execute lint, format, typecheck e testes.

## 📌 Convenções de branch & commits

- Branches: `feat/<area>/<desc>`, `fix/<area>/<desc>`, `chore/<area>/<desc>`
- Commits: `<escopo>: <ação concisa>` (ex.: `users: add health endpoint with otel metrics`)

## 🧠 Regras finais (para Copilot e serviços automatizados)

- Trate este repositório como plataforma interna. Não introduza decisões não documentadas sem validação.
- Priorize clareza, rastreabilidade e evolução segura.

## ➡️ Output esperado ao implementar serviços

- Sempre crie um arquivo `services/<servico>/implementacoes/*.md` com as decisões de implementação.
- Atualize o `README.md` do serviço.

---
Se precisar, posso ajustar tom, adicionar exemplos específicos (ex.: `users` service) ou gerar um PR com a alteração — diga como prefere proceder.
