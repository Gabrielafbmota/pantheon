# Pipeline de Conhecimento (Mermaid)

```mermaid
graph LR
    A[Entrada: ISBN / Título / JSON / UI] --> B[Normalização]
    B --> C[Deduplicação]
    C --> D[Enriquecimento (APIs + LLM opcional)]
    D --> E[Persistência MongoDB]
    E --> F[Indexação/Busca]
```
