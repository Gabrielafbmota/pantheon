# ADR 0001 — Pantheon como orquestrador

## Contexto
Precisamos de coesão entre múltiplos sistemas internos, evitando decisões divergentes.

## Decisão
Adotar **Pantheon** como camada de governança e catálogo (sistemas + eventos), sem concentrar domínio.

## Alternativas
- Sem orquestrador (alto risco de divergência)
- Orquestrador monolítico (alto acoplamento)

## Consequências
- Padrões centralizados e auditáveis
- Menor acoplamento por contratos versionados
