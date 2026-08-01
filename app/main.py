"""Flight booking app — FastAPI entrypoint.

One process. `/api/*` JSON routes now; the compiled Vite bundle gets mounted at
`/` at task 13. That mount must be registered *after* the API routers, since a
`/` mount registered first would swallow `/api/*`.

On startup the database is created and, if empty, seeded. On Render the disk is
ephemeral so this happens on every cold start — see PLAN.md R1.
"""

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .routers import airports, bookings, flights, guides
from .seed.run import seed_if_empty

logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    started = time.perf_counter()
    counts = seed_if_empty()
    elapsed_ms = (time.perf_counter() - started) * 1000
    if counts is None:
        logger.info("Database already seeded (%.0f ms)", elapsed_ms)
    else:
        logger.info(
            "Seeded %s (%.0f ms)",
            ", ".join(f"{v} {k}" for k, v in counts.items()),
            elapsed_ms,
        )
    yield


app = FastAPI(title="Flight Booking App", lifespan=lifespan)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(airports.router)
app.include_router(flights.router)
app.include_router(bookings.router)
app.include_router(guides.router)
