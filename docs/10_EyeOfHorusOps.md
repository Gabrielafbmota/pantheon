# 10 — EyeOfHorusOps

## Propósito
Operação confiável: logs, métricas, traces, incidentes e remediação controlada.

## MVP1
- Dashboard básico por serviço
- Visualizar logs de container (prioridade)
- Health/status board
- Incidentes manuais + timeline
- Eventos:
  - `incident.v1.opened`
  - `incident.v1.updated`
  - `incident.v1.closed`

## Self-healing (evolução)
- Ações allowlisted
- Cooldown obrigatório
- Aprovação manual (MVP2)
- Auditoria completa (quem aprovou, por quê, impacto)
