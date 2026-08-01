"""Endpoint smoke tests.

Not exhaustive by design (PLAN.md §1) — these cover the happy path plus the
error branches that are easy to break silently and awkward to notice by hand.
"""

from datetime import date, timedelta


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_airports_sorted_and_offset_not_exposed(client):
    r = client.get("/api/airports")
    assert r.status_code == 200
    airports = r.json()

    assert len(airports) == 6
    assert [a["city"] for a in airports] == sorted(a["city"] for a in airports)

    # utc_offset_minutes is seed-time only. Leaking it would invite a client to
    # start doing timezone maths the whole design exists to avoid.
    assert "utc_offset_minutes" not in airports[0]


def test_search_returns_chronological_results(client, today):
    r = client.get(
        "/api/flights/search",
        params={"origin": "LHR", "destination": "AMS", "date": today},
    )
    assert r.status_code == 200
    flights = r.json()

    assert 2 <= len(flights) <= 3
    departures = [f["departure_at"] for f in flights]
    assert departures == sorted(departures)
    assert all(f["origin"]["iata_code"] == "LHR" for f in flights)
    assert all(f["currency"] == "USD" for f in flights)


def test_search_every_route_and_day_is_populated(client):
    """R6: empty results are eliminated, not merely unlikely."""
    codes = ["AMS", "ATL", "BCN", "CDG", "LHR", "LIS"]
    start = date.today()

    for day_offset in (0, 6, 13):  # first, middle and last day of the window
        when = (start + timedelta(days=day_offset)).isoformat()
        for origin in codes:
            for destination in codes:
                if origin == destination:
                    continue
                r = client.get(
                    "/api/flights/search",
                    params={
                        "origin": origin,
                        "destination": destination,
                        "date": when,
                    },
                )
                assert r.status_code == 200
                assert len(r.json()) >= 2, f"{origin}->{destination} on {when}"


def test_search_rejects_same_origin_and_destination(client, today):
    r = client.get(
        "/api/flights/search",
        params={"origin": "ATL", "destination": "ATL", "date": today},
    )
    assert r.status_code == 400


def test_search_rejects_malformed_date(client):
    r = client.get(
        "/api/flights/search",
        params={"origin": "ATL", "destination": "CDG", "date": "not-a-date"},
    )
    assert r.status_code == 422


def test_transatlantic_arrival_is_offset_corrected(client, today):
    """R12: the arrival must reflect the destination's local clock.

    ATL is UTC-4 and CDG UTC+2 in summer, so a correct eastbound arrival is
    departure + duration + 6h. Computing it naively would put the landing six
    hours early, and nothing else in the app would notice.
    """
    from datetime import datetime

    r = client.get(
        "/api/flights/search",
        params={"origin": "ATL", "destination": "CDG", "date": today},
    )
    flight = r.json()[0]

    departure = datetime.fromisoformat(flight["departure_at"])
    arrival = datetime.fromisoformat(flight["arrival_at"])
    expected = departure + timedelta(
        minutes=flight["duration_minutes"] + 360  # +6h ATL -> CDG
    )
    assert arrival == expected


def test_flight_lookup_404s_on_unknown_id(client):
    assert client.get("/api/flights/999999").status_code == 404


def test_booking_round_trip(client, today):
    flights = client.get(
        "/api/flights/search",
        params={"origin": "ATL", "destination": "LIS", "date": today},
    ).json()
    flight = flights[0]
    seats_before = flight["seats_available"]

    created = client.post(
        "/api/bookings",
        json={
            "flight_id": flight["id"],
            "contact_email": "ada@example.com",
            "contact_phone": "+1 404 555 0142",
            "passengers": [
                {"first_name": "Ada", "last_name": "Lovelace"},
                {"first_name": "Charles", "last_name": "Babbage"},
            ],
        },
    )
    assert created.status_code == 201
    booking = created.json()

    assert booking["status"] == "confirmed"
    assert len(booking["reference"]) == 6
    # No ambiguous glyphs — this is a code people read aloud and type back in.
    assert not set(booking["reference"]) & set("01IOS5")
    assert booking["total_price_minor"] == flight["price_minor"] * 2
    assert booking["contact_email"] == "ada@example.com"
    assert len(booking["passengers"]) == 2

    # The confirmation payload carries the guide, so the frontend needs no
    # second request on the happy path.
    assert booking["arrival_guide"]["city"] == "Lisbon"
    assert len(booking["arrival_guide"]["attractions"]) >= 3

    seats_after = client.get(f"/api/flights/{flight['id']}").json()["seats_available"]
    assert seats_after == seats_before - 2

    # Retrieval by reference returns the same payload, case-insensitively.
    fetched = client.get(f"/api/bookings/{booking['reference'].lower()}")
    assert fetched.status_code == 200
    assert fetched.json()["reference"] == booking["reference"]


def test_booking_rejects_invalid_payloads(client, today):
    flight_id = client.get(
        "/api/flights/search",
        params={"origin": "BCN", "destination": "CDG", "date": today},
    ).json()[0]["id"]

    def post(**overrides):
        payload = {
            "flight_id": flight_id,
            "contact_email": "a@b.com",
            "passengers": [{"first_name": "A", "last_name": "B"}],
        }
        payload.update(overrides)
        return client.post("/api/bookings", json=payload)

    assert post(contact_email="not-an-email").status_code == 422
    assert post(passengers=[]).status_code == 422
    assert post(passengers=[{"first_name": "A", "last_name": "B"}] * 10).status_code == 422
    assert post(flight_id=999999).status_code == 404


def test_booking_409s_when_seats_run_out(client, today):
    """Book a flight down below the party size and confirm the guard holds."""
    flight = client.get(
        "/api/flights/search",
        params={"origin": "AMS", "destination": "BCN", "date": today},
    ).json()[0]

    party = [{"first_name": "P", "last_name": str(i)} for i in range(9)]

    # Drain it nine at a time until fewer than nine seats remain.
    while True:
        available = client.get(f"/api/flights/{flight['id']}").json()["seats_available"]
        if available < 9:
            break
        r = client.post(
            "/api/bookings",
            json={
                "flight_id": flight["id"],
                "contact_email": "a@b.com",
                "passengers": party,
            },
        )
        assert r.status_code == 201

    r = client.post(
        "/api/bookings",
        json={
            "flight_id": flight["id"],
            "contact_email": "a@b.com",
            "passengers": party,
        },
    )
    assert r.status_code == 409
    assert "seat" in r.json()["detail"].lower()


def test_unknown_booking_reference_404s(client):
    assert client.get("/api/bookings/ZZZZZZ").status_code == 404


def test_guide_lookup(client):
    r = client.get("/api/guides/bcn")  # lower case on purpose
    assert r.status_code == 200
    guide = r.json()

    assert guide["city"] == "Barcelona"
    assert guide["transport"]["mode"] in {"train", "metro", "bus", "taxi"}
    assert guide["distance_km"] > 0
    assert all(a["name"] and a["description"] for a in guide["attractions"])

    assert client.get("/api/guides/JFK").status_code == 404


def test_every_airport_has_a_guide(client):
    for airport in client.get("/api/airports").json():
        r = client.get(f"/api/guides/{airport['iata_code']}")
        assert r.status_code == 200, airport["iata_code"]


def test_unmatched_api_paths_stay_json(client):
    """The SPA catch-all must not swallow API 404s into an HTML 200."""
    r = client.get("/api/nope")
    assert r.status_code == 404
    assert r.headers["content-type"].startswith("application/json")
