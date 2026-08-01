# Meridian — flight booking demo

Search one-way flights across six cities, book them, and get an **Arrival Guide**
for your destination: how to get from the airport into the city, how long it
takes, roughly what it costs, and three or four things worth doing when you land.

**Live:** https://flight-booking-app-zr2v.onrender.com

One FastAPI process serves both the JSON API under `/api/*` and the compiled
React bundle at `/`. Same origin in development and production alike, so CORS
never enters the picture. Data lives in SQLite and is seeded at startup — there
are **no API keys anywhere in this repo or its environment, and nothing calls an
external service at runtime.**

---

## Stack

| | |
|---|---|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2, SQLite |
| Frontend | React 19, Vite, react-router-dom, vanilla CSS with custom properties |
| Hosting | Render free tier, deployed from `render.yaml` |

No Tailwind, no CSS-in-JS, no state management library — page state lives in the
URL, so a reload or a shared link reproduces exactly what you were looking at.

---

## Running it locally

```bash
# Backend — http://127.0.0.1:8000
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --reload

# Frontend — http://localhost:5173, proxying /api to :8000
cd frontend
npm install
npm run dev
```

The database is created and seeded on first start. To reset it:

```bash
rm flights.db && .venv/bin/python -m app.seed.run
```

### Tests

```bash
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
```

Fifteen endpoint tests covering search, booking, retrieval, guides and the
error branches. They build and seed their own throwaway database via
`FLIGHTS_DB_PATH` and never touch your working `flights.db`.

---

## Deploying

```bash
./deploy.sh "Optional commit message"
```

That builds the frontend, commits the output, and pushes — in one step, on
purpose. See "Why `static/` is committed" below.

---

## Two things that will look wrong at first glance

### Why `static/` is committed to git

Build output in version control is normally a mistake. Here it is deliberate.

Render's build command is `pip install -r requirements.txt` — Python only. It
never runs `npm`, never needs Node in the build image, and cannot fail because
of a frontend toolchain problem. The cost is that the built bundle has to come
from somewhere, so it is committed.

The risk this creates is a stale `static/` deployed against newer source. That
is why `deploy.sh` exists and why build-add-commit-push is a single command
rather than four things to remember. `static/` is conspicuously absent from
`.gitignore`, and both `.gitignore` files carry a note saying not to add it.

### Why bookings disappear

Render's free tier has an ephemeral filesystem. Every deploy and every cold
start gives the instance a fresh disk, so `flights.db` is recreated and reseeded
from scratch.

Flights are regenerated relative to *today*, which means the fourteen-day
booking window is always current and a demo recorded last week still works this
week. Bookings, though, only live as long as the instance does. A booking
reference will stop resolving after the next restart. For a persistent database
this would need a Render disk or a managed Postgres; for a demo, permanently
fresh flight dates are the better trade.

---

## How the data works

Six airports, and every ordered pair between them is a route — 30 routes. Each
is populated on all fourteen days of the window, at two or three departures a
day, for **1,120 flights**. Intra-European routes get three departures; the
longer transatlantic ones get two, which is roughly how the real schedules run.

Every attribute derives deterministically from `(route, day, slot)`. There is no
unseeded randomness anywhere, so two seed runs on the same day produce identical
data and a recorded demo keeps matching what the app shows.

Because every route is populated on every day, and the date picker is bounded to
exactly that window, **a search cannot return nothing**. The empty state exists
as a defensive fallback and should be unreachable in normal use.

### Timezones

Flight times are stored as naive local datetimes at their own airport, and
`duration_minutes` is precomputed. All the offset arithmetic happens **once, at
seed time**:

```
arrival_at = departure_at + duration_minutes
             - origin.utc_offset_minutes
             + destination.utc_offset_minutes
```

Nothing at request time touches a timezone. This matters most on transatlantic
legs: an evening departure from Atlanta lands in Europe the following morning,
and computing it naively would show the arrival six hours early — plausible
enough that nothing else would flag it.

Summer offsets are hard-coded and DST transitions ignored, which is safe for a
fourteen-day window that is reseeded on every cold start.

### Money

Every amount is an integer count of US cents, everywhere, end to end. Never a
float. Fares are flat per passenger — no taxes, fees, child fares or cabin
classes are modelled, and the UI says so rather than implying otherwise.

Guide transport costs are the exception, and stay in the destination's **local**
currency: `~$2.50` for MARTA, `~€7.25` for the Aerobús, `~£25` for the Heathrow
Express. Converting those to USD would be actively misleading, since you pay
them at the destination in local money.

---

## API

| Method | Path | |
|---|---|---|
| `GET` | `/api/health` | Render's health check |
| `GET` | `/api/airports` | Populates both search dropdowns |
| `GET` | `/api/flights/search` | `?origin=&destination=&date=&passengers=` |
| `GET` | `/api/flights/{id}` | One flight, for the passenger-details page |
| `POST` | `/api/bookings` | Returns the full confirmation payload, guide included |
| `GET` | `/api/bookings/{reference}` | Same payload — makes the URL reloadable |
| `GET` | `/api/guides/{iata_code}` | Standalone guide lookup |

Interactive docs at `/docs` on any running instance.

Two fields are deliberately never exposed: `airports.utc_offset_minutes`, which
is seed-time only, and `flights.seats_total`, which is internal.

---

## Known limitations

- **No accounts and no authentication.** A booking is retrieved solely by its
  reference code, so anyone holding a reference can see the passenger names and
  contact email on that booking.
- **No payment and no email.** The confirmation page *is* the confirmation.
- **Seat race condition, accepted.** Two simultaneous bookings for the last seat
  can both succeed — the check and the decrement are not atomic against
  concurrent writers. Effectively unreachable on a single-worker instance, and
  not worth the complexity here.
- **One-way flights only.** No returns, multi-city or connections.
- **Flight data is plausible fiction.** Carriers, flight numbers, schedules and
  fares are generated to look realistic and do not correspond to real services.
  The *guide* content is the part intended to be factually accurate.
- **Guide content is general knowledge.** Distances, journey times and fares are
  approximate and labelled as such in the UI.
- **Google Fonts is a runtime network dependency** for the browser. The offline
  constraint was about guide data, which is served from SQLite; if the fonts
  fail to load the page falls back to system serif and sans.
- **Modern browsers only.** ES2020+, no polyfills.

---

## Layout

```
app/
  main.py          FastAPI app, startup seed, static mount, SPA fallback
  database.py      engine, session factory, get_db dependency
  models.py        six SQLAlchemy models
  schemas.py       Pydantic request/response models and ORM -> response builders
  reference.py     booking reference generator
  routers/         airports, flights, bookings, guides
  seed/
    content.py     airports, guides, attractions, per-route durations and fares
    flights.py     the 30 x 14 x (2-3) generation loop
    run.py         idempotent seeding entrypoint
frontend/          Vite React app; builds to ../static
static/            build output — COMMITTED, see above
tests/test_api.py  endpoint smoke tests
docs/              demo script
deploy.sh          build, commit and push in one step
PLAN.md            the implementation plan this was built from
```
