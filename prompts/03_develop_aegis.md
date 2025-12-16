# Prompt — Desenvolver Aegis

Você é especialista em qualidade e segurança (pre-commit/CI).

Quero implementar o **Aegis** com:
- CLI local (pre-commit) + CI gate (GitHub Actions)
- Policies versionadas (policy-as-code)
- Findings com severidade, baseline e waivers com expiração
- Persistência em MongoDB
- Eventos `quality.*` para Pantheon/Mnemosyne

Siga o fluxo:
1) Modelo de domínio e severidade
2) Pre-commit rápido
3) CI gate por delta vs baseline
4) Persistência e eventos
5) Testes (unit e integração)
