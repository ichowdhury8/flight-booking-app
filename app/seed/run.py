"""Idempotent seeding entrypoint.

Called on FastAPI startup, and runnable directly for a local reset:

    python -m app.seed.run          # seed if empty
    python -m app.seed.run --force  # drop everything and reseed

The guard is `airports.count() == 0`, so a warm instance restarting does not
duplicate rows. On Render the disk is ephemeral and this runs on every cold
start, which is what keeps the 14-day flight window permanently fresh (R1).
"""

import sys
from datetime import date

from sqlalchemy.orm import Session

from ..database import Base, SessionLocal, engine
from ..models import Airport, ArrivalGuide, Attraction
from .content import AIRPORTS, GUIDES
from .flights import generate_flights


def seed(db: Session, today: date | None = None) -> dict[str, int]:
    """Populate airports, guides, attractions and flights. Assumes empty tables."""
    today = today or date.today()

    airports = [Airport(**a) for a in AIRPORTS]
    db.add_all(airports)
    db.flush()  # assign ids without committing — flights need them below

    by_code = {a.iata_code: a for a in airports}

    attraction_count = 0
    for code, spec in GUIDES.items():
        guide = ArrivalGuide(
            airport_id=by_code[code].id,
            intro=spec["intro"],
            distance_km=spec["distance_km"],
            transport_mode=spec["transport_mode"],
            transport_name=spec["transport_name"],
            transport_minutes=spec["transport_minutes"],
            transport_notes=spec["transport_notes"],
            transport_cost_note=spec["transport_cost_note"],
        )
        db.add(guide)
        db.flush()
        for order, item in enumerate(spec["attractions"]):
            db.add(
                Attraction(
                    guide_id=guide.id,
                    name=item["name"],
                    description=item["description"],
                    category=item["category"],
                    sort_order=order,
                )
            )
            attraction_count += 1

    flights = generate_flights(by_code, today)
    db.bulk_save_objects(flights)
    db.commit()

    return {
        "airports": len(airports),
        "guides": len(GUIDES),
        "attractions": attraction_count,
        "flights": len(flights),
    }


def seed_if_empty() -> dict[str, int] | None:
    """Startup hook. Creates tables, then seeds only if there is nothing there."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Airport).count() > 0:
            return None
        return seed(db)
    finally:
        db.close()


def main() -> None:
    if "--force" in sys.argv:
        Base.metadata.drop_all(bind=engine)
        print("dropped all tables")

    counts = seed_if_empty()
    if counts is None:
        print("database already seeded — nothing to do")
    else:
        print(
            "seeded: "
            + ", ".join(f"{v} {k}" for k, v in counts.items())
        )


if __name__ == "__main__":
    main()
