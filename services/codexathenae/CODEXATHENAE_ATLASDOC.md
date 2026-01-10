# 🏛️ CODEXATHENAE — ATLASDOC (DOCUMENTO ÚNICO)

**Plataforma Unificada de Catálogo, Leitura Ativa e Inteligência de Leitura**  
**Módulo interno:** Kallioreader  
**Status:** MVP0 real + evolução planejada  
**Data:** 2026-01-09

---

## 📌 Premissas Críticas (NÃO NEGOCIÁVEIS)

- ✅ Nenhum dado atual é perdido
- ✅ A collection `books` existente é mantida e apenas **expandida**
- ✅ O frontend e o bot passam a depender **exclusivamente da API**
- ✅ Inclui **script de ingestão** do `codexathenae.books.json`
- ✅ Inclui **Prompt Final de Desenvolvimento** ajustado para Raspberry Pi (arm64)
- ✅ **Leitura ≠ Catálogo**
- ✅ **Modelo Book é imutável** (estado de leitura vive em `reading`)
- ✅ Sem microserviços

---

## 1. Visão Geral

### 1.1 O que é o CodexAthenae

O **CodexAthenae** é uma plataforma única que integra:

- 📚 Catálogo canônico de livros
- 🧾 Ingestão (JSON, ISBN, UI, APIs públicas)
- 📖 Leitura ativa (EPUB / PDF) via **Kallioreader**
- ✍️ Highlights e notas (desacoplados do catálogo)
- 📊 Análise de hábitos e métricas
- 🧠 Base sólida para IA (apenas dados derivados)

> **Leitura não contamina o Book.**  
> **IA não escreve no domínio.**  
> **Tudo que o Front/Bot faz passa pela API.**

---

## 2. MVP0 — Estado Atual (REAL)

### 2.1 Já existe hoje

- Frontend React em produção (dark mode, cards)
- MongoDB com dados reais
- Collection `books` populada (principalmente Google Books)
- Navegação lateral funcional

### 2.2 Estrutura atual da collection `books` (preservada)

```json
{
  "id": "uuid",
  "title": "The Hobbit",
  "authors": ["J. R. R. Tolkien"],
  "publishedDate": "2009-04-20",
  "publishDate": "1938-01-01",
  "description": "This is the story...",
  "imageLinks": "http://books.google.com/...",
  "isbn": "9780345445605",
  "genre": "Fiction"
}
```

✅ **Esses dados são preservados integralmente.**

---

## 3. Arquitetura

### 3.1 Princípios

- DDD com **Bounded Contexts**
- Clean Architecture
- Offline-first (PWA/Android)
- Eventual consistency
- IA-ready (sem acoplamento prematuro)

### 3.2 Bounded Contexts

| Contexto | Responsabilidade |
|---|---|
| `books` | Catálogo, metadados, deduplicação |
| `reading` | Progresso e sessões (Kallioreader) |
| `highlights` | Marcações e notas |
| `users` | Identidade e preferências |
| `insights` | Métricas/IA derivadas (read-only) |

### 3.3 Diagrama geral

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

---

## 4. Clean Architecture

- **Domain**: entidades, regras, contratos (sem dependência externa)
- **Application**: casos de uso (orquestra domain + infraestrutura)
- **Infrastructure**: MongoDB (Motor), clients externos, storage
- **Presentation**: FastAPI (REST), autenticação, validação

Estrutura alvo:

```text
backend/src/codexathenae/
├── domain/
├── application/
├── infrastructure/
└── presentation/
```

---

## 5. Modelo de Dados

### 5.1 `books` — mantida + expandida

```json
{
  "id": "uuid",
  "title": "string",
  "authors": ["string"],
  "isbn": "string",
  "genre": "string",
  "description": "string",
  "imageLinks": "string",
  "publishedDate": "string",
  "publishDate": "string",
  "publisher": "string",
  "tags": ["string"],
  "rating": 4.5,
  "metadata": {
    "source": "google_books|open_library|manual|import_json",
    "source_id": "string",
    "fetched_at": "datetime"
  },
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

**Regras**  
- `books` representa **apenas catálogo**  
- Nenhum progresso/sessão aqui  
- Deduplicação por `isbn` e fallback `title+authors` (normalizado)

### 5.2 `reading` (Kallioreader)

**`reading_progress`**

```json
{
  "book_id": "uuid",
  "user_id": "uuid",
  "percent": 0.0,
  "epub_cfi": "string|null",
  "pdf_page": 1,
  "pdf_scroll_y": 1200,
  "last_read_at": "datetime",
  "updated_at": "datetime"
}
```

**`reading_sessions`**

```json
{
  "id": "uuid",
  "book_id": "uuid",
  "user_id": "uuid",
  "started_at": "datetime",
  "ended_at": "datetime|null",
  "duration_seconds": 600,
  "device": "web|pwa|android",
  "source": "epub|pdf"
}
```

### 5.3 `highlights`

```json
{
  "id": "uuid",
  "book_id": "uuid",
  "user_id": "uuid",
  "text": "string",
  "note": "string|null",
  "locator_type": "epub_cfi|pdf_page",
  "locator_value": "string",
  "created_at": "datetime"
}
```

### 5.4 `users`

- JWT (access + refresh)
- preferências (tema, metas, IA)
- scopes por usuário

### 5.5 `insights` (DERIVADO)

- streak
- tempo/sessão
- páginas/min
- estagnação (>N dias)
- micro-metas

> `insights` é read-only e recalculável.

---

## 6. Pipeline de Conhecimento

```mermaid
graph LR
    A[Entrada: ISBN / Título / JSON / UI] --> B[Normalização]
    B --> C[Deduplicação]
    C --> D[Enriquecimento (APIs + LLM opcional)]
    D --> E[Persistência MongoDB]
    E --> F[Indexação/Busca]
```

---

## 7. Contratos de API (mínimo viável)

### Books

- `GET /books`
- `GET /books/{id}`
- `POST /books`
- `PUT /books/{id}`
- `DELETE /books/{id}`
- `POST /import/books` (ingestão JSON)

### Reading

- `POST /reading/progress`
- `GET /reading/progress/{book_id}`
- `POST /reading/sessions/start`
- `POST /reading/sessions/end`

### Highlights

- `POST /highlights`
- `GET /highlights/{book_id}`

### Files (opcional no MVP0)

- `POST /files/upload`
- `GET /files/{file_id}`

---

## 8. Frontend (React + Vite + Tailwind)

### Telas

1. Dashboard (KPIs do catálogo + insights)
2. Biblioteca (grid de cards)
3. Detalhes do livro
4. Reader (EPUB)
5. Reader (PDF)
6. Highlights/Notas

### Offline-first

- IndexedDB
- Sync queue resiliente
- Resolução de conflitos por `updated_at` (server-wins por padrão)

---

## 9. Bot (Telegram) — Cliente da API

- não acessa MongoDB
- não chama Google Books diretamente
- apenas consome API:
  - buscar
  - criar livro (ISBN/título)
  - consultar detalhes
  - registrar progresso (opcional)
  - registrar highlight (opcional)

---

## 10. Requisitos Não Funcionais

| Categoria | Requisito |
|---|---|
| Infra | Raspberry Pi (arm64) |
| Deploy | Docker Compose |
| DB | MongoDB (Atlas ou local) |
| Logs | loguru |
| Testes | pytest (backend) / vitest (frontend, opcional) |
| Segurança | JWT + CORS restrito + validação |
| Observabilidade | EyeOfHorusOps |

---

## 11. Como rodar (referência)

Veja o `README_TECHNICO.md` deste pacote.

---

## 🧠 Prompt Final de Desenvolvimento (Raspberry Pi)

> “Implemente o CodexAthenae conforme este AtlasDoc único. Mantenha `Book` imutável; leitura e progresso em bounded context `reading`; offline-first no frontend; bot e frontend dependem exclusivamente da API; Clean Architecture; MongoDB com Motor; logs com loguru; testes com pytest; deploy com Docker Compose compatível com arm64 (Raspberry Pi).”
