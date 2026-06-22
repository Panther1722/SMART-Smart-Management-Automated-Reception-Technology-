# AI Receptionist Prototype – Chat Booking Demo

This repository contains a working milestone of the project:

**Design and Development of a Single-Hotel AI Receptionist Prototype for Booking Inquiry and Request Handling**

The prototype demonstrates a full-stack conversational flow: a guest chats with an AI receptionist on the frontend, messages are handled by a FastAPI backend, booking details are extracted from the conversation, and every turn is stored in PostgreSQL.

```
Frontend (React chat UI) → FastAPI backend → PostgreSQL database
                              ↓
                    LLM extraction + replies (optional)
                    Rule-based fallback when LLM is off
```

The stack runs in Docker Compose with one command and supports GitHub Codespaces for easy testing.

---

## What this prototype does

- Displays a multilingual chat interface (English, German, French, Italian, Spanish)
- Collects the guest email before chat begins and persists the session in the browser
- Sends messages to `POST /api/chat` and shows assistant replies in real time
- Extracts structured booking fields (dates, guest count, request type, etc.) from conversation
- Uses a hosted LLM (Gemini or OpenAI) when configured, with rule-based replies as fallback
- Stores each message, extracted fields, and AI reply in PostgreSQL
- Restores chat history when the user returns in the same browser tab
- Runs through Docker Compose with one command
- Supports GitHub Codespaces for instructor testing

---

## System flow

1. The user opens the web page and selects a language.
2. The user enters their email and starts a session (`POST /api/session/start`).
3. The user sends chat messages (`POST /api/chat`).
4. The backend merges prior session fields, extracts new details (LLM or rules), and generates a reply.
5. The backend writes the message, extracted fields, and `ai_reply` into `booking_requests`.
6. The frontend displays the assistant reply and loads history on return visits.

For verification, use `GET /api/booking-requests` or `GET /api/chat-history/{session_id}`.

---

## Repository structure

```text
.
├─ backend/
│  ├─ app/
│  │  ├─ __init__.py
│  │  ├─ chat_rules.py          # Rule-based replies when LLM is disabled
│  │  ├─ database.py
│  │  ├─ date_normalization.py
│  │  ├─ extraction_service.py  # LLM + rule extraction orchestration
│  │  ├─ field_extraction.py
│  │  ├─ llm_service.py         # Gemini / OpenAI integration
│  │  ├─ main.py
│  │  ├─ models.py
│  │  ├─ routes.py
│  │  └─ schemas.py
│  ├─ Dockerfile
│  └─ requirements.txt
├─ frontend/
│  ├─ src/
│  │  ├─ App.jsx                # Chat UI, session, i18n
│  │  ├─ main.jsx
│  │  └─ styles.css
│  ├─ index.html
│  ├─ nginx.conf
│  ├─ package.json
│  ├─ vite.config.js
│  └─ Dockerfile
├─ .devcontainer/
│  └─ devcontainer.json
├─ .env.example
├─ docker-compose.yml
└─ README.md
```

---

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/session/start` | Create or update a chat session with guest email |
| `GET` | `/api/session/{session_id}` | Look up a session |
| `POST` | `/api/chat` | Send a message; extract fields and return assistant reply |
| `GET` | `/api/chat-history/{session_id}` | Return messages for a session |
| `POST` | `/api/booking-request` | Direct insert (legacy / testing) |
| `GET` | `/api/booking-requests` | List recent saved requests (JSON) |
| `GET` | `/health` | Health check including LLM configuration status |
| `GET` | `/docs` | FastAPI interactive API documentation |

---

## Run locally with Docker

### Prerequisites

- Docker Desktop or Docker Engine
- Docker Compose support

### Start the project

From the root of the repository:

```bash
docker compose up --build
```

### Open in browser

- Frontend: http://localhost:8080
- Backend docs: http://localhost:8000/docs
- Health (LLM status): http://localhost:8000/health

### Stop the project

```bash
docker compose down
```

To also remove the database volume:

```bash
docker compose down -v
```

---

## Run in GitHub Codespaces

1. Open the repository in GitHub Codespaces.
2. Wait until the dev container finishes loading.
3. In the Codespaces terminal, run:

```bash
docker compose up --build
```

4. Open the forwarded frontend port (8080).
5. Enter your email, start chatting, and send a booking-related message.
6. Verify stored data via `GET /api/booking-requests` or `GET /api/chat-history/{session_id}` in the API docs.

---

## Environment variables

Configuration is handled through environment variables. Copy `.env.example` to `.env` for local overrides.

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string for the backend |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | Database container credentials |
| `FRONTEND_PORT`, `BACKEND_PORT`, `DB_PORT` | Host port mappings |
| `CORS_ALLOW_ORIGINS` | Allowed frontend origins (`*` by default) |
| `LOG_LEVEL` | Backend log level |
| `LLM_ENABLED` | `true` to use hosted LLM; `false` for rule-based replies only |
| `LLM_PROVIDER` | `gemini` or `openai` |
| `LLM_MODEL` | Model name (e.g. `gemini-2.5-flash`) |
| `API_KEY` | Provider API key (also accepts `LLM_API_KEY`, `GEMINI_API_KEY`, `OPENAI_API_KEY`) |
| `LLM_TIMEOUT_SECONDS` | Request timeout for LLM calls |
| `LLM_MAX_HISTORY_MESSAGES` | Max prior turns sent to the LLM |

**Never commit `.env` or API keys to the repository.**

With `LLM_ENABLED=false` (the default), the app still works using rule-based extraction and replies.

---

## Team development workflow and AI tools

This project is developed using a mix of human work and support from AI tools.

### Human responsibilities

- Define project requirements and scope
- Decide the architecture and technology stack
- Review all generated code and configuration
- Run tests and verify that the full flow works
- Decide what is finally committed to the repository

### AI tool support

- Suggest project structure and boilerplate
- Propose backend and frontend implementations
- Help write and refine documentation
- Assist with debugging and troubleshooting
- Suggest simpler alternatives when something is too complex

### How AI is used in practice

AI tools are used to draft code and documentation while the developer focuses on planning and testing. Once a draft is generated, it is reviewed, simplified if needed, and only then added to the project.

### Keeping the project aligned

To keep the project aligned with the proposal and the course requirements:

- The project proposal is used as the main reference for scope and goals
- Milestones are kept testable end-to-end in Docker
- All important changes are reviewed by a human
- Only verified code is included in the submission

### Quality and traceability

Content suggested by AI tools is treated as a draft until it is verified by:

- Running Docker Compose
- Testing the chat flow (email → message → reply)
- Checking saved records in the database
- Reviewing logs and API behavior (`/health`, `/docs`)

Traceability is maintained through repository structure, documented endpoints, version control, and this README.

---

## Prototype and evaluation dimensions

| Dimension | Notes |
|-----------|-------|
| **Performance** | Chat requests involve DB reads/writes; LLM calls are optional and timeout-bounded |
| **Development time** | Modular backend services and a single-page React frontend |
| **Cost** | Open-source stack; LLM usage is optional and provider-billed |
| **Accuracy** | Structured field extraction with session merge; LLM does not confirm bookings |
| **Usability** | Multilingual chat UI with email gate and session restore |
| **Security** | Secrets via environment variables; DB accessed only through the backend |
| **Scalability** | Frontend, backend, and database are separate services |
| **Extensibility** | Clear split between routes, extraction, LLM, and rule-based fallback |
| **Traceability** | Full message history and extracted fields stored per session |

---

## Future roadmap

Next iterations can extend this base by adding:

- Room availability and pricing checks against real inventory
- Staff/admin dashboard for reviewing conversations and requests
- Workflow automation such as email notifications
- Additional channels such as WhatsApp or voice
- Stronger authentication and guest identity verification

---

## Purpose of this milestone

This repository demonstrates a working prototype that is:

- Frontend based (React chat UI)
- Backend connected (FastAPI with session and chat APIs)
- Database integrated (PostgreSQL with sessions and booking requests)
- AI-ready (optional LLM with safe rule-based fallback)
- Containerized (Docker Compose)
- Cloud-deployable and GitHub Codespaces compatible

It serves as the technical foundation for the long-term goal of building a single-hotel AI receptionist system.
