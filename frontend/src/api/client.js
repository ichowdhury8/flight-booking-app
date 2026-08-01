/* One request wrapper plus a function per endpoint.
 *
 * Paths are relative, so the browser is same-origin in both dev (Vite proxies
 * /api to :8000) and production (FastAPI serves both). CORS never applies. */

export class ApiError extends Error {
  constructor(status, detail) {
    super(detail || `Request failed (${status})`);
    this.status = status;
    this.detail = detail;
  }
}

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(path, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch {
    throw new ApiError(0, "Could not reach the server. Check your connection.");
  }

  if (!response.ok) {
    let detail;
    try {
      const body = await response.json();
      // FastAPI's 422 detail is an array of field errors; surface the first.
      detail = Array.isArray(body.detail)
        ? body.detail[0]?.msg
        : body.detail;
    } catch {
      /* non-JSON error body — fall through to the generic message */
    }
    throw new ApiError(response.status, detail);
  }

  return response.status === 204 ? null : response.json();
}

export function getAirports() {
  return request("/api/airports");
}

export function searchFlights({ origin, destination, date, passengers }) {
  const params = new URLSearchParams({
    origin,
    destination,
    date,
    passengers: String(passengers ?? 1),
  });
  return request(`/api/flights/search?${params}`);
}

export function getFlight(flightId) {
  return request(`/api/flights/${flightId}`);
}

export function createBooking(payload) {
  return request("/api/bookings", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getBooking(reference) {
  return request(`/api/bookings/${reference}`);
}

export function getGuide(iataCode) {
  return request(`/api/guides/${iataCode}`);
}
