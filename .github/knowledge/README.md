# Knowledge base index (espelho de `.claude`)

Este diretório fornece um índice e ponteiros rápidos para os arquivos de conhecimento e prompts mantidos em `.claude/`.

## Por que existe
Algumas interfaces e integrações (GitHub UI, ações, bots) leem conteúdo dentro de `.github/`. Em vez de duplicar todo o conteúdo, este README centraliza acesso e descrições e aponta para os arquivos canonicamente mantidos em `.claude/`.

## Localizações principais (consulte sempre a versão canônica em `.claude/`)

- `.claude/CLAUDE.md` — Documento canônico com arquitetura, padrões e decisões.
- `.claude/project-knowledge/` — Conhecimento do projeto (políticas, arquitetura, NFRs, roadmap).
  - `aegis-policies.md` — Políticas e padrões de qualidade/segurança (Aegis).
  - `architecture.md` — Visão arquitetural e decisões de alto nível.
  - `atlasforge-spec.md` — Especificações do AtlasForge.
  - `mnemosyne-ai-rag.md` — Notas sobre estratégia RAG para Mnemosyne.
  - `nfrs.md` — Non-functional requirements.
  - `roadmap.md` — Roadmap do projeto.
- `.claude/prompts/` — Prompts canônicos por sistema (ex.: `mnemosyne.md`, `aegis.md`).

## Como usar
- Leia `CLAUDE.md` antes de fazer mudanças arquiteturais.
- Quando precisar de um prompt ou orientação para agente, consulte `.claude/prompts/`.
- Se for necessário expor parte do conteúdo para workflows GitHub (ex.: Actions que consomem prompts), copie apenas os arquivos necessários para `.github/` e documente a razão neste README.

> Observação: a fonte da verdade é `.claude/` — mantenha-a atualizada e registre alterações via PR.
