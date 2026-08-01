import { useEffect, useState } from "react";
import { Link, useLocation, useParams } from "react-router-dom";

import { getBooking } from "../api/client";
import StepIndicator from "../components/StepIndicator";
import FlightSummaryCard from "../components/booking/FlightSummaryCard";
import ArrivalGuide from "../components/guide/ArrivalGuide";
import Button from "../components/ui/Button";
import Card from "../components/ui/Card";
import ErrorBanner from "../components/ui/ErrorBanner";
import Skeleton from "../components/ui/Skeleton";
import { formatUSD } from "../lib/format";

import styles from "./ConfirmationPage.module.css";

export default function ConfirmationPage() {
  const { reference } = useParams();
  const location = useLocation();

  /* Handed over by PassengerPage on the happy path — the POST response is
     already the full confirmation payload, so there's nothing to refetch.
     A reload drops this state and the effect below fills it in instead. */
  const handedOver = location.state?.booking;

  const [booking, setBooking] = useState(
    handedOver?.reference === reference ? handedOver : null,
  );
  const [error, setError] = useState(null);

  useEffect(() => {
    if (booking) return undefined;

    let active = true;
    getBooking(reference)
      .then((data) => active && setBooking(data))
      .catch((err) => active && setError(err.message));

    return () => {
      active = false;
    };
  }, [reference, booking]);

  if (error) {
    return (
      <>
        <ErrorBanner>{error}</ErrorBanner>
        <div className={styles.actions}>
          <Button as={Link} to="/" variant="secondary">
            Back to search
          </Button>
        </div>
      </>
    );
  }

  if (!booking) {
    return (
      <div className={styles.loading}>
        <Skeleton height={48} width={320} />
        <Skeleton height={200} />
      </div>
    );
  }

  return (
    <>
      <StepIndicator step={3} />

      {/* Two columns rather than stacked: the reference sat under the lede and
          pushed the Arrival Guide most of a screen further down for no reason,
          while the right half of the header was empty. */}
      <header className={styles.header}>
        <div className={styles.headerMain}>
          {/* SERIF #3 of 4 — see global.css */}
          <h1 className={`display ${styles.title}`}>You're booked</h1>
          <p className={styles.lede}>
            Keep this reference — it's the only way to find this booking again.
            No account was created and no email has been sent.
          </p>
        </div>

        <div className={styles.referenceBlock}>
          <span className={styles.referenceLabel}>Booking reference</span>
          {/* Inter, not the serif. See the note in the stylesheet. */}
          <span className={styles.reference}>{booking.reference}</span>
        </div>
      </header>

      <div className={styles.layout}>
        <div>
          <Card>
            <h2 className={styles.sectionHeading}>
              {booking.passengers.length === 1 ? "Passenger" : "Passengers"}
            </h2>

            <ul className={styles.passengerList}>
              {booking.passengers.map((passenger, index) => (
                <li key={index} className={styles.passenger}>
                  <span className={styles.passengerName}>
                    {passenger.first_name} {passenger.last_name}
                  </span>
                  <span className={styles.passengerMeta}>
                    Ticket {index + 1} of {booking.passengers.length}
                  </span>
                </li>
              ))}
            </ul>

            <p className={styles.contact}>
              Contact: <strong>{booking.contact_email}</strong>
              {booking.contact_phone && ` · ${booking.contact_phone}`}
              {" · "}
              Total{" "}
              <span className="tnum">
                {formatUSD(booking.total_price_minor)}
              </span>{" "}
              {booking.currency}
            </p>
          </Card>
        </div>

        <aside className={styles.aside}>
          <FlightSummaryCard flight={booking.flight} title="Itinerary" />
        </aside>
      </div>

      {/* Rendered conditionally so a missing guide degrades quietly (R7). */}
      {booking.arrival_guide && <ArrivalGuide guide={booking.arrival_guide} />}

      <div className={styles.actions}>
        <Button as={Link} to="/" variant="secondary">
          Book another flight
        </Button>
      </div>
    </>
  );
}
