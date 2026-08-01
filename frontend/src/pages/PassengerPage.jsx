import { useEffect, useState } from "react";
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";

import { createBooking, getFlight } from "../api/client";
import StepIndicator from "../components/StepIndicator";
import FlightSummaryCard from "../components/booking/FlightSummaryCard";
import PassengerForm from "../components/booking/PassengerForm";
import PriceSummary from "../components/booking/PriceSummary";
import Button from "../components/ui/Button";
import ErrorBanner from "../components/ui/ErrorBanner";
import Skeleton from "../components/ui/Skeleton";

import styles from "./PassengerPage.module.css";

function readPassengerCount(searchParams) {
  const n = Number(searchParams.get("passengers") ?? 1);
  return Number.isInteger(n) && n >= 1 && n <= 9 ? n : 1;
}

export default function PassengerPage() {
  const { flightId } = useParams();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const passengerCount = readPassengerCount(searchParams);

  /* Refetched rather than handed over in router state, so a reload or a
     shared link works without depending on how the user got here. */
  const [flight, setFlight] = useState(null);
  const [loadError, setLoadError] = useState(null);

  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState(null);

  useEffect(() => {
    let active = true;
    setFlight(null);
    setLoadError(null);

    getFlight(flightId)
      .then((data) => active && setFlight(data))
      .catch((error) => active && setLoadError(error.message));

    return () => {
      active = false;
    };
  }, [flightId]);

  async function handleSubmit(payload) {
    setSubmitting(true);
    setSubmitError(null);
    try {
      const booking = await createBooking({
        flight_id: Number(flightId),
        ...payload,
      });
      /* Pass the booking through so the confirmation page doesn't need a
         second request on the happy path. It still refetches if this state is
         missing, which is what makes the URL reloadable and shareable. */
      navigate(`/booking/${booking.reference}`, {
        replace: true,
        state: { booking },
      });
    } catch (error) {
      setSubmitError(error.message);
      setSubmitting(false);
    }
  }

  if (loadError) {
    return (
      <>
        <ErrorBanner>{loadError}</ErrorBanner>
        <div className={styles.back}>
          <Button as={Link} to="/" variant="secondary">
            Back to search
          </Button>
        </div>
      </>
    );
  }

  if (!flight) {
    return (
      <div className={styles.loading}>
        <Skeleton height={28} width={220} />
        <Skeleton height={200} />
      </div>
    );
  }

  return (
    <>
      <StepIndicator step={2} />

      <div className={styles.layout}>
        <div>
          <h1 className={styles.title}>Passenger details</h1>
          <p className={styles.subtitle}>
            Names must match the travel document each passenger will carry.
          </p>

          <PassengerForm
            count={passengerCount}
            submitting={submitting}
            submitError={submitError}
            onSubmit={handleSubmit}
          />
        </div>

        <aside className={styles.aside}>
          <FlightSummaryCard flight={flight} />
          <PriceSummary flight={flight} passengerCount={passengerCount} />
        </aside>
      </div>
    </>
  );
}
