"""Hand-authored seed content: airports, arrival guides, attractions, and the
per-route duration and fare tables the flight generator works from.

Everything in this file is static data. Nothing here is fetched, and nothing in
this app calls an external service at runtime — the Arrival Guide is read from
SQLite like any other row.

ACCURACY NOTE (PLAN.md A13): distances, transport modes, service names, journey
times and cost notes are drawn from general knowledge. They are approximately
right, not authoritative, and are a draft until fact-checked.
"""

# ---------------------------------------------------------------------------
# Airports
#
# utc_offset_minutes is a hard-coded *summer* offset, used only to compute
# arrival_at at seed time (PLAN.md A4). It is never read at request time and is
# never exposed by the API.
# ---------------------------------------------------------------------------

AIRPORTS = [
    {
        "iata_code": "ATL",
        "name": "Hartsfield–Jackson Atlanta International",
        "city": "Atlanta",
        "country": "United States",
        "utc_offset_minutes": -240,  # EDT
    },
    {
        "iata_code": "LHR",
        "name": "London Heathrow",
        "city": "London",
        "country": "United Kingdom",
        "utc_offset_minutes": 60,  # BST
    },
    {
        "iata_code": "CDG",
        "name": "Paris Charles de Gaulle",
        "city": "Paris",
        "country": "France",
        "utc_offset_minutes": 120,  # CEST
    },
    {
        "iata_code": "BCN",
        "name": "Barcelona El Prat",
        "city": "Barcelona",
        "country": "Spain",
        "utc_offset_minutes": 120,  # CEST
    },
    {
        "iata_code": "AMS",
        "name": "Amsterdam Schiphol",
        "city": "Amsterdam",
        "country": "Netherlands",
        "utc_offset_minutes": 120,  # CEST
    },
    {
        "iata_code": "LIS",
        "name": "Lisbon Humberto Delgado",
        "city": "Lisbon",
        "country": "Portugal",
        "utc_offset_minutes": 60,  # WEST
    },
]


# ---------------------------------------------------------------------------
# Arrival guides — one per airport, 3–4 attractions each.
# transport_cost_note stays in the destination's local currency (PLAN.md A16).
# ---------------------------------------------------------------------------

GUIDES = {
    "ATL": {
        "intro": (
            "Atlanta spreads out rather than up, and its centre of gravity sits between "
            "Downtown, Midtown and the parks and neighbourhoods strung along the BeltLine."
        ),
        "distance_km": 16.0,
        "transport_mode": "metro",
        "transport_name": "MARTA Gold or Red Line",
        "transport_minutes": 20,
        "transport_notes": (
            "The station is inside the domestic terminal, past baggage claim — you never "
            "go outside. Ride north to Five Points for Downtown, or stay on for Midtown."
        ),
        "transport_cost_note": "~$2.50 one way, plus $2 for a reusable Breeze card",
        "attractions": [
            {
                "name": "Georgia Aquarium",
                "description": (
                    "One of the largest aquariums in the world, with whale sharks and manta "
                    "rays in a viewing tunnel that is worth the queue."
                ),
                "category": "landmark",
            },
            {
                "name": "Martin Luther King Jr. National Historical Park",
                "description": (
                    "Dr. King's birth home, Ebenezer Baptist Church and his tomb, all within "
                    "a few walkable blocks in the Sweet Auburn district."
                ),
                "category": "museum",
            },
            {
                "name": "The Atlanta BeltLine — Eastside Trail",
                "description": (
                    "A former rail corridor turned walking and cycling path, lined with murals, "
                    "breweries and patios between Piedmont Park and Krog Street Market."
                ),
                "category": "outdoors",
            },
            {
                "name": "Ponce City Market",
                "description": (
                    "A vast Sears warehouse converted into a food hall and shops, with a rooftop "
                    "that has one of the best skyline views in the city."
                ),
                "category": "food",
            },
        ],
    },
    "LHR": {
        "intro": (
            "London rewards picking one or two areas a day rather than criss-crossing it. "
            "Almost everything below is walkable from a single Underground stop."
        ),
        "distance_km": 24.0,
        "transport_mode": "train",
        "transport_name": "Heathrow Express to Paddington",
        "transport_minutes": 15,
        "transport_notes": (
            "Fifteen minutes non-stop from Terminals 2 and 3, around 21 from Terminal 5. "
            "The Elizabeth line is slower at roughly 30 minutes but considerably cheaper."
        ),
        "transport_cost_note": "~£25 one way on the day; far less booked in advance",
        "attractions": [
            {
                "name": "The British Museum",
                "description": (
                    "Eight million objects spanning human history, free to enter, with the "
                    "glass-roofed Great Court at its centre."
                ),
                "category": "museum",
            },
            {
                "name": "Tower of London",
                "description": (
                    "A working fortress for nearly a thousand years, holding the Crown Jewels "
                    "and a great deal of grim and well-told history."
                ),
                "category": "landmark",
            },
            {
                "name": "Borough Market",
                "description": (
                    "A food market under railway arches near London Bridge — go hungry, arrive "
                    "early, and eat standing up like everyone else."
                ),
                "category": "food",
            },
            {
                "name": "Hampstead Heath",
                "description": (
                    "Eight hundred acres of half-wild parkland north of the centre, with a view "
                    "back over the whole city from Parliament Hill."
                ),
                "category": "outdoors",
            },
        ],
    },
    "CDG": {
        "intro": (
            "Paris is compact and best walked between its arrondissements, with the Seine as "
            "the reference point you can always navigate back to."
        ),
        "distance_km": 25.0,
        "transport_mode": "train",
        "transport_name": "RER B to Gare du Nord",
        "transport_minutes": 35,
        "transport_notes": (
            "Trains run every 10–20 minutes from Terminals 2 and 3. Direct services are "
            "quicker; keep your ticket, you need it to get out of the barriers."
        ),
        "transport_cost_note": "~€13 one way",
        "attractions": [
            {
                "name": "Musée d'Orsay",
                "description": (
                    "A converted Beaux-Arts railway station holding the world's great collection "
                    "of Impressionist painting, under an enormous glass clock."
                ),
                "category": "museum",
            },
            {
                "name": "Sainte-Chapelle",
                "description": (
                    "A small royal chapel on the Île de la Cité whose upper level is almost "
                    "entirely 13th-century stained glass. Go on a bright day."
                ),
                "category": "landmark",
            },
            {
                "name": "Le Marais",
                "description": (
                    "Narrow medieval streets, falafel counters, small galleries and the arcaded "
                    "Place des Vosges — the most walkable few hours in the city."
                ),
                "category": "neighbourhood",
            },
            {
                "name": "Père Lachaise Cemetery",
                "description": (
                    "A hillside of cobbled avenues and elaborate tombs on the eastern edge of "
                    "the city, quieter and stranger than any museum."
                ),
                "category": "outdoors",
            },
        ],
    },
    "BCN": {
        "intro": (
            "Barcelona sits between hills and sea, with Gaudí's work scattered across the grid "
            "of the Eixample and the old city tangled below it."
        ),
        "distance_km": 14.0,
        "transport_mode": "bus",
        "transport_name": "Aerobús A1/A2 to Plaça de Catalunya",
        "transport_minutes": 35,
        "transport_notes": (
            "A1 serves Terminal 1 and A2 Terminal 2; both leave from directly outside arrivals "
            "every 5–10 minutes. Pay at the stop or on board by card."
        ),
        "transport_cost_note": "~€7.25 one way",
        "attractions": [
            {
                "name": "Basílica de la Sagrada Família",
                "description": (
                    "Gaudí's unfinished cathedral, where the interior columns branch like trees "
                    "and the stained glass shifts colour across the day. Book a timed slot."
                ),
                "category": "landmark",
            },
            {
                "name": "Park Güell",
                "description": (
                    "A hillside park of mosaic terraces and undulating benches, with the whole "
                    "city and the Mediterranean laid out below."
                ),
                "category": "outdoors",
            },
            {
                "name": "The Gothic Quarter",
                "description": (
                    "The medieval core between Las Ramblas and Via Laietana — Roman walls, the "
                    "cathedral cloister, and streets narrow enough to lose the sun."
                ),
                "category": "neighbourhood",
            },
            {
                "name": "Mercat de Sant Josep de la Boqueria",
                "description": (
                    "A covered market off Las Ramblas since the 19th century. Skip the entrance "
                    "stalls and eat at a counter deeper inside."
                ),
                "category": "food",
            },
        ],
    },
    "AMS": {
        "intro": (
            "Amsterdam's canal rings make it small and very walkable. Watch for bikes — the "
            "cycle lane is a road, and you will be in it before you notice."
        ),
        "distance_km": 15.0,
        "transport_mode": "train",
        "transport_name": "Intercity train to Amsterdam Centraal",
        "transport_minutes": 17,
        "transport_notes": (
            "The platforms are directly beneath the terminal, no transfer needed. Trains run "
            "several times an hour, and all night at reduced frequency."
        ),
        "transport_cost_note": "~€6 one way",
        "attractions": [
            {
                "name": "Rijksmuseum",
                "description": (
                    "The Dutch national museum, built around Vermeer, Rembrandt's Night Watch, "
                    "and eight centuries of the country's art."
                ),
                "category": "museum",
            },
            {
                "name": "Van Gogh Museum",
                "description": (
                    "The largest collection of Van Gogh's work anywhere, hung chronologically so "
                    "you watch the style arrive. Timed tickets sell out."
                ),
                "category": "museum",
            },
            {
                "name": "Anne Frank House",
                "description": (
                    "The canal-side annexe where the Frank family hid for two years, preserved "
                    "almost empty. Tickets are released online in advance only."
                ),
                "category": "landmark",
            },
            {
                "name": "The Jordaan",
                "description": (
                    "A former workers' district of narrow canals, brown cafés and courtyard "
                    "gardens, just west of the centre and best wandered without a plan."
                ),
                "category": "neighbourhood",
            },
        ],
    },
    "LIS": {
        "intro": (
            "Lisbon is built across seven hills above the Tagus, which makes it beautiful and "
            "unexpectedly strenuous. Wear something with grip on the cobbles."
        ),
        "distance_km": 7.0,
        "transport_mode": "metro",
        "transport_name": "Metro red line from Aeroporto",
        "transport_minutes": 20,
        "transport_notes": (
            "The station is a short signed walk from arrivals. Change at Alameda or "
            "São Sebastião for the centre and the Baixa."
        ),
        "transport_cost_note": "~€1.80 one way, plus €0.50 for a Navegante card",
        "attractions": [
            {
                "name": "Mosteiro dos Jerónimos, Belém",
                "description": (
                    "A vast Manueline monastery from Portugal's age of exploration, with a "
                    "cloister carved like rope and coral. The tower is a short walk away."
                ),
                "category": "landmark",
            },
            {
                "name": "Alfama and São Jorge Castle",
                "description": (
                    "The oldest quarter, a maze of stairways and laundry lines climbing to a "
                    "Moorish castle with the best view over the river."
                ),
                "category": "neighbourhood",
            },
            {
                "name": "Time Out Market",
                "description": (
                    "Half of the Mercado da Ribeira turned into a hall of stalls run by the "
                    "city's better-known chefs. Busy, and worth it."
                ),
                "category": "food",
            },
            {
                "name": "Tram 28",
                "description": (
                    "A vintage yellow tram that grinds through Graça, Alfama and Estrela. Board "
                    "at the start of the line early, or you will not get on."
                ),
                "category": "outdoors",
            },
        ],
    },
}


# ---------------------------------------------------------------------------
# Per-city-pair base durations (minutes) and base fares (US cents).
#
# Symmetric: the key is a frozenset-like sorted tuple, applied in both directions.
# Durations are typical block times; fares are the mid-point the slot and day
# multipliers move around. PLAN.md A7 — plausible fiction, not real schedules.
# ---------------------------------------------------------------------------

ROUTE_BASE = {
    # Intra-European
    ("AMS", "BCN"): {"duration": 135, "fare": 12_000},
    ("AMS", "CDG"): {"duration": 80, "fare": 10_000},
    ("AMS", "LHR"): {"duration": 75, "fare": 10_500},
    ("AMS", "LIS"): {"duration": 175, "fare": 14_500},
    ("BCN", "CDG"): {"duration": 105, "fare": 11_000},
    ("BCN", "LHR"): {"duration": 125, "fare": 13_000},
    ("BCN", "LIS"): {"duration": 105, "fare": 5_500},
    ("CDG", "LHR"): {"duration": 75, "fare": 9_500},
    ("CDG", "LIS"): {"duration": 150, "fare": 14_000},
    ("LHR", "LIS"): {"duration": 165, "fare": 15_000},
    # Transatlantic. Keys are sorted city pairs — base_for() sorts before lookup.
    ("AMS", "ATL"): {"duration": 520, "fare": 78_000},
    ("ATL", "BCN"): {"duration": 545, "fare": 72_000},
    ("ATL", "CDG"): {"duration": 515, "fare": 64_200},
    ("ATL", "LHR"): {"duration": 500, "fare": 69_000},
    ("ATL", "LIS"): {"duration": 495, "fare": 70_500},
}


# Up to two plausible carriers per ordered route, selected by slot so a day's
# departures offer a carrier choice as well as a time and price choice.
CARRIERS = {
    ("AMS", "BCN"): [("KL", "KLM"), ("VY", "Vueling")],
    ("BCN", "AMS"): [("VY", "Vueling"), ("KL", "KLM")],
    ("AMS", "CDG"): [("AF", "Air France"), ("KL", "KLM")],
    ("CDG", "AMS"): [("AF", "Air France"), ("KL", "KLM")],
    ("AMS", "LHR"): [("BA", "British Airways"), ("KL", "KLM")],
    ("LHR", "AMS"): [("BA", "British Airways"), ("KL", "KLM")],
    ("AMS", "LIS"): [("TP", "TAP Air Portugal"), ("KL", "KLM")],
    ("LIS", "AMS"): [("TP", "TAP Air Portugal"), ("KL", "KLM")],
    ("BCN", "CDG"): [("AF", "Air France"), ("VY", "Vueling")],
    ("CDG", "BCN"): [("AF", "Air France"), ("VY", "Vueling")],
    ("BCN", "LHR"): [("BA", "British Airways"), ("VY", "Vueling")],
    ("LHR", "BCN"): [("BA", "British Airways"), ("VY", "Vueling")],
    ("BCN", "LIS"): [("TP", "TAP Air Portugal"), ("VY", "Vueling")],
    ("LIS", "BCN"): [("TP", "TAP Air Portugal"), ("VY", "Vueling")],
    ("CDG", "LHR"): [("BA", "British Airways"), ("AF", "Air France")],
    ("LHR", "CDG"): [("BA", "British Airways"), ("AF", "Air France")],
    ("CDG", "LIS"): [("TP", "TAP Air Portugal"), ("AF", "Air France")],
    ("LIS", "CDG"): [("TP", "TAP Air Portugal"), ("AF", "Air France")],
    ("LHR", "LIS"): [("TP", "TAP Air Portugal"), ("BA", "British Airways")],
    ("LIS", "LHR"): [("TP", "TAP Air Portugal"), ("BA", "British Airways")],
    # Atlanta is a Delta hub, so Delta plus the natural partner in each market.
    ("ATL", "AMS"): [("DL", "Delta Air Lines"), ("KL", "KLM")],
    ("AMS", "ATL"): [("DL", "Delta Air Lines"), ("KL", "KLM")],
    ("ATL", "BCN"): [("DL", "Delta Air Lines"), ("DL", "Delta Air Lines")],
    ("BCN", "ATL"): [("DL", "Delta Air Lines"), ("DL", "Delta Air Lines")],
    ("ATL", "CDG"): [("DL", "Delta Air Lines"), ("AF", "Air France")],
    ("CDG", "ATL"): [("DL", "Delta Air Lines"), ("AF", "Air France")],
    ("ATL", "LHR"): [("DL", "Delta Air Lines"), ("VS", "Virgin Atlantic")],
    ("LHR", "ATL"): [("DL", "Delta Air Lines"), ("VS", "Virgin Atlantic")],
    ("ATL", "LIS"): [("DL", "Delta Air Lines"), ("TP", "TAP Air Portugal")],
    ("LIS", "ATL"): [("DL", "Delta Air Lines"), ("TP", "TAP Air Portugal")],
}


def base_for(origin: str, destination: str) -> dict:
    """Base duration and fare for a city pair, applied symmetrically."""
    return ROUTE_BASE[tuple(sorted((origin, destination)))]


def is_transatlantic(origin: str, destination: str) -> bool:
    return "ATL" in (origin, destination)
