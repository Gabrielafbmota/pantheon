# 13 — CI/CD e Dockerização padrão (GitHub Actions)

## Padrões
- Build por serviço (paths filter)
- Testes obrigatórios (pytest)
- Lint/format (ruff/black/mypy) como gate
- SBOM/dependency audit quando aplicável
- Imagem Docker multi-arch (arm64/amd64) se necessário

## Workflow sugerido (alto nível)
1. Checkout
2. Setup Python + Poetry
3. Install deps
4. Lint + tests
5. Build Docker
6. Push registry (GHCR)
7. Deploy (ECS/K3s/Compose), conforme ambiente

## Docker padrão
- Logs em stdout (json)
- Healthcheck
- Env vars para config
- Usuário não-root quando possível
