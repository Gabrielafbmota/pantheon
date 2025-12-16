# 06 — Pantheon (Orquestrador)

## Missão
Pantheon é o **núcleo de governança e orquestração** do ecossistema. Ele define:
- contratos
- catálogo de sistemas
- catálogo de eventos
- padrões de observabilidade e auditoria

## Não-responsabilidades
- Não executa o domínio dos sistemas
- Não substitui Aegis/Mnemosyne/EyeOfHorusOps/AtlasForge
- Não “vira monólito”

## Interfaces
- API (admin): registry, contratos, health do ecossistema
- Eventos: publicação e validação (catálogo)

## MVP1 (Pantheon)
- Registry de serviços (nome, owner, env, endpoints)
- Catálogo de eventos (schema + versão + exemplos)
- Convecções globais (IDs, headers, logging)

## Evoluções
- Dashboard unificado
- Governance-as-code transversal
- Policy engine para contratos (ex: eventos proibidos sem schema)
