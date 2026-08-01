import { useState } from "react";

import { toISODate } from "../../lib/format";
import Button from "../ui/Button";
import Field from "../ui/Field";
import AirportSelect from "./AirportSelect";
import PassengerStepper from "./PassengerStepper";
import styles from "./SearchForm.module.css";

/* The seed covers today + 0..13 and is regenerated on every cold start, so the
 * picker is bounded to match. This is what makes an empty result set
 * unreachable rather than merely unlikely (PLAN.md R6). */
export const WINDOW_DAYS = 14;

export function windowBounds() {
  const today = new Date();
  const last = new Date(today);
  last.setDate(last.getDate() + WINDOW_DAYS - 1);
  return { min: toISODate(today), max: toISODate(last) };
}

export default function SearchForm({ airports, initial, onSearch, loading }) {
  const { min, max } = windowBounds();

  const [origin, setOrigin] = useState(initial.origin);
  const [destination, setDestination] = useState(initial.destination);
  const [date, setDate] = useState(initial.date || min);
  const [passengers, setPassengers] = useState(initial.passengers);
  const [errors, setErrors] = useState({});

  function handleSubmit(event) {
    event.preventDefault();

    const next = {};
    if (!origin) next.origin = "Choose where you're flying from.";
    if (!destination) next.destination = "Choose where you're flying to.";
    if (origin && origin === destination) {
      next.destination = "Origin and destination must be different.";
    }
    if (!date) next.date = "Choose a date.";
    else if (date < min || date > max) {
      next.date = `Choose a date between ${min} and ${max}.`;
    }

    setErrors(next);
    if (Object.keys(next).length > 0) return;

    onSearch({ origin, destination, date, passengers });
  }

  return (
    <form className={styles.form} onSubmit={handleSubmit} noValidate>
      <AirportSelect
        label="From"
        value={origin}
        onChange={setOrigin}
        airports={airports}
        exclude={destination}
        error={errors.origin}
        disabled={airports.length === 0}
      />

      <AirportSelect
        label="To"
        value={destination}
        onChange={setDestination}
        airports={airports}
        exclude={origin}
        error={errors.destination}
        disabled={airports.length === 0}
      />

      <Field label="Departing" error={errors.date}>
        {(controlProps) => (
          <input
            {...controlProps}
            type="date"
            value={date}
            min={min}
            max={max}
            onChange={(event) => setDate(event.target.value)}
          />
        )}
      </Field>

      <PassengerStepper value={passengers} onChange={setPassengers} />

      <Button type="submit" className={styles.submit} disabled={loading}>
        {loading ? "Searching…" : "Search flights"}
      </Button>
    </form>
  );
}
