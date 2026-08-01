import { formatUSD } from "../../lib/format";
import Card from "../ui/Card";
import styles from "./PriceSummary.module.css";

export default function PriceSummary({ flight, passengerCount }) {
  const total = flight.price_minor * passengerCount;

  return (
    <Card>
      <h2 className={styles.heading}>Price</h2>

      <div className={styles.row}>
        <span>
          Fare × {passengerCount} passenger{passengerCount === 1 ? "" : "s"}
        </span>
        <span className="tnum">{formatUSD(flight.price_minor)}</span>
      </div>

      <div className={styles.total}>
        <span className={styles.totalLabel}>Total</span>
        <span className={`${styles.totalValue} tnum`}>{formatUSD(total)}</span>
      </div>

      {/* A6: fares are flat per passenger — no taxes or fees are modelled at
          all. A3: no payment is taken. Both need saying plainly rather than
          being papered over with a reassuring line that isn't true. */}
      <p className={styles.note}>
        Fares are flat per passenger; no taxes or fees are modelled. No payment
        is taken — this is a demonstration booking.
      </p>
    </Card>
  );
}
