import { fieldStyles } from "../ui/Field";
import styles from "./PassengerStepper.module.css";

const MIN = 1;
const MAX = 9; // matches the Pydantic bound on POST /api/bookings

export default function PassengerStepper({ value, onChange }) {
  const label = `${value} passenger${value === 1 ? "" : "s"}`;

  return (
    <div className={fieldStyles.field}>
      <span className={fieldStyles.label} id="passengers-label">
        Passengers
      </span>
      <div
        className={styles.stepper}
        role="group"
        aria-labelledby="passengers-label"
      >
        <button
          type="button"
          className={styles.step}
          onClick={() => onChange(Math.max(MIN, value - 1))}
          disabled={value <= MIN}
          aria-label="Remove a passenger"
        >
          −
        </button>
        <span className={`${styles.value} tnum`} aria-live="polite">
          {value}
          <span className="sr-only"> {label}</span>
        </span>
        <button
          type="button"
          className={styles.step}
          onClick={() => onChange(Math.min(MAX, value + 1))}
          disabled={value >= MAX}
          aria-label="Add a passenger"
        >
          +
        </button>
      </div>
    </div>
  );
}
