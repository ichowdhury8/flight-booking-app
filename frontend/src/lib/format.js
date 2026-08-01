/* Display formatting. All money arrives from the API as integer US cents. */

const usd = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
});

/** 64200 -> "$642.00" */
export function formatUSD(minor) {
  return usd.format(minor / 100);
}

/** 515 -> "8h 35m" */
export function formatDuration(minutes) {
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return m === 0 ? `${h}h` : `${h}h ${m}m`;
}

/* The API sends naive local datetimes ("2026-08-02T17:05:00") that are already
 * correct at their own airport — the offset arithmetic happened at seed time.
 * JS parses an offset-less datetime as local time, so parsing and formatting
 * round-trips the wall clock exactly. Do NOT append "Z" here: that would
 * reintroduce the timezone bug the seed exists to avoid. */
function parseLocal(value) {
  return new Date(value);
}

/** "2026-08-02T17:05:00" -> "5:05 PM"  (A14) */
export function formatTime(value) {
  return parseLocal(value).toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
  });
}

/** "2026-08-02T17:05:00" -> "Sun, Aug 2"  (A14) */
export function formatDate(value) {
  return parseLocal(value).toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
  });
}

/** Calendar days between two naive datetimes — for the "+1" arrival badge. */
export function dayOffset(from, to) {
  const a = parseLocal(from);
  const b = parseLocal(to);
  const startA = new Date(a.getFullYear(), a.getMonth(), a.getDate());
  const startB = new Date(b.getFullYear(), b.getMonth(), b.getDate());
  return Math.round((startB - startA) / 86400000);
}

/** 16 -> "10 mi (16 km)"  (A15) */
export function formatDistance(km) {
  const { miles, kilometres } = distanceParts(km);
  return `${miles} mi (${kilometres} km)`;
}

/** The same conversion, unformatted, for laying the two units out separately. */
export function distanceParts(km) {
  return { miles: Math.round(km * 0.621371), kilometres: Math.round(km) };
}

/** Date -> "2026-08-02", in local time rather than UTC. */
export function toISODate(date) {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}
