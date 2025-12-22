# 08 — Aegis

## Propósito
Bloquear regressões de qualidade e segurança **antes** do deploy.

## Modelo de domínio
- Policy (versionada)
- Rule (scanner/check)
- ScanRun (execução)
- Finding (resultado, severity, arquivo/linha, fingerprint)
- Baseline (estado aceito)
- Waiver (exceção com expiração, justificativa, owner)

## MVP1
- Pre-commit: checks rápidos (lint/format/secrets)
- CI gate: bloquear findings novos (delta vs baseline)
- Persistir ScanRuns/Findings no MongoDB
- Emitir eventos:
  - `quality.v1.scan_completed`
  - `quality.v1.violation_detected`

## Estado atual
| Área                      | Status | Observações                               |
|---------------------------|--------|-------------------------------------------|
| CLI (scan/persist)        | ✅      | Typer, baseline delta                     |
| Scanners (ruff/black/secrets) | ✅  | Severidades mapeadas                      |
| Mongo repository          | ✅      | Persistência de reports                   |
| Integrações plataforma    | 🚧     | Stubs para Mnemosyne/EyeOfHorusOps        |
| Waivers/CRUD              | ❌     | Planejado para MVP2                       |

## Evoluções
- Painel de políticas
- Learning mode
- Waivers por time e SLA
