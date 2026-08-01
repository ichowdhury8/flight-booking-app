"""The six SQLAlchemy models described in PLAN.md §2.

Two conventions worth stating once, because they are load-bearing everywhere else:

1. All money is an integer count of US cents (`*_minor`). Never a float.
2. All flight datetimes are naive *local* times at the relevant airport. The
   offset arithmetic that makes that true happens once, at seed time, in
   app/seed/flights.py. Nothing at request time touches a timezone.
"""

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Airport(Base):
    __tablename__ = "airports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    iata_code: Mapped[str] = mapped_column(String(3), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    city: Mapped[str] = mapped_column(String, nullable=False)
    country: Mapped[str] = mapped_column(String, nullable=False)

    # Hard-coded summer offset. Seed-time only: used to compute arrival_at, then
    # never read again. Deliberately absent from every API response schema.
    utc_offset_minutes: Mapped[int] = mapped_column(Integer, nullable=False)

    guide: Mapped["ArrivalGuide | None"] = relationship(back_populates="airport")


class Flight(Base):
    __tablename__ = "flights"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    flight_number: Mapped[str] = mapped_column(String, nullable=False)
    airline: Mapped[str] = mapped_column(String, nullable=False)

    origin_id: Mapped[int] = mapped_column(
        ForeignKey("airports.id"), nullable=False, index=True
    )
    destination_id: Mapped[int] = mapped_column(
        ForeignKey("airports.id"), nullable=False, index=True
    )

    departure_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    arrival_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)

    price_minor: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")

    seats_total: Mapped[int] = mapped_column(Integer, nullable=False)
    seats_available: Mapped[int] = mapped_column(Integer, nullable=False)

    # foreign_keys is required: there are two FKs to the same table, so SQLAlchemy
    # cannot infer which one each relationship should join on.
    origin: Mapped["Airport"] = relationship(foreign_keys=[origin_id], lazy="joined")
    destination: Mapped["Airport"] = relationship(
        foreign_keys=[destination_id], lazy="joined"
    )

    # The search query's exact shape — WHERE origin AND destination AND date range.
    __table_args__ = (
        Index("ix_flights_route_departure", "origin_id", "destination_id", "departure_at"),
    )


class ArrivalGuide(Base):
    __tablename__ = "arrival_guides"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    airport_id: Mapped[int] = mapped_column(
        ForeignKey("airports.id"), unique=True, nullable=False
    )

    intro: Mapped[str] = mapped_column(Text, nullable=False)
    distance_km: Mapped[float] = mapped_column(Float, nullable=False)

    # Constrained in app code, not by the DB, to train/metro/taxi/bus.
    transport_mode: Mapped[str] = mapped_column(String, nullable=False)
    transport_name: Mapped[str] = mapped_column(String, nullable=False)
    transport_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    transport_notes: Mapped[str | None] = mapped_column(Text)
    # Local currency at the destination, not USD — see PLAN.md A16.
    transport_cost_note: Mapped[str | None] = mapped_column(String)

    airport: Mapped["Airport"] = relationship(back_populates="guide", lazy="joined")
    attractions: Mapped[list["Attraction"]] = relationship(
        back_populates="guide",
        order_by="Attraction.sort_order",
        lazy="selectin",
    )


class Attraction(Base):
    __tablename__ = "attractions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    guide_id: Mapped[int] = mapped_column(
        ForeignKey("arrival_guides.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)

    guide: Mapped["ArrivalGuide"] = relationship(back_populates="attractions")


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    reference: Mapped[str] = mapped_column(
        String(6), unique=True, nullable=False, index=True
    )
    flight_id: Mapped[int] = mapped_column(ForeignKey("flights.id"), nullable=False)

    contact_email: Mapped[str] = mapped_column(String, nullable=False)
    contact_phone: Mapped[str | None] = mapped_column(String)

    passenger_count: Mapped[int] = mapped_column(Integer, nullable=False)
    # Snapshot at time of booking. Never recomputed from the flight's current price.
    total_price_minor: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)

    status: Mapped[str] = mapped_column(String, nullable=False, default="confirmed")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    flight: Mapped["Flight"] = relationship(lazy="joined")
    passengers: Mapped[list["Passenger"]] = relationship(
        back_populates="booking", lazy="selectin"
    )


class Passenger(Base):
    __tablename__ = "passengers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    booking_id: Mapped[int] = mapped_column(
        ForeignKey("bookings.id"), nullable=False, index=True
    )
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    date_of_birth: Mapped[date | None] = mapped_column(Date)

    booking: Mapped["Booking"] = relationship(back_populates="passengers")
