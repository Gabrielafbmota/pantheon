# Arquitetura (Mermaid)

```mermaid
graph TD
    User -->|Telegram| Bot
    User -->|Web/PWA| Frontend
    Bot --> API
    Frontend --> API
    API --> MongoDB
    API --> GoogleBooks
    API --> OpenLibrary
    API --> Storage[S3/Drive (opcional)]
```
