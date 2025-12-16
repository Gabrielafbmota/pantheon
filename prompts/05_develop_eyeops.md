# Prompt — Desenvolver EyeOfHorusOps

Você é especialista em observabilidade e incidentes (OTEL, logs, runbooks).

Quero implementar o **EyeOfHorusOps** com prioridade para **logs de container**.

MVP1:
- Dashboard/API por serviço
- Logs + health + incidentes manuais
- Eventos `incident.*` e publicação no Mnemosyne (postmortem)

Evolução:
- Runbooks allowlisted com aprovação e auditoria

Siga o fluxo:
1) Modelo (Incident/Signal/RunbookAction)
2) API e coleta de logs
3) Incidentes e timeline
4) Testes e guardrails de segurança
