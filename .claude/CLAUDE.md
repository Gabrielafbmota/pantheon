# 📘 CLAUDE.md — Atlas Complete Kit

This file provides guidance to **Claude (claude.ai / Claude Code)** when working with this repository.  
It also serves as the **canonical architectural and development reference** for the Atlas Platform.

---

## 🧭 Visão Geral do Projeto

**Atlas Complete Kit** é um repositório de **documentação, arquitetura e prompts** para um ecossistema de serviços internos, composto por quatro pilares:

- **AtlasForge** — Gerador *zero-click* de projetos backend  
- **Aegis** — Guardião de qualidade e segurança (pre-commit + CI)  
- **Mnemosyne** — Sistema de ingestão, memória e conhecimento  
- **EyeOfHorusOps** — Observabilidade, incidentes e auto-remediação controlada  

**Estado atual**: **MVP0**  
A plataforma ainda **não está implementada**.  
Este repositório existe para **definir decisões, contratos, padrões e direção**, antes da implementação.

---

## 🏗️ Arquitetura & Padrão de Integração

### Integração Primária
Arquitetura **orientada a eventos**, com **eventos versionados** e contratos explícitos.

**Formato padrão**:
```

<dominio>.v<versao>.<acao>

````

**Exemplos**:
- `user.v1.created`
- `orders.v2.payment_succeeded`

---

### Stack Alvo (Obrigatória)

- **Backend**: Python + FastAPI  
- **Arquitetura**: Clean Architecture  
- **Banco**: MongoDB  
- **Infra**: Docker + GitHub Actions  
- **Observabilidade**: OpenTelemetry (logs, métricas e traces)  

---

## 📁 Estrutura do Repositório

```text
.claude/              # Organização local para Claude (instructions + knowledge)
prompts/              # Prompts de desenvolvimento por sistema
docs/                 # Documentação arquitetural e planejamento
  ├── Arquitetura_Ecossistema.md
  ├── MVP0_Estado_Atual.md
  ├── NFRs.md
  ├── Roadmap.md
  └── Backlog.md
diagrams/             # Diagramas Mermaid (ecosystem.mmd)
.github/              # Configurações GitHub e Copilot
services/             # Serviços (quando implementados)
````

---

## 🧱 Padrão Clean Architecture (Obrigatório)

Todo serviço **deve** seguir esta estrutura lógica:

```text
src/<service>/
 ├── domain/         # Entidades, value objects, regras puras
 ├── application/    # Casos de uso e orquestração
 ├── adapters/       # Persistência, gateways, clients (ou infrastructure/)
 └── api/            # Endpoints FastAPI e schemas Pydantic
tests/               # Testes unitários e de integração
```

**Regras**

* Nenhuma regra de negócio fora de `domain/`
* `application/` não conhece frameworks
* `api/` é camada de borda
* Dependências sempre apontam para dentro

---

## ⚙️ Comandos de Desenvolvimento (Referência)

Este é primariamente um **repositório de documentação**.
Ao implementar serviços:

### Ambiente

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# ou
poetry install
```

### Execução

```bash
uvicorn src.<service>.api.main:app --reload --port 8000
```

### Testes

```bash
pytest -q
```

### Docker

```bash
docker build -t atlas-<service> .
docker run -e "MONGO_URI=..." atlas-<service>
```

### Qualidade (recomendado)

```bash
ruff check .
black .
mypy .
```

---

## 📡 Versionamento de Eventos

* Sempre versionar eventos
* Documentar schema e exemplos quando aplicável
* Evitar breaking changes sem nova versão

---

## 📊 Requisitos de Observabilidade

Todo serviço **deve incluir**:

* `GET /health` — readiness + liveness
* `GET /metrics` — compatível com Prometheus
* Instrumentação **OpenTelemetry**:

  * traces
  * métricas
  * logs estruturados

---

## 🗄️ Convenções MongoDB

* Persistência via camada dedicada
* Documentar índices e retenção
* Cliente:

  * Motor (async) ou
  * PyMongo
* Connection string **sempre** via `MONGO_URI`

---

## 🔐 Práticas de Segurança

* **Nunca** hardcode secrets
* Tudo via variáveis de ambiente
* Logs **não podem** conter:

  * tokens
  * senhas
  * connection strings
* Seguir OWASP API Top 10

---

## 🌱 Convenções de Branch & Commit

### Branches

```
feat/<area>/<descricao-curta>
fix/<area>/<descricao-curta>
chore/<area>/<descricao-curta>
```

### Commits

```
<escopo>: <ação concisa>
```

**Exemplo**:

```
users: add health endpoint with otel metrics
```

---

## 🧪 Estratégia de Testes

* Testes unitários **obrigatórios**
* Testes de integração quando aplicável
* Todos os testes devem rodar no CI

---

## 🔁 Abordagem de Desenvolvimento Iterativo

1. Scaffold mínimo
2. Comportamento (casos de uso)
3. Observabilidade
4. Testes
5. Endurecimento (qualidade e segurança)

Consulte sempre:

* `docs/`
* `prompts/`
* arquivos de knowledge do Claude

---

## 🧩 Exemplo — Criando um Novo Serviço

Serviço `users`:

1. `src/users/api/main.py` — FastAPI + `/health`
2. `src/users/domain/` — entidade `User`
3. `src/users/application/` — `CreateUser`
4. `src/users/adapters/mongo.py`
5. `tests/users/test_api.py`

---

## ❓ Quando Perguntar Antes de Decidir

* Troca de banco (ex.: MongoDB → PostgreSQL)
* Mudanças que afetam mais de um serviço
* Decisões arquiteturais globais
* Quebra de contratos de eventos

---

# 📌 Decisões de Implementação — AtlasForge

## Localização

**`services/atlasforge/`**

## Dependências

**Poetry**

## MVP1

CLI completo:

* geração
* módulos
* upgrade seguro

## Integrações

Placeholders reais:

* Aegis
* Mnemosyne
* EyeOfHorusOps

## Templates

Modelo híbrido:

* estrutura em código
* conteúdo em templates

➡️ Todas as decisões são **coerentes, escaláveis e alinhadas à visão de plataforma**.

---

## 🧠 Regra Final (para Claude)

* Trate este repositório como **plataforma interna**
* Respeite os padrões descritos aqui
* Não introduza decisões não documentadas
* Priorize clareza, rastreabilidade e evolução segura


## Output Final
* Sempre consulte este arquivo para decisões arquiteturais
* Sempre crie um arquivo com as informações de implementação dentro de services/<servico>/implementacoes/*.md
* Atuelize o README.md
