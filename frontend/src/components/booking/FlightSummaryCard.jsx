import {
  dayOffset,
  formatDate,
  formatDuration,
  formatTime,
} from "../../lib/format";
import Card from "../ui/Card";
import styles from "./FlightSummaryCard.module.css";

function Stop({ time, date, code, city, nextDay }) {
  return (
    <div>
      <div className={`${styles.time} tnum`}>
        {time}
        {nextDay > 0 && (
          <span className={styles.nextDay}>
            {" "}
            +{nextDay}
            <span className="sr-only"> day{nextDay === 1 ? "" : "s"} later</span>
          </span>
        )}
      </div>
      <div className={styles.place}>
        {city} ({code})
      </div>
      <div className={`${styles.date} tnum`}>{date}</div>
    </div>
  );
}

/* Doubles as the ConfirmationPage itinerary card — same content, same shape, so
   the two pages agree by construction rather than by being kept in sync. */
export default function FlightSummaryCard({ flight, title = "Your flight" }) {
  const plusDays = dayOffset(flight.departure_at, flight.arrival_at);

  return (
    <Card>
      <div className={styles.head}>
        {/* h2, so Inter 600 — not the serif. */}
        <h2 className={styles.title}>{title}</h2>
        <span className={styles.carrier}>
          {flight.airline} <span className="tnum">{flight.flight_number}</span>
        </span>
      </div>

      <div className={styles.leg}>
        <div className={styles.rail} aria-hidden="true">
          <span className={`${styles.node} ${styles.nodeFilled}`} />
          <span className={styles.line} />
          <span className={styles.node} />
        </div>

        <div className={styles.stops}>
          <Stop
            time={formatTime(flight.departure_at)}
            date={formatDate(flight.departure_at)}
            code={flight.origin.iata_code}
            city={flight.origin.city}
          />
          <Stop
            time={formatTime(flight.arrival_at)}
            date={formatDate(flight.arrival_at)}
            code={flight.destination.iata_code}
            city={flight.destination.city}
            nextDay={plusDays}
          />
        </div>
      </div>

      <p className={`${styles.duration} tnum`}>
        {formatDuration(flight.duration_minutes)} · Direct
      </p>
    </Card>
  );
}
