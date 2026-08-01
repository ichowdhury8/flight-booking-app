"""Booking creation and retrieval.

There is no auth: a booking is retrieved solely by its reference code, and anyone
holding a reference can see the passenger names and contact email on it
(PLAN.md A2). No payment is taken and no email is sent — the confirmation page
*is* the confirmation (A3).
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Booking, Flight, Passenger
from ..reference import MAX_ATTEMPTS, generate_reference
from ..schemas import BookingCreate, BookingOut, to_booking_out
from .guides import load_guide

router = APIRouter(prefix="/api/bookings", tags=["bookings"])


@router.post("", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
def create_booking(
    payload: BookingCreate, db: Session = Depends(get_db)
) -> BookingOut:
    flight = db.get(Flight, payload.flight_id)
    if flight is None:
        raise HTTPException(status_code=404, detail="Flight not found.")

    count = len(payload.passengers)
    if flight.seats_available < count:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Only {flight.seats_available} seat(s) left on this flight; "
                f"{count} requested."
            ),
        )

    # Price is snapshotted here and never recomputed from the flight afterwards.
    total_price_minor = flight.price_minor * count

    booking: Booking | None = None
    for _ in range(MAX_ATTEMPTS):
        candidate = Booking(
            reference=generate_reference(),
            flight_id=flight.id,
            contact_email=str(payload.contact_email),
            contact_phone=payload.contact_phone,
            passenger_count=count,
            total_price_minor=total_price_minor,
            currency=flight.currency,
            status="confirmed",
            created_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )
        # A savepoint, so a UNIQUE collision on `reference` costs us this insert
        # rather than the whole transaction.
        savepoint = db.begin_nested()
        db.add(candidate)
        try:
            db.flush()
        except IntegrityError:
            savepoint.rollback()
            continue
        booking = candidate
        break

    if booking is None:
        raise HTTPException(
            status_code=500,
            detail="Could not allocate a booking reference. Please try again.",
        )

    for p in payload.passengers:
        db.add(
            Passenger(
                booking_id=booking.id,
                first_name=p.first_name.strip(),
                last_name=p.last_name.strip(),
                date_of_birth=p.date_of_birth,
            )
        )

    # Known limitation R5: two simultaneous bookings for the last seat can both
    # pass the check above. Accepted — single worker, single process.
    flight.seats_available -= count

    db.commit()
    db.refresh(booking)

    guide = load_guide(db, flight.destination.iata_code)
    return to_booking_out(booking, guide)


@router.get("/{reference}", response_model=BookingOut)
def get_booking(reference: str, db: Session = Depends(get_db)) -> BookingOut:
    booking = (
        db.query(Booking).filter(Booking.reference == reference.upper()).first()
    )
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found.")

    guide = load_guide(db, booking.flight.destination.iata_code)
    return to_booking_out(booking, guide)
