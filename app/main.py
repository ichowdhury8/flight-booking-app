"""Flight booking app.

Task 2 scaffold: health check only. Models, routers, seeding and the static
mount for the built frontend all arrive in later tasks — the point of this
step is to prove the Render deploy in isolation, before any of our own code
can be the reason it fails.
"""

from fastapi import FastAPI

app = FastAPI(title="Flight Booking App")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
