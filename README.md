# EV Charging Network

A full-stack EV charging platform built for a university assignment.
Drivers can find nearby stations, reserve charging slots, monitor a live
charging session, pay, and review history — all through a Tesla/Apple
inspired dark, glassmorphic UI.

**Stack:** FastAPI · SQLModel · PostgreSQL · vanilla HTML/CSS/JS · Docker Compose

---

## Folder Structure

```
project-name/
├── backend/
│   ├── app/
│   │   ├── main.py            # App entrypoint, routers, static mount, seeding
│   │   ├── routers/
│   │   │   ├── auth.py        # Register / login / JWT dependency
│   │   │   ├── users.py       # Profile & vehicles
│   │   │   ├── stations.py    # Station discovery & detail
│   │   │   ├── bookings.py    # Reservations
│   │   │   ├── charging.py    # Live charging session
│   │   │   └── payments.py    # Payments
│   │   ├── models.py          # SQLModel tables
│   │   ├── schemas.py         # Pydantic request/response schemas
│   │   ├── database.py        # Engine & session dependency
│   │   └── crud.py            # CRUD + auth helpers (hashing, JWT)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── index.html
│   ├── pages/                 # login, register, dashboard, stations, ...
│   ├── css/style.css
│   └── js/                    # api.js, auth.js, and one file per page
├── docs/
│   ├── user-journey.md
│   ├── er-diagram.png
│   └── api-spec.md
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## Installation

1. Install [Docker](https://docs.docker.com/get-docker/) and Docker Compose.
2. Clone this repository and enter the project folder.
3. Copy the environment template:
   ```bash
   cp .env.example .env
   ```
4. (Optional) edit `.env` to change the Postgres credentials or JWT secret.

## Run the project

```bash
docker compose up --build
```

This starts two containers:
- **db** — PostgreSQL 16, with a persisted volume
- **backend** — FastAPI app, serving both the REST API and the static frontend

Once both containers report healthy, open:
- **App:** http://localhost:8000
- **Swagger docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

On first boot, the backend automatically creates all tables and seeds:
- 20 charging stations with chargers
- 10 demo users (password: `password123`, e.g. `user1@example.com`)
- sample vehicles, bookings, charging sessions, and payments for `user1`

## Docker commands

| Command | Purpose |
|---|---|
| `docker compose up --build` | Build images and start the stack |
| `docker compose up -d` | Start in the background |
| `docker compose down` | Stop and remove containers |
| `docker compose down -v` | Also wipe the Postgres volume (fresh reseed) |
| `docker compose logs -f backend` | Tail backend logs |

## Running without Docker (optional, for development)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql://ev_user:ev_password@localhost:5432/ev_charging_db
uvicorn app.main:app --reload
```
You'll need a local PostgreSQL instance matching `DATABASE_URL`, and the
`frontend` folder copied/symlinked to `backend/frontend` (or adjust the
static mount path in `app/main.py`) since Docker normally handles that copy.

## API Overview

See [`docs/api-spec.md`](docs/api-spec.md) for the full endpoint reference.
Key routes:

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/register` | Create an account |
| POST | `/api/login` | Authenticate, receive a JWT |
| GET/PUT | `/api/profile` | View/update profile |
| GET | `/api/stations` | Browse stations (search/filter) |
| GET | `/api/stations/{id}` | Station detail + chargers |
| POST/GET | `/api/bookings` | Create/list reservations |
| GET | `/api/charging/status` | Poll live charging session |
| POST | `/api/charging/stop` | Stop a session |
| POST/GET | `/api/payments` | Pay / list payment history |

All endpoints except register/login require a Bearer JWT.

## Authentication

- Passwords are hashed with bcrypt (`passlib`).
- Sessions use signed JWTs (`python-jose`), stored in `localStorage` on
  the frontend and sent as `Authorization: Bearer <token>`.
- Unauthenticated requests to protected pages redirect to `login.html`.

## Notes for graders

- Frontend is intentionally framework-free per the assignment brief:
  plain HTML/CSS/JS served directly by FastAPI's `StaticFiles`.
- `docs/er-diagram.png` was generated from the actual SQLModel schema.
- Mock data is regenerated automatically the first time the `db` volume
  is empty; run `docker compose down -v` to reset and reseed.
