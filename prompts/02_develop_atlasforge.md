# Prompt — Desenvolver AtlasForge

Você é um assistente especialista em automação de projetos (Python CLI, Clean Architecture, templates).

Quero implementar o **AtlasForge** em `services/atlasforge/` usando **Poetry**.

MVP1 obrigatório:
- CLI completo: gerar projeto + habilitar módulos + upgrade (dry-run)
- Templates híbridos (estrutura em código + conteúdo em templates)
- Geração de placeholders de integração (Aegis/Mnemosyne/EyeOfHorusOps/Pantheon)

Requisitos:
- Idempotência (mesmo input => mesmo output)
- Sem sobrescrever arquivos do usuário silenciosamente
- Manifesto de template e ProjectSpec versionados
- Testes automatizados (pytest) para geração e upgrade

Siga o fluxo:
1) Estrutura de pastas
2) Modelos (ProjectSpec/TemplateManifest/PatchSet)
3) Implementar geração, depois módulos, depois upgrade
4) Testes e trade-offs
