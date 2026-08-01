"""Pydantic request/response models, plus the builders that map ORM rows onto them.

The response shapes are deliberately not one-to-one with the tables. Two things
the API never exposes:

  * `airports.utc_offset_minutes` — seed-time only (PLAN.md §2).
  * `flights.seats_total` — an internal number; only `seats_available` is useful
    to a client, and only as a scarcity signal.
"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_serializer

from .models import ArrivalGuide, Booking, Flight

# ---------------------------------------------------------------------------
# Airports
# ---------------------------------------------------------------------------


class AirportOut(BaseModel):
    """Full airport record for the search dropdowns."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    iata_code: str
    name: str
    city: str
    country: str


class AirportBrief(BaseModel):
    """The two fields a flight card actually renders."""

    iata_code: str
    city: str


# ---------------------------------------------------------------------------
# Flights
# ---------------------------------------------------------------------------


class FlightOut(BaseModel):
    id: int
    flight_number: str
    airline: str
    origin: AirportBrief
    destination: AirportBrief
    # Naive local times at their own airport — see models.py.
    departure_at: datetime
    arrival_at: datetime
    duration_minutes: int
    price_minor: int
    currency: str
    seats_available: int


def to_flight_out(flight: Flight) -> FlightOut:
    return FlightOut(
        id=flight.id,
        flight_number=flight.flight_number,
        airline=flight.airline,
        origin=AirportBrief(
            iata_code=flight.origin.iata_code, city=flight.origin.city
        ),
        destination=AirportBrief(
            iata_code=flight.destination.iata_code, city=flight.destination.city
        ),
        departure_at=flight.departure_at,
        arrival_at=flight.arrival_at,
        duration_minutes=flight.duration_minutes,
        price_minor=flight.price_minor,
        currency=flight.currency,
        seats_available=flight.seats_available,
    )


# ---------------------------------------------------------------------------
# Arrival guide
# ---------------------------------------------------------------------------


class AttractionOut(BaseModel):
    name: str
    description: str
    category: str


class TransportOut(BaseModel):
    mode: str
    name: str
    minutes: int
    notes: str | None
    # Local currency at the destination, not USD — deliberate, see PLAN.md A16.
    cost_note: str | None


class GuideAirportOut(BaseModel):
    iata_code: str
    name: str


class GuideOut(BaseModel):
    city: str
    country: str
    airport: GuideAirportOut
    intro: str
    distance_km: float
    transport: TransportOut
    attractions: list[AttractionOut]


def to_guide_out(guide: ArrivalGuide) -> GuideOut:
    return GuideOut(
        city=guide.airport.city,
        country=guide.airport.country,
        airport=GuideAirportOut(
            iata_code=guide.airport.iata_code, name=guide.airport.name
        ),
        intro=guide.intro,
        distance_km=guide.distance_km,
        transport=TransportOut(
            mode=guide.transport_mode,
            name=guide.transport_name,
            minutes=guide.transport_minutes,
            notes=guide.transport_notes,
            cost_note=guide.transport_cost_note,
        ),
        attractions=[
            AttractionOut(
                name=a.name, description=a.description, category=a.category
            )
            for a in guide.attractions
        ],
    )


# ---------------------------------------------------------------------------
# Bookings
# ---------------------------------------------------------------------------


class PassengerIn(BaseModel):
    first_name: str = Field(min_length=1, max_length=60)
    last_name: str = Field(min_length=1, max_length=60)
    date_of_birth: date | None = None


class BookingCreate(BaseModel):
    flight_id: int
    contact_email: EmailStr
    contact_phone: str | None = Field(default=None, max_length=40)
    passengers: list[PassengerIn] = Field(min_length=1, max_length=9)


class PassengerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    first_name: str
    last_name: str


class BookingOut(BaseModel):
    reference: str
    status: str
    created_at: datetime
    total_price_minor: int
    currency: str
    flight: FlightOut
    passengers: list[PassengerOut]
    # None is reachable in principle — the frontend renders the section
    # conditionally so a missing guide degrades quietly (PLAN.md R7).
    arrival_guide: GuideOut | None

    @field_serializer("created_at")
    def _utc_z(self, value: datetime) -> str:
        """created_at is stored naive-UTC; mark it as UTC on the way out."""
        return value.isoformat(timespec="seconds") + "Z"


def to_booking_out(booking: Booking, guide: ArrivalGuide | None) -> BookingOut:
    return BookingOut(
        reference=booking.reference,
        status=booking.status,
        created_at=booking.created_at,
        total_price_minor=booking.total_price_minor,
        currency=booking.currency,
        flight=to_flight_out(booking.flight),
        passengers=[PassengerOut.model_validate(p) for p in booking.passengers],
        arrival_guide=to_guide_out(guide) if guide else None,
    )
