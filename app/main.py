"""Flight booking app — FastAPI entrypoint.

One process serving both halves: `/api/*` JSON routes and the compiled Vite
bundle at `/`. Same-origin in dev and prod alike, so CORS never enters the
picture.

On startup the database is created and, if empty, seeded. On Render the disk is
ephemeral so this happens on every cold start — see PLAN.md R1.
"""

import logging
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .routers import airports, bookings, flights, guides
from .seed.run import seed_if_empty

logger = logging.getLogger("uvicorn.error")

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


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


# ---------------------------------------------------------------------------
# Static frontend.
#
# Registered AFTER every API router — ordering is load-bearing. A catch-all
# mounted at "/" before the routers would swallow all of /api/*.
#
# The whole block is guarded on static/ existing, which is what lets the backend
# run on its own in local development (and is why the task 2 deploy could ship
# before the frontend existed).
# ---------------------------------------------------------------------------

if STATIC_DIR.is_dir():
    app.mount(
        "/assets",
        StaticFiles(directory=STATIC_DIR / "assets"),
        name="assets",
    )

    @app.get("/{full_path:path}")
    def spa_fallback(full_path: str) -> FileResponse:
        """Serve index.html for client-side routes so deep links reload.

        Unmatched /api/* paths must NOT land here — an API 404 stays JSON
        rather than becoming a 200 with an HTML body, which would be far
        harder to debug from the client.
        """
        if full_path == "api" or full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not Found")

        if full_path:
            candidate = (STATIC_DIR / full_path).resolve()
            # Confine to STATIC_DIR: full_path is attacker-controlled and could
            # otherwise walk out of the directory with "..".
            if candidate.is_file() and candidate.is_relative_to(STATIC_DIR):
                return FileResponse(candidate)

        return FileResponse(STATIC_DIR / "index.html")

else:  # pragma: no cover - local backend-only development
    logger.warning(
        "static/ not found — serving the API only. Run `npm run build` in "
        "frontend/ to generate it."
    )
