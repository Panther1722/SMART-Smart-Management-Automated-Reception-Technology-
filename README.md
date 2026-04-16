## AI Receptionist Prototype – Booking Request Demo

**Academic project milestone repository** for:

**Design and Development of a Single-Hotel AI Receptionist Prototype for Booking Inquiry and Request Handling**

This first working prototype demonstrates the essential full-stack workflow required for the project:

**Frontend (one button) → FastAPI backend → PostgreSQL database**

This is intentionally minimal and “tomorrow-ready” while setting a clean foundation for later AI receptionist capabilities.

---

## Features

- **One-button booking request submission** from a web page
- **FastAPI backend** with simple REST endpoints
- **PostgreSQL persistence** (`booking_requests` table)
- **Docker Compose one-command run**
- **GitHub Codespaces compatible** via `.devcontainer/`
- **Cloud-deployable structure** (containerized services, env vars, clear ports)
- **Extensible foundation** for future AI receptionist functionality

---

## Architecture (flow)

1. User clicks **“Send Booking Request”**
2. Frontend calls `POST /api/booking-request`
3. Backend validates payload and inserts a row into PostgreSQL
4. Backend returns the saved record (id + timestamp)
5. Frontend shows a success message

Note: The frontend container (Nginx) reverse-proxies `/api/*` to the backend container so the browser can use simple relative URLs.

---

## Repository structure

```
.
├─ backend/
│  ├─ app/
│  │  ├─ __init__.py
│  │  ├─ database.py
│  │  ├─ main.py
│  │  ├─ models.py
│  │  ├─ routes.py
│  │  └─ schemas.py
│  ├─ Dockerfile
│  └─ requirements.txt
├─ frontend/
│  ├─ app.js
│  ├─ index.html
│  ├─ nginx.conf
│  ├─ style.css
│  └─ Dockerfile
├─ .devcontainer/
│  └─ devcontainer.json
├─ .env.example
├─ docker-compose.yml
└─ README.md
```

---

## API endpoints

- **POST** `/api/booking-request`
  - Inserts one booking request row into the database
  - Request body:
    - `message` (string; defaults to `"Booking request submitted from prototype"`)
- **GET** `/api/booking-requests`
  - Lists the latest saved requests (up to 100) for verification
- **GET** `/health`
  - Health check endpoint

FastAPI docs:
- `GET /docs` (also available through the frontend URL because Nginx proxies `/docs`)

---

## How to run locally (Docker)

### Prerequisites

- Docker Desktop (or Docker Engine) with Compose support

### Run

From the repo root:

```bash
docker compose up --build
```

Open:
- Frontend: `http://localhost:8080`
- Backend docs: `http://localhost:8080/docs` (proxied) or `http://localhost:8000/docs`

### Stop

```bash
docker compose down
```

To also remove the database volume (danger: deletes saved requests):

```bash
docker compose down -v
```

---

## How to run in GitHub Codespaces (instructor steps)

1. Open this repository in **GitHub Codespaces**
2. Wait for the dev container to finish initializing
3. In the Codespaces terminal, run:

```bash
docker compose up --build
```

4. Open the forwarded port for the frontend (**8080**) in the browser
5. Click **“Send Booking Request”**
6. Verify persistence (optional):
   - Open `GET /api/booking-requests` from the frontend footer link, or
   - Open `GET /docs` and try the endpoints

---

## Environment variables

This repo is safe-by-default for a prototype: no secrets are committed.

- Use `.env.example` as a template if you want to override ports or DB settings.
- Docker Compose provides defaults if `.env` is not present.

Key variables:
- `DATABASE_URL` (backend)
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` (db)
- `FRONTEND_PORT`, `BACKEND_PORT`, `DB_PORT` (host port mapping)

---

## AI-assisted team development workflow (mandatory)

This project is developed by a **hybrid team** consisting of human contributors and AI agents. The goal is to accelerate delivery while maintaining correctness, alignment with requirements, and academic traceability.

### Human responsibilities

- **Requirements & scope**: define “tomorrow’s submission” criteria and keep the scope minimal
- **Architecture decisions**: select stack (FastAPI + Postgres + Docker) and ensure extensibility for later AI features
- **Verification**: run the app, click the button, confirm DB writes, check endpoints
- **Review & approval**: review AI-generated code for correctness, security hygiene, and clarity before submission

### AI agent responsibilities

- **Boilerplate generation**: scaffold Docker Compose, FastAPI project structure, and static frontend
- **Implementation drafting**: propose clean minimal endpoints, DB model, and startup logic
- **Documentation**: draft `README.md`, run instructions, and verification steps
- **Debug assistance**: help diagnose container/networking/CORS issues and propose fixes quickly
- **Refactoring**: remove unnecessary complexity and keep the prototype readable

### Asynchronous AI usage

- AI agents can draft code, documentation, and alternative designs in parallel while humans validate requirements and prepare submission artifacts.
- Work can proceed “unattended” for short intervals (e.g., generating a clean repo skeleton), then humans validate and integrate results.

### Direction control (staying aligned)

- The team keeps alignment via:
  - proposal-based requirements (this milestone = one-button write-through demo)
  - small, reviewable changes
  - clear repository structure
  - human approval before merging or submitting

### Quality control

- AI output is treated as a **draft** until verified by:
  - running Docker Compose
  - manual UI click testing
  - checking `GET /api/booking-requests`
  - reviewing logs for errors

### Traceability

- Traceability is maintained using:
  - commit history and PR-style discipline (even in small teams)
  - explicit mapping from requirements → endpoints/data model
  - this README as a “living specification” for the milestone

---

## Optimization dimensions (prototype mapping)

- **Performance**: simple synchronous DB insert; minimal UI; low overhead services.
- **Development Time**: static frontend + FastAPI + Compose keeps build time short and predictable.
- **Cost**: runs on a small VM/container host; Postgres + Python are cost-effective for prototypes.
- **Accuracy**: deterministic request insertion; no AI/LLM variability in this milestone.
- **Usability**: one clear action button, plus immediate success/failure feedback.
- **Security**: env-based configuration, no secrets in repo; minimal attack surface; CORS configurable (default permissive for demo).
- **Scalability**: containerized services; can scale backend horizontally behind a proxy later.
- **Extensibility/Maintainability**: clean separation (`frontend/`, `backend/`), simple DB model, minimal but structured code.
- **Traceability**: explicit endpoints, simple schema, and documentation of flow and responsibilities.

---

## Future roadmap (next milestones)

Later versions may add:

- conversational AI layer (intent detection + responses)
- room availability and pricing checks
- richer booking inquiry capture (dates, guests, preferences)
- admin dashboard for staff review
- optional automation helpers (e.g., n8n notifications) as non-critical add-ons
- extra channels (WhatsApp, voice)

