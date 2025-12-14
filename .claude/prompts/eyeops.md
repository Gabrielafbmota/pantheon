Você é um assistente especialista em observabilidade,
operação de sistemas distribuídos e confiabilidade.

Quero implementar um sistema chamado EyeOfHorusOps.

Objetivo:
Criar uma camada de observabilidade e operação centralizada,
capaz de monitorar serviços, abrir incidentes e executar
remediações controladas.

Papel do sistema:
- Centralizar logs, métricas e healthchecks
- Priorizar visualização de logs de container
- Detectar falhas e abrir incidentes
- Executar runbooks com guardrails e auditoria

Stack:
- Backend: Python + FastAPI
- Observabilidade: OpenTelemetry
- Logs: Loki ou CloudWatch
- Métricas: Prometheus ou CloudWatch
- Arquitetura: Clean Architecture

Modelo conceitual:
- Service
- Signal
- Alert
- Incident
- RunbookAction
- RemediationJob

Funcionalidades MVP:
- Service registry
- Logs centralizados por serviço/env
- Health e status
- Incidentes manuais e automáticos
- Timeline de incidentes

Self-healing (controlado):
- Apenas ações allowlisted
- Cooldown obrigatório
- Aprovação manual (MVP2)
- Auditoria completa

Integrações:
- Mnemosyne: publicar incidentes e pós-mortem
- Aegis: receber alertas críticos de qualidade
- AtlasForge: padrões de logging e tracing injetados

Requisitos não funcionais:
- Segurança forte
- Nenhuma ação destrutiva sem auditoria
- Logs estruturados
- Correlação por traceId e correlationId

Siga este fluxo:
1. Definir service registry.
2. Implementar logs e health.
3. Implementar incidentes.
4. Implementar runbooks controlados.
5. Explicar decisões e trade-offs.
