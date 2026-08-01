"""The flight generation loop: 30 ordered routes × 14 days × 2–3 departures.

Every attribute derives deterministically from `(route_index, day_offset, slot)`.
There is no unseeded `random` anywhere, so two seed runs on the same day produce
byte-identical data and a demo recorded on Monday still matches on Tuesday.

The one piece of real arithmetic here is the arrival time (PLAN.md R12):

    arrival_at = departure_at + duration_minutes
                 - origin.utc_offset_minutes
                 + destination.utc_offset_minutes

Departure and arrival are both stored as naive *local* times at their own
airport. Doing this at seed time means nothing at request time ever touches a
timezone — `duration_minutes` is displayed straight from the column.
"""

from datetime import date, datetime, time, timedelta

from ..models import Flight
from .content import AIRPORTS, CARRIERS, base_for, is_transatlantic

WINDOW_DAYS = 14

# Slot shape: (hour, minute, jitter_span_minutes). The jitter spreads departures
# across the stated window so a route's daily set doesn't cluster.
INTRA_EU_SLOTS = [(6, 50, 80), (12, 20, 80), (18, 30, 90)]
# ATL -> Europe: evening departures, landing in Europe the following morning.
TRANSAT_EASTBOUND_SLOTS = [(17, 0, 70), (18, 20, 70)]
# Europe -> ATL: late morning / early afternoon, landing the same afternoon.
TRANSAT_WESTBOUND_SLOTS = [(10, 0, 80), (11, 40, 80)]

# Cheapest slot is the least convenient one. Midday costs the most.
INTRA_EU_PRICE_MULT = [0.85, 1.15, 0.95]
TRANSAT_PRICE_MULT = [1.00, 0.90]

# ±25%, applied per (day, slot) rather than per day, so the cheap slot isn't the
# cheapest on literally every date.
DAY_JITTER = [
    0.00, 0.12, -0.08, 0.20, -0.15, 0.05, 0.25,
    -0.20, 0.10, -0.05, 0.18, -0.12, 0.08, -0.25,
]

# Seats remaining runs lower on the cheaper slots — realistic, and a quiet nudge
# toward the trade-off the results list is built to show. The floor of 11 keeps
# every flight bookable for the maximum party of 9.
INTRA_EU_SEAT_BASE = [11, 48, 26]
TRANSAT_SEAT_BASE = [34, 15]


def _mix(*parts: int) -> int:
    """FNV-1a over the inputs. Deterministic across runs and interpreters —
    unlike `hash()`, which is randomised per process for str/bytes."""
    h = 2166136261
    for p in parts:
        h = ((h ^ (p & 0xFFFFFFFF)) * 16777619) & 0xFFFFFFFF
    return h


def ordered_routes() -> list[tuple[str, str]]:
    """All 30 ordered (origin, destination) pairs, in a stable order."""
    codes = sorted(a["iata_code"] for a in AIRPORTS)
    return [(o, d) for o in codes for d in codes if o != d]


def _slots_for(origin: str, destination: str) -> tuple[list, list, list]:
    """(departure slots, price multipliers, seat bases) for a route."""
    if not is_transatlantic(origin, destination):
        return INTRA_EU_SLOTS, INTRA_EU_PRICE_MULT, INTRA_EU_SEAT_BASE
    slots = TRANSAT_EASTBOUND_SLOTS if origin == "ATL" else TRANSAT_WESTBOUND_SLOTS
    return slots, TRANSAT_PRICE_MULT, TRANSAT_SEAT_BASE


def generate_flights(airports_by_code: dict, start_date: date) -> list[Flight]:
    """Build every Flight row for the 14-day window starting at `start_date`."""
    flights: list[Flight] = []

    for route_index, (origin_code, dest_code) in enumerate(ordered_routes()):
        origin = airports_by_code[origin_code]
        destination = airports_by_code[dest_code]

        base = base_for(origin_code, dest_code)
        base_duration = base["duration"]
        base_fare = base["fare"]

        slots, price_mult, seat_base = _slots_for(origin_code, dest_code)
        carriers = CARRIERS[(origin_code, dest_code)]

        for day_offset in range(WINDOW_DAYS):
            flight_date = start_date + timedelta(days=day_offset)

            for slot, (hour, minute, span) in enumerate(slots):
                noise = _mix(route_index, day_offset, slot)

                # --- departure, rounded to the nearest 5 minutes -------------
                jitter = (noise % span) // 5 * 5
                departure_at = datetime.combine(
                    flight_date, time(hour, minute)
                ) + timedelta(minutes=jitter)

                # --- duration: 0–15 min off the route's base ----------------
                duration = base_duration + ((noise >> 8) % 16)

                # --- arrival, offset-corrected. The whole point of R12. -----
                arrival_at = (
                    departure_at
                    + timedelta(minutes=duration)
                    - timedelta(minutes=origin.utc_offset_minutes)
                    + timedelta(minutes=destination.utc_offset_minutes)
                )

                # --- price --------------------------------------------------
                day_factor = 1.0 + DAY_JITTER[
                    (day_offset * 3 + slot + route_index) % len(DAY_JITTER)
                ]
                price_minor = int(base_fare * price_mult[slot] * day_factor)
                price_minor = round(price_minor, -2)  # tidy to whole dollars

                # --- carrier and flight number ------------------------------
                prefix, airline = carriers[slot % len(carriers)]
                number = 100 + ((route_index * 37 + slot * 11) % 3900)

                # --- seats --------------------------------------------------
                seats_total = 120 + ((noise >> 16) % 61)
                seats_available = min(
                    seat_base[slot] + ((noise >> 20) % 22), seats_total
                )

                flights.append(
                    Flight(
                        flight_number=f"{prefix}{number}",
                        airline=airline,
                        origin_id=origin.id,
                        destination_id=destination.id,
                        departure_at=departure_at,
                        arrival_at=arrival_at,
                        duration_minutes=duration,
                        price_minor=price_minor,
                        currency="USD",
                        seats_total=seats_total,
                        seats_available=seats_available,
                    )
                )

    return flights
