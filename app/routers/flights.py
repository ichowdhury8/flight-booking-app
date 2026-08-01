"""Flight search and lookup."""

from datetime import date, datetime, time

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, aliased

from ..database import get_db
from ..models import Airport, Flight
from ..schemas import FlightOut, to_flight_out

router = APIRouter(prefix="/api/flights", tags=["flights"])


@router.get("/search", response_model=list[FlightOut])
def search_flights(
    origin: str = Query(min_length=3, max_length=3, description="Origin IATA code"),
    destination: str = Query(
        min_length=3, max_length=3, description="Destination IATA code"
    ),
    date_: date = Query(alias="date", description="Departure date, YYYY-MM-DD"),
    passengers: int = Query(default=1, ge=1, le=9),
    db: Session = Depends(get_db),
) -> list[FlightOut]:
    origin = origin.upper()
    destination = destination.upper()

    if origin == destination:
        raise HTTPException(
            status_code=400, detail="Origin and destination must be different."
        )

    origin_airport = aliased(Airport)
    dest_airport = aliased(Airport)

    # departure_at is a naive local datetime, so "on this date" is a half-open
    # range over the day rather than a function call on the column — which also
    # keeps the composite (origin, destination, departure_at) index usable.
    day_start = datetime.combine(date_, time.min)
    day_end = datetime.combine(date_, time.max)

    rows = (
        db.query(Flight)
        .join(origin_airport, Flight.origin_id == origin_airport.id)
        .join(dest_airport, Flight.destination_id == dest_airport.id)
        .filter(
            origin_airport.iata_code == origin,
            dest_airport.iata_code == destination,
            Flight.departure_at >= day_start,
            Flight.departure_at <= day_end,
            Flight.seats_available >= passengers,
        )
        .order_by(Flight.departure_at.asc())
        .all()
    )

    return [to_flight_out(f) for f in rows]


@router.get("/{flight_id}", response_model=FlightOut)
def get_flight(flight_id: int, db: Session = Depends(get_db)) -> FlightOut:
    flight = db.get(Flight, flight_id)
    if flight is None:
        raise HTTPException(status_code=404, detail="Flight not found.")
    return to_flight_out(flight)
