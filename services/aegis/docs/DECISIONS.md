# Aegis — Decisões e Trade-offs (MVP)

Resumo das decisões iniciais:

- Models: usar Pydantic para validação e serialização determinística.
- CLI: Typer pela ergonomia e fácil integração com testes.
- Pre-commit: hooks locais que executam `aegis scan` (rápido, sem I/O pesado).
- CI: GitHub Actions executando `aegis scan` em PRs; bloquear por delta/new CRITICAL.
- Persistence: MongoDB para reports e baselines (interfaces primeiro, implementação depois).

Trade-offs:

- MVP opta por detectores simples e determinísticos em favor de velocidade e reprodutibilidade.
- Integrações com Mnemosyne / EyeOfHorusOps inicialmente stubs — reduz complexidade inicial.
