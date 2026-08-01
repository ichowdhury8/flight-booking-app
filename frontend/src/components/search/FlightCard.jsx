import { Link } from "react-router-dom";

import {
  dayOffset,
  formatDuration,
  formatTime,
  formatUSD,
} from "../../lib/format";
import Button from "../ui/Button";
import Card from "../ui/Card";
import styles from "./FlightCard.module.css";

const LOW_SEATS = 15;

export default function FlightCard({ flight, passengers, searchParams }) {
  const plusDays = dayOffset(flight.departure_at, flight.arrival_at);
  const lowSeats = flight.seats_available <= LOW_SEATS;
  const total = flight.price_minor * passengers;

  return (
    <Card interactive className={styles.card} as="li">
      <div className={styles.main}>
        <p className={styles.carrier}>
          <span className={styles.airline}>{flight.airline}</span>
          <span aria-hidden="true">·</span>
          <span className="tnum">{flight.flight_number}</span>
        </p>

        <div className={styles.timeline}>
          <div className={styles.endpoint}>
            <div className={`${styles.time} tnum`}>
              {formatTime(flight.departure_at)}
            </div>
            <div className={styles.code}>{flight.origin.iata_code}</div>
          </div>

          <div className={styles.middle}>
            <div className={`${styles.duration} tnum`}>
              {formatDuration(flight.duration_minutes)}
            </div>
            <div className={styles.rule} aria-hidden="true" />
          </div>

          <div className={styles.endpoint}>
            <div className={styles.arrivalTime}>
              <span className={`${styles.time} tnum`}>
                {formatTime(flight.arrival_at)}
              </span>
              {plusDays > 0 && (
                <span className={styles.nextDay}>
                  +{plusDays}
                  <span className="sr-only">
                    {" "}
                    day{plusDays === 1 ? "" : "s"} later
                  </span>
                </span>
              )}
            </div>
            <div className={styles.code}>{flight.destination.iata_code}</div>
          </div>
        </div>

        {lowSeats && (
          <p className={`${styles.seats} ${styles.seatsLow}`}>
            Only {flight.seats_available} seats left at this price
          </p>
        )}
      </div>

      <div className={styles.aside}>
        <div>
          <div className={`${styles.price} tnum`}>
            {formatUSD(flight.price_minor)}
          </div>
          <div className={styles.priceMeta}>
            {passengers > 1 ? (
              <span className="tnum">{formatUSD(total)} total</span>
            ) : (
              "per person"
            )}
          </div>
        </div>

        <Button
          as={Link}
          to={`/book/${flight.id}?${searchParams}`}
          size="sm"
          variant="secondary"
        >
          Select
          <span className="sr-only">
            {" "}
            {flight.airline} {flight.flight_number}, departing{" "}
            {formatTime(flight.departure_at)}
          </span>
        </Button>
      </div>
    </Card>
  );
}
