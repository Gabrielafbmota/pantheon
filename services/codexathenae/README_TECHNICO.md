# 📚 CodexAthenae — README Técnico (Raspberry Pi / arm64)

Data: 2026-01-09

Este repositório contém **documentação + prompts + templates** para implementar o CodexAthenae como **plataforma única** (catálogo + leitura ativa Kallioreader).

## Requisitos

- Python 3.12+
- Node 20+
- Docker + Docker Compose v2
- MongoDB (Atlas recomendado) ou Mongo local
- Raspberry Pi 4+ (arm64) (alvo primário)

## Variáveis de ambiente

Crie `.env` na raiz do serviço (ex.: `services/codexathenae/.env`).

Veja `.env.example`.

### Segurança (mínimo)
- **NUNCA** commitar `.env`
- CORS restrito aos seus domínios
- JWT com segredo forte (>=32 chars)
- Rate limit básico (Nginx / middleware)

## Rodando local (dev)

### Backend (FastAPI)
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
uvicorn codexathenae.presentation.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (React)
```bash
cd frontend
npm install
npm run dev -- --host
```

### Importação do JSON
```bash
cd backend
python -m scripts.import_books --json ../data/codexathenae.books.json
```

## Docker Compose (arm64)

```bash
docker compose up --build
```

- `docker-compose.yml` suporta:
  - Mongo local **opcional**
  - Backend + Frontend
  - Rede isolada

> Se você usar Mongo Atlas, desative o serviço `mongo` e configure `MONGO_DB_URI`.

## CI/CD (GitHub Actions)

Este pacote inclui um template em `.github/workflows/ci.yml` para:
- lint (ruff)
- tests (pytest)
- build docker

Deploy: recomendado via `docker compose pull && docker compose up -d` no Pi.

## Testes

### Backend
```bash
cd backend
pytest -q
```

## Estrutura do pacote

- `CODEXATHENAE_ATLASDOC.md` — documento único consolidado
- `prompts/` — prompts por contexto e por fluxo (backend/frontend/bot/infra)
- `backend/` — template mínimo (Clean Architecture)
- `scripts/import_books.py` — ingestão idempotente do `codexathenae.books.json`
- `diagrams/` — Mermaid prontos
