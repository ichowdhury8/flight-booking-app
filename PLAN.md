# Flight Booking App — Implementation Plan (rev. 4)

**Stack:** FastAPI + SQLite/SQLAlchemy + React (Vite), single deployable service on Render free tier.
**Budget:** 2.5 days (~20 working hours).
**Status:** plan for review — no code written yet. Awaiting your confirmation before task 1.

**Changes in rev. 4:** R12, R13 and R10 all resolved and folded in. `utc_offset_minutes` is now a
committed part of the schema; Barcelona's transfer is the Aerobús (`bus`); the seed emits 2–3 departures
per route per day, varying by time, carrier and price, for **1,120 flights**.

**Carried forward:** deploy proven first; seed content generated and fact-checked by you; empty search
results eliminated by exhaustive seeding; `static/` committed to git; demo video and documentation as
deliverables; design tokens fixed to your palette with the serif confined to four places.

**No open decisions remain.** Every risk is either closed or accepted as a known limitation.

---

## 1. Architecture in one paragraph

One FastAPI process. It serves `/api/*` JSON routes and mounts the compiled Vite bundle at `/` as static
files, with an SPA fallback so client-side routes reload correctly. SQLite file on local disk, opened via
SQLAlchemy ORM. On startup, if the database is empty, a seed module populates airports, flights, arrival
guides and attractions. No background workers, no auth, no external calls at runtime. One repo, one
process, one Render web service.

Deliberate omissions to protect the 2.5-day budget: no user accounts, no payment, no email delivery, no
seat maps, no return or multi-city flights, no admin UI, no test suite beyond a handful of endpoint
smoke tests.

---

## 2. Database schema

Six tables, all with `INTEGER PRIMARY KEY AUTOINCREMENT`. Flight times are stored as **naive local
datetimes at the relevant airport**, computed correctly at seed time — see A4.

### `airports`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | |
| `iata_code` | TEXT, UNIQUE, NOT NULL | e.g. `ATL`. Indexed. |
| `name` | TEXT NOT NULL | e.g. `Hartsfield–Jackson` |
| `city` | TEXT NOT NULL | e.g. `Atlanta` |
| `country` | TEXT NOT NULL | e.g. `United States` |
| `utc_offset_minutes` | INTEGER NOT NULL | Hard-coded summer offset. **Seed-time only** — never read at request time, never exposed by the API. |

### `flights`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | |
| `flight_number` | TEXT NOT NULL | e.g. `DL84` |
| `airline` | TEXT NOT NULL | e.g. `Delta Air Lines` |
| `origin_id` | INTEGER FK → `airports.id`, NOT NULL | Indexed |
| `destination_id` | INTEGER FK → `airports.id`, NOT NULL | Indexed |
| `departure_at` | DATETIME NOT NULL | naive local time at origin. Indexed. |
| `arrival_at` | DATETIME NOT NULL | naive local time at destination, offset-corrected at seed time |
| `duration_minutes` | INTEGER NOT NULL | precomputed — no timezone maths anywhere at request time |
| `price_minor` | INTEGER NOT NULL | **US cents.** Integer, never float. |
| `currency` | TEXT NOT NULL DEFAULT `'USD'` | ISO 4217 |
| `seats_total` | INTEGER NOT NULL | |
| `seats_available` | INTEGER NOT NULL | decremented on booking |

Composite index on `(origin_id, destination_id, departure_at)` — the search query's exact shape. At 1,120
rows this is the difference between a scan and a seek on the app's hottest query.

### `arrival_guides`

One row per destination airport. The custom feature's spine.

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | |
| `airport_id` | INTEGER FK → `airports.id`, **UNIQUE**, NOT NULL | one guide per airport |
| `intro` | TEXT NOT NULL | 1–2 sentence orientation line for the city |
| `distance_km` | REAL NOT NULL | airport → city centre. Displayed in miles with km — see A15. |
| `transport_mode` | TEXT NOT NULL | constrained in app code to `train` / `metro` / `taxi` / `bus` |
| `transport_name` | TEXT NOT NULL | e.g. `MARTA Gold/Red Line`, `Aerobús A1/A2` |
| `transport_minutes` | INTEGER NOT NULL | approximate journey time |
| `transport_notes` | TEXT | e.g. `Station is inside the domestic terminal, before you exit.` |
| `transport_cost_note` | TEXT | free text, **in the destination's local currency** — see A16 |

### `attractions`

3–4 rows per guide. A separate table rather than a JSON blob, so the guide renders from a plain join and
stays queryable.

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | |
| `guide_id` | INTEGER FK → `arrival_guides.id`, NOT NULL | Indexed |
| `name` | TEXT NOT NULL | e.g. `Musée d'Orsay` |
| `description` | TEXT NOT NULL | one sentence, ~15–25 words |
| `category` | TEXT NOT NULL | `landmark` / `museum` / `food` / `outdoors` / `neighbourhood` |
| `sort_order` | INTEGER NOT NULL | display order within the guide |

### `bookings`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | |
| `reference` | TEXT, UNIQUE, NOT NULL | 6-char code, e.g. `K7HP2Q`. Indexed. |
| `flight_id` | INTEGER FK → `flights.id`, NOT NULL | |
| `contact_email` | TEXT NOT NULL | |
| `contact_phone` | TEXT | optional |
| `passenger_count` | INTEGER NOT NULL | denormalised for convenience |
| `total_price_minor` | INTEGER NOT NULL | US cents, snapshot at time of booking — not recomputed |
| `currency` | TEXT NOT NULL | snapshot |
| `status` | TEXT NOT NULL DEFAULT `'confirmed'` | only ever `confirmed` in v1 |
| `created_at` | DATETIME NOT NULL | UTC, server-generated |

### `passengers`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | |
| `booking_id` | INTEGER FK → `bookings.id`, NOT NULL | Indexed |
| `first_name` | TEXT NOT NULL | |
| `last_name` | TEXT NOT NULL | |
| `date_of_birth` | DATE | optional in v1 |

**Reference code generation:** 6 characters from `ABCDEFGHJKLMNPQRTUVWXYZ2346789` — 30 characters, with
both halves of each ambiguous pair removed (`0/O`, `1/I`, `5/S`). Generate, attempt insert, retry up to 5
times on the UNIQUE constraint. 30⁶ ≈ 729 million.

> Corrected at task 16. Earlier revisions gave the alphabet as
> `ABCDEFGHJKLMNPQRSTUVWXYZ23456789`, which still contained `S` and `5` and so contradicted the stated
> rule beside it. The implementation follows the rule; a test asserts it.

---

## 3. Seed data

### Cities — 6

| IATA | City | Country | UTC offset | Mode | Transfer |
|---|---|---|---|---|---|
| `ATL` | Atlanta | United States | −240 | `metro` | MARTA Gold/Red to Five Points, ~20 min |
| `LHR` | London | United Kingdom | +60 | `train` | Heathrow Express to Paddington, ~15 min |
| `CDG` | Paris | France | +120 | `train` | RER B to Gare du Nord, ~45 min |
| `BCN` | Barcelona | Spain | +120 | `bus` | **Aerobús A1/A2** to Plaça de Catalunya, ~35 min |
| `AMS` | Amsterdam | Netherlands | +120 | `train` | Mainline train to Centraal, ~17 min |
| `LIS` | Lisbon | Portugal | +60 | `metro` | Metro red line, ~20 min |

Mode coverage is train ×3, metro ×2, bus ×1. `taxi` goes unused, by your decision: a correct dataset
beats a fully-exercised enum. The app-level constraint still permits `taxi` for future cities.

### Flights — 1,120 rows

6 cities → **30 ordered routes** (6 × 5), **14 days** (today + 0..13), **2–3 departures per route per
day**, split on realistic grounds:

| Route class | Routes | Departures/day | Rows |
|---|---|---|---|
| Intra-European (5 cities → 5 × 4) | 20 | 3 | 840 |
| Transatlantic (ATL ↔ 5 cities) | 10 | 2 | 280 |
| | **30** | | **1,120** |

Short-haul European city pairs genuinely run more daily frequencies than transatlantic ones, so this is
realism rather than an arbitrary split.

Every attribute derives **deterministically** from `(route, day_offset, slot)` — no unseeded `random` —
so two seed runs produce identical data and a demo recorded Monday still matches Tuesday.

**Departure slots.** Chosen so each route's daily set spans the day rather than clustering:

- *Intra-European (3 slots):* early morning ~06:50–08:10, midday ~12:20–13:40, evening ~18:30–20:00.
- *Transatlantic westbound (Europe → ATL, 2 slots):* late morning and early afternoon, ~10:00–13:00 —
  these land in Atlanta the same afternoon once the −5/−6h offset is applied.
- *Transatlantic eastbound (ATL → Europe, 2 slots):* evening, ~17:00–19:30 — overnight, landing in
  Europe the following morning. This is how the real schedules work, and it only reads correctly
  because of the offset fix below.

**Arrival**, computed at seed time and stored:

```
arrival_at = departure_at + duration_minutes
             − origin.utc_offset_minutes
             + destination.utc_offset_minutes
```

Nothing at request time touches offsets; `duration_minutes` is displayed directly. Summer offsets are
hard-coded and DST transitions ignored, which is safe for a 14-day window that is reseeded on every cold
start (A4).

**Price — the trade-off the results list is built to show.** A per-route base fare, modulated by slot
and then by day:

- Early morning: **~0.85×** — cheapest, least convenient.
- Midday: **~1.15×** — most expensive, most convenient.
- Evening: **~0.95×**.
- Transatlantic overnight: **~0.90×** against the daytime option.
- Then ±25% by day offset, so the cheap slot isn't the cheapest on literally every date.

Base fares span roughly **$55** (LIS–BCN) to **$780** (ATL–AMS).

**Other per-flight variation**, so a route's daily set doesn't look cloned:

- **Airline** varies by slot — each route has up to two plausible carriers, so the results list offers a
  carrier choice as well as a time and price choice.
- **Flight number** = carrier prefix + a stable number from route index and slot.
- **Duration** varies 0–15 min by slot off the per-route base (different aircraft, different routings).
- **Seats** — `seats_total` 120–180; `seats_available` runs lower on the cheaper slots, which is both
  realistic and a quiet nudge toward the trade-off.

Per-route base durations are hand-authored across 15 city pairs, applied symmetrically, in two bands:
intra-European ~1h15–2h45 and transatlantic ~8h–10h. Inserted with a single `bulk_save_objects` call.

### Guides — 6 guides, ~21 attractions

One guide per airport, 3–4 attractions each. **I generate this content**; you fact-check distances,
transport modes, service names and journey times before it ships. Atlanta you verify first-hand. See R4
and A13 — the fact-check gates the demo video, not the code.

### Seeding strategy

On FastAPI startup: `create_all()`, then `if session.query(Airport).count() == 0: seed()`. Idempotent,
no migration tooling, no Alembic. Also runnable as `python -m app.seed` for local resets.

---

## 4. API endpoints

All under `/api`. All responses JSON. All amounts in **USD cents**. Errors use FastAPI's default
`{"detail": ...}` shape.

### `GET /api/health`
→ `200 {"status": "ok"}`. Render's health check, and the entire payload of the first deploy (task 2).

### `GET /api/airports`
Populates both search dropdowns. Sorted by city. `utc_offset_minutes` is seed-time only and is not
exposed.
```json
[{ "id": 1, "iata_code": "ATL", "name": "Hartsfield–Jackson", "city": "Atlanta", "country": "United States" }]
```

### `GET /api/flights/search`
Query params: `origin` (IATA), `destination` (IATA), `date` (`YYYY-MM-DD`), `passengers` (int, default 1).

- `400` if origin == destination.
- `422` if the date is malformed (FastAPI handles this).
- Filters to `seats_available >= passengers`.
- **Ordered by `departure_at` ascending.** No sort control in v1 — with 2–3 results, chronological is
  the clearest default and a sort UI would be clutter against the design direction.
- Returns `200 []` if nothing matches. With exhaustive seeding plus a bounded date picker this is
  unreachable in normal use, but endpoint and UI both still handle it.

```json
[{
  "id": 7,
  "flight_number": "DL84",
  "airline": "Delta Air Lines",
  "origin": { "iata_code": "ATL", "city": "Atlanta" },
  "destination": { "iata_code": "CDG", "city": "Paris" },
  "departure_at": "2026-08-04T16:40:00",
  "arrival_at": "2026-08-05T07:15:00",
  "duration_minutes": 515,
  "price_minor": 64200,
  "currency": "USD",
  "seats_available": 34
}]
```
`price_minor: 64200` → `$642.00`. Departs Atlanta 4:40 PM, lands Paris 7:15 AM next day: 8h35 in the air
across a +6h offset. That arrival is only correct because of the seed-time offset computation.

### `GET /api/flights/{flight_id}`
Same shape as one search result. Used by the passenger-details page so a refresh or a shared link works
without depending on router state. `404` if unknown.

### `POST /api/bookings`
Request:
```json
{
  "flight_id": 7,
  "contact_email": "a@b.com",
  "contact_phone": "+1...",
  "passengers": [
    { "first_name": "Ada", "last_name": "Lovelace", "date_of_birth": "1815-12-10" }
  ]
}
```
Validation (Pydantic): ≥1 passenger, ≤9 passengers, non-empty names, `EmailStr` for the email.

Server-side: `404` if the flight doesn't exist; `409` if `seats_available < len(passengers)`; otherwise
create booking + passengers, decrement seats, commit — one transaction.

Response `201` — the full confirmation payload, so the frontend needs no second request:
```json
{
  "reference": "K7HP2Q",
  "status": "confirmed",
  "created_at": "2026-07-31T14:02:11Z",
  "total_price_minor": 128400,
  "currency": "USD",
  "flight": { ...full flight object... },
  "passengers": [{ "first_name": "Ada", "last_name": "Lovelace" }],
  "arrival_guide": { ...guide object below... }
}
```
`128400` → `$1,284.00`: two passengers at `$642.00`.

### `GET /api/bookings/{reference}`
Identical payload to the POST response. Makes the confirmation URL reloadable and shareable. `404` on
unknown reference.

### `GET /api/guides/{iata_code}`
Standalone guide lookup. Not needed by the happy path, but it keeps the Arrival Guide independently
testable.
```json
{
  "city": "Barcelona",
  "country": "Spain",
  "airport": { "iata_code": "BCN", "name": "El Prat" },
  "intro": "...",
  "distance_km": 15.0,
  "transport": {
    "mode": "bus",
    "name": "Aerobús A1/A2",
    "minutes": 35,
    "notes": "Departs outside both terminals every 5–10 minutes; pay on board or at the stop.",
    "cost_note": "~€7.25 one way"
  },
  "attractions": [
    { "name": "...", "description": "...", "category": "landmark" }
  ]
}
```
`404` if the airport has no guide.

### Static serving
Registered **after** all API routes — ordering matters, since a `/` mount registered first swallows
`/api/*`:
```
app.mount("/assets", StaticFiles(directory="static/assets"))
# catch-all GET route returning static/index.html for anything not under /api
```
The catch-all must not intercept `/api/*` 404s — those stay JSON. At task 2 `static/` doesn't exist yet,
so the mount is guarded by an existence check; that guard stays permanently, since it's also what lets
the backend run alone in local development.

---

## 5. Frontend

### 5.1 Design tokens and type

Built against your exact values. Four are given; the rest are derived and marked as such.

```css
/* Given */
--accent:        #0F5257;   /* deep teal   */
--bg:            #FAF8F5;   /* warm off-white */
--text:          #1A1A17;   /* body text   */
--border:        #E8E3DB;   /* hairlines   */

/* Derived — proposed, adjustable at task 9 */
--surface:       #FFFFFF;   /* cards, lifting off the warm page */
--text-muted:    #6B6862;   /* captions, secondary metadata */
--accent-hover:  #0A3D41;   /* button hover / pressed */
--accent-wash:   #EDF2F1;   /* the one tinted block: TransferCallout background */
--border-strong: #8A8378;   /* input outlines only — see the contrast note */
--focus-ring:    #0F5257 at 40% opacity, 3px, offset 2px
--radius-sm: 6px;  --radius-md: 10px;
--shadow: 0 1px 2px rgba(26,26,23,.04), 0 8px 24px rgba(26,26,23,.06);
--space: 4 / 8 / 12 / 16 / 24 / 32 / 48 / 64 / 96px
```

**Contrast, computed:** `--accent` on `--bg` is **8.38:1**; white on `--accent` is **8.88:1**;
`--text` on `--bg` is **16.4:1**. All comfortably AA, most AAA.

One finding worth acting on: `--border` on `--bg` is **1.20:1**. That is correct and handsome for
decorative hairlines and card edges, and below the **3:1** WCAG 1.4.11 wants for the boundary of an
interactive control. So form inputs get `--border-strong` (**3.54:1**) and everything else keeps
`--border`. Without this split, the inputs are pretty and effectively invisible.

**Fonts** — one Google Fonts request, `preconnect` to `fonts.gstatic.com`, `display=swap`:

```
https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@400;500;600&display=swap
```

Instrument Serif ships one weight (400) plus an italic; all emphasis comes from size, never from bold.
Inter carries 400/500/600.

**Where Instrument Serif is used — the complete list. Nothing else.**

| Element | Font | Size |
|---|---|---|
| `<Hero>` h1 on SearchPage | **Instrument Serif** | 56px / 1.05 / −0.01em |
| `<GuideHeader>` destination city name | **Instrument Serif** | 40px / 1.1 / −0.01em |
| `<ConfirmationHeader>` h1 ("You're booked") | **Instrument Serif** | 40px / 1.1 |
| `<NotFoundPage>` h1 | **Instrument Serif** | 40px / 1.1 |

**Everything else is Inter.** Explicitly, and these are exactly the places a global
`h1,h2,h3 { font-family: serif }` rule would wrongly capture:

- The **booking reference code** — Inter 600, tabular figures, generous letter-spacing. It is an
  alphanumeric string a human will read aloud or type; a display serif is actively harmful here.
- **Flight times, dates, durations, prices, airport codes** — Inter with `font-variant-numeric:
  tabular-nums` so columns align. This matters more now that each results list stacks 2–3 cards whose
  times and prices should read as a column.
- **Every section heading** — "Your itinerary", "Passengers", "Getting into the city". These are h2/h3.
  **Rule: `h1` is serif, `h2` and below are Inter 600.**
- **All form labels, inputs, placeholders, validation text, buttons.**
- **All of `<FlightCard>`**, including the airline name.
- **All of `<TransferCallout>`** — distance, mode, journey time, notes.
- **`<AttractionCard>` names and descriptions.** Attraction names are the most tempting place to reach
  for the serif, and your instruction is city name only. They stay Inter 600.

Implementation: no global heading rule at all. `--font-display` is applied by a single `.display` class,
used in exactly the four places above, so nothing can inherit it by accident.

**Inter scale:** 32 / 24 / 20 / 16 / 14 / 12px, line-height 1.5 body and 1.25 headings.

### 5.2 Component tree

Routing via `react-router-dom`, four routes. State lives in the URL — reloads and shared links work for
free, no global state library.

```
<App>
├── <Header/>                        wordmark only, no nav
├── <Routes>
│   ├── "/"                <SearchPage>
│   │                      ├── <Hero/>                      ← serif h1
│   │                      ├── <SearchForm>                 syncs to ?origin=&destination=&date=&passengers=
│   │                      │   ├── <AirportSelect/> × 2      from GET /api/airports
│   │                      │   ├── <DateField/>              min=today, max=today+13 — see R6
│   │                      │   ├── <PassengerStepper/>
│   │                      │   └── <Button variant="primary"/>
│   │                      └── <ResultsSection>
│   │                          ├── <ResultsHeader/>          "3 flights · Atlanta → Paris · Tue, Aug 4"
│   │                          ├── <FlightCard/> × 2–3       chronological; all Inter, tabular figures
│   │                          │   └── <FlightTimeline/>     dep — duration — arr
│   │                          ├── <EmptyState/>             defensive fallback only
│   │                          └── <Skeleton/> while loading
│   │
│   ├── "/book/:flightId"  <PassengerPage>
│   │                      ├── <StepIndicator step={2}/>
│   │                      ├── <FlightSummaryCard/>          refetched via GET /api/flights/:id
│   │                      ├── <PassengerForm>
│   │                      │   ├── <PassengerFieldset/> × n  n from ?passengers=
│   │                      │   └── <ContactFieldset/>
│   │                      ├── <PriceSummary/>               n × fare = total, USD
│   │                      └── <Button>Confirm booking</Button>
│   │
│   ├── "/booking/:reference"  <ConfirmationPage>
│   │                      ├── <ConfirmationHeader/>         ← serif h1; the code itself is Inter
│   │                      ├── <ItineraryCard/>
│   │                      ├── <PassengerList/>
│   │                      └── <ArrivalGuide>                ← the custom feature
│   │                          ├── <GuideHeader/>            ← serif city name, the second serif moment
│   │                          ├── <TransferCallout/>        --accent-wash block; all Inter
│   │                          └── <AttractionList>
│   │                              └── <AttractionCard/> × 3–4
│   │
│   └── "*"                <NotFoundPage/>
└── <Footer/>
```

**Shared primitives** (`src/components/ui/`): `Button`, `Field`, `Card`, `Skeleton`, `ErrorBanner`,
`Spinner`.
**Non-component modules:** `src/api/client.js` (one `request()` wrapper plus endpoint functions),
`src/lib/format.js` (USD from cents via `Intl.NumberFormat`, duration as `8h 35m`, dates, km→miles).

`<FlightCard>` now carries a real comparison job: departure and arrival times, duration, carrier, price,
and an unobtrusive seats-remaining note when it's low. Keeping those five facts legible in a single
scannable row, at three cards deep, is the main typographic problem of task 10.

Vanilla CSS with custom properties plus a few `.module.css` files. No Tailwind, no CSS-in-JS.

---

## 6. File / folder structure

```
flight-booking-app/
├── app/
│   ├── __init__.py
│   ├── main.py                 FastAPI app, startup seed hook, static mount, SPA fallback
│   ├── database.py             engine, SessionLocal, Base, get_db dependency
│   ├── models.py               6 SQLAlchemy models
│   ├── schemas.py              Pydantic request/response models
│   ├── reference.py            booking reference generator
│   ├── routers/
│   │   ├── airports.py
│   │   ├── flights.py
│   │   ├── bookings.py
│   │   └── guides.py
│   └── seed/
│       ├── __init__.py
│       ├── content.py          6 cities, 6 guides, ~21 attractions, per-route durations and base fares
│       ├── flights.py          the 30 × 14 × (2–3) generation loop
│       └── run.py              idempotent seeding entrypoint
├── frontend/
│   ├── package.json
│   ├── vite.config.js          build.outDir = "../static", proxy /api → :8000 in dev
│   ├── index.html              font preconnect + single Google Fonts link
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── api/client.js
│       ├── lib/format.js
│       ├── styles/{tokens.css,global.css}
│       ├── components/
│       │   ├── ui/{Button,Field,Card,Skeleton,ErrorBanner}.jsx
│       │   ├── Header.jsx  Footer.jsx  StepIndicator.jsx
│       │   ├── search/{SearchForm,AirportSelect,FlightCard,EmptyState}.jsx
│       │   ├── booking/{FlightSummaryCard,PassengerForm,PriceSummary}.jsx
│       │   └── guide/{ArrivalGuide,TransferCallout,AttractionCard}.jsx
│       └── pages/{SearchPage,PassengerPage,ConfirmationPage,NotFoundPage}.jsx
├── static/                     ← Vite build output, COMMITTED TO GIT. Not ignored. See R3.
├── tests/test_api.py           ~8 smoke tests
├── docs/demo-script.md         shot list and narration for the demo video
├── deploy.sh                   build → add static/ → commit → push, as one step (R9)
├── requirements.txt
├── render.yaml
├── .gitignore
└── README.md
```

**`.gitignore` — explicit contents**, since getting this wrong breaks the deploy:

```
.venv/
__pycache__/
*.pyc
node_modules/
flights.db
.DS_Store
```

`static/` is deliberately absent. Committing build output is unusual and will look wrong to anyone
reading the repo, so the README explains it in one line.

Dev loop: `uvicorn app.main:app --reload` on :8000 and `npm run dev` on :5173, Vite proxying `/api` to
:8000. Production: one process. Same-origin in both, so CORS never enters the picture.

---

## 7. Build order and time estimates

Deploy is task 2 — before any model exists — because it's the only task that can fail for reasons
outside your code.

### Day 1 (8:00)

| # | Task | Est. |
|---|---|---|
| 1 | Repo scaffold: venv, `requirements.txt`, `.gitignore` (per §6), FastAPI app exposing only `GET /api/health` | 0:30 |
| 2 | **Deploy to Render.** `render.yaml`, Python-only build command, health check path, first push, verify the live URL returns `{"status":"ok"}`. **Checkpoint — nothing proceeds past a green health check without checking in with you.** | 1:00 |
| 3 | Vite app scaffold, dev proxy, confirm the React dev server reaches the local API | 0:30 |
| 4 | `models.py` + `database.py` — six tables, relationships, indexes | 1:15 |
| 5 | **Generate seed content** — 6 cities, 6 guides, ~21 attractions, per-route durations and base fares | 0:45 |
| 6 | Flight generation loop (30 × 14 × 2–3), offset-corrected arrivals, slot/price/carrier variation, seed runner, startup hook; verify 1,120 rows, idempotency, and spot-check a transatlantic arrival by hand | 1:15 |
| 7 | API: `/health`, `/airports`, `/flights/search`, `/flights/{id}` + Pydantic schemas | 1:30 |
| 8 | API: `POST /bookings`, `GET /bookings/{ref}`, `GET /guides/{iata}`, reference generator, seat decrement | 1:15 |

**End of day 1:** live deployed URL, complete backend verifiable through Swagger UI.
**Your task, in parallel:** fact-check the generated guide content. This gates task 18.

### Day 2 (7:15)

| # | Task | Est. |
|---|---|---|
| 9 | Design tokens per §5.1, global styles, font loading, layout shell, UI primitives. Verify the serif lands in exactly four places. | 1:30 |
| 10 | `SearchPage` — form, airport selects, bounded date picker, URL-synced params, results list, loading state | 2:00 |
| 11 | `PassengerPage` — flight summary, dynamic passenger fieldsets, client-side validation, price summary | 2:00 |
| 12 | `ConfirmationPage` — reference display, itinerary, passenger list | 1:00 |
| 13 | **Second deploy** via `deploy.sh`; verify the full app live including a deep link | 0:45 |

**End of day 2:** the whole happy path working on the live URL. Arrival Guide functional but unstyled.

### Day 3 — half day (4:45)

| # | Task | Est. |
|---|---|---|
| 14 | **Arrival Guide UI** — serif city name, `--accent-wash` transfer callout, attraction cards | 1:30 |
| 15 | Polish: typographic rhythm, spacing, responsive to 375px, focus states, error banners | 1:00 |
| 16 | Smoke tests (~8: search, booking, retrieval, guide, the 409 path) | 0:30 |
| 17 | README + `docs/demo-script.md` | 0:30 |
| 18 | **Demo video** — shot list, warm the instance, record, re-takes, trim under 2:30 | 1:00 |
| 19 | Final `deploy.sh` run and a full walkthrough of the live URL | 0:15 |

**Total: 20:00 against a 20:00 budget.** That is not slack, it's an exact fit, and estimates are
estimates — so the cut list below is load-bearing rather than contingency. Expect to use some of it.
Cut in this order: (1) passenger date of birth, (2) `StepIndicator`, (3) smoke tests, (4) drop the
flight window from 14 days to 7 — halves the seed to 560 rows and changes nothing else, (5) drop
intra-European routes to 2 departures/day, which costs the comparison story on short-haul but keeps it
transatlantic.

### Demo video — shot list (task 18)

Under 2:30, no audio required. Seven beats:

1. Live URL loads, clean landing page, serif hero — 0:10
2. Pick origin, destination, date — 0:20
3. Results appear — three flights, visibly different times and prices — 0:15
4. Select a flight, land on passenger details — 0:15
5. Fill passenger and contact details — 0:30
6. Confirm → reference code, large and legible — 0:20
7. **Scroll to the Arrival Guide** — city name, transfer callout, attractions. The differentiator; give
   it the most time — 0:35

Practical notes: hit the URL a minute beforehand so R2's cold start doesn't open the video with a
50-second blank page. Record with QuickTime (`⌘⇧5`) at a fixed, tidy window size. **Use Atlanta as the
destination** — it's the guide you can personally vouch for, and an inbound transatlantic leg shows off
the overnight arrival. Budget covers two or three takes.

---

## 8. Risks

### Closed

- **R1 — ephemeral disk, accepted.** Re-seed on startup. Bookings persist only for the life of the
  instance; flight dates stay permanently fresh.
- **R2 — cold starts, accepted.** ~50s after ~15 min idle. Matters for the demo recording.
- **R3 — `static/` committed, build command Python-only.** No dependency on Node in Render's build
  image. `static/` absent from `.gitignore`, spelled out in §6.
- **R4 — seed content generated, fact-check is the control.** Risk moved from schedule to accuracy.
  Atlanta you verify first-hand.
- **R5 — seat race condition, accepted as a known limitation.** Two simultaneous bookings for the last
  seat can both succeed. Effectively impossible on a single-worker instance. Documented in the README,
  not fixed.
- **R6 — empty results eliminated.** All 30 routes populated on all 14 days, date picker bounded to
  match, same-city rejected in form and API. `EmptyState` survives as a defensive fallback.
- **R7 — guide coverage.** All six airports have guides. The frontend still renders the section
  conditionally so a missing guide degrades quietly.
- **R8 — one-way flights only.** Confirmed.
- **R9 — stale committed `static/`.** Mitigated by `deploy.sh` making build-add-commit-push atomic.
- **R10 — resolved.** 2–3 departures per route per day, varying by time, carrier and price, so the
  results list presents a genuine trade-off rather than a single card.
- **R11 — seeding on every cold start.** Now 1,120 rows rather than 420. Still a single
  `bulk_save_objects` and still expected well under a second against an already ~50s cold start.
  Measured once at task 6 rather than assumed.
- **R12 — resolved.** `utc_offset_minutes` on `airports`, arrivals computed at seed time. Transatlantic
  legs now display correct local arrival times.
- **R13 — resolved.** Barcelona is `bus` (Aerobús). Lisbon stays `metro` on accuracy grounds. `taxi`
  unused and that's fine.

### Accepted, non-blocking

- **R14 — Google Fonts is a runtime network dependency.** Your offline constraint was about the guide
  data, and the fonts load in the browser rather than on the server, so this doesn't violate it as
  written. If the fonts fail to load the page falls back to system serif and sans and the design loses
  much of its character. Self-hosting both families as woff2 in `static/` costs ~15 minutes and
  slightly improves first paint — a reasonable day-3 upgrade if time allows, but it is below the cut
  line, not above it.

---

## 9. Assumptions to verify

- **A1 — One-way flights only.** No return, multi-city, or connections. *(Confirmed.)*
- **A2 — No authentication, no accounts.** A booking is retrieved solely by its reference code. Anyone
  with a reference can view that booking, including passenger names and contact email.
- **A3 — No payment and no email.** The confirmation page *is* the confirmation. The UI must not imply
  a card was taken.
- **A4 — Timezones handled at seed time only.** *(Confirmed.)* Hard-coded summer UTC offsets produce
  correct local arrival times. DST transitions within the 14-day window are ignored; offsets would be
  wrong if the app ran across a DST boundary, which R1's per-cold-start reseed makes unreachable in
  practice. No timezone library, no offsets at request time.
- **A5 — Currency is USD**, stored as integer cents, no conversion. *(Confirmed.)*
- **A6 — Fares are per passenger and flat.** Total = fare × passenger count. No taxes, fees, child
  fares, or cabin classes. More conspicuous at $642 than it was at £89.
- **A7 — Flight metadata is plausible fiction.** Carriers, flight numbers, schedules and frequencies are
  generated to look realistic; they do not correspond to real services. Only the *guide* content is
  intended to be factually accurate (A13).
- **A8 — The bookable window is exactly 14 days**, today + 0..13, reseeded on every cold start, with the
  date picker bounded to match.
- **A9 — Desktop-first, mobile-responsive.** Laid out for desktop, verified down to 375px.
- **A10 — Modern browsers only.** No IE, no polyfills, ES2020+ output.
- **A11 — Passenger date of birth is optional** and unvalidated beyond being a date.
- **A12 — Design tokens fixed to your palette and pairing.** *(Confirmed; see §5.1.)* The four given
  values are used verbatim. The derived tokens — `--surface`, `--text-muted`, `--accent-hover`,
  `--accent-wash`, `--border-strong` — are my proposals and are the one place I'd expect you to want
  adjustments at task 9. The `h1` = serif, `h2` and below = Inter split is my reading of "page
  headings".
- **A13 — Generated guide content is a draft until you check it.** Distances, transport modes, service
  names, journey times and cost notes come from general knowledge: approximately right, not
  authoritative. Atlanta you verify directly; the other five need your review between task 5 and task
  18. The UI labels distances and journey times as approximate regardless.
- **A14 — Times display in 12-hour format with AM/PM** (`4:40 PM`), dates as `Tue, Aug 4`, given a
  US-based audience and USD pricing. A formatter change if you'd rather have 24-hour.
- **A15 — Distances display in miles with km in parentheses** (`10 mi (16 km)`). Stored as km in
  `distance_km`; converted in `format.js`.
- **A16 — Guide transport costs stay in the destination's local currency** — `~$2.50` for MARTA,
  `~€7.25` for the Aerobús, `~£25` for the Heathrow Express. Converting them to USD would be actively
  misleading, since you pay them at the destination in local money. Deliberate, and independent of A5.

---

## 10. Definition of done

- Live Render URL, deployed from a Python-only build command, with no API keys anywhere in the codebase
  or environment.
- Search a route and date → 2–3 flights, chronological, with visibly different times, carriers and
  prices.
- Transatlantic arrival times are correct in destination local time.
- Select a flight → passenger details form validating on both client and server.
- Submit → confirmation page with a reference code, itinerary, and passenger list.
- Confirmation page shows the Arrival Guide: 3–4 attractions, distance to the city centre, and the
  recommended transport with journey time — all read from SQLite, with no runtime external calls.
- Reloading `/booking/{reference}` works, as does a deep link into any route.
- Instrument Serif appears in exactly the four places listed in §5.1 and nowhere else.
- All amounts in USD, formatted from integer cents.
- Guide content fact-checked and accepted by you.
- `README.md` covers setup, the dev loop, the `deploy.sh` procedure, and known limitations.
- Demo video recorded, under 2:30, covering the seven beats in §7.
