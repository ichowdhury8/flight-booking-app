import { distanceParts } from "../../lib/format";
import ModeIcon from "./ModeIcon";
import styles from "./TransferCallout.module.css";

export default function TransferCallout({ transport, distanceKm }) {
  const { miles, kilometres } = distanceParts(distanceKm);

  return (
    <section className={styles.callout} aria-labelledby="transfer-heading">
      <div className={styles.top}>
        <div>
          <p className={styles.eyebrow} id="transfer-heading">
            Getting into the city
          </p>
          <p className={styles.service}>{transport.name}</p>
        </div>

        <span className={styles.modePill}>
          <ModeIcon mode={transport.mode} />
          {transport.mode}
        </span>
      </div>

      <div className={styles.stats}>
        <div>
          <p className={`${styles.statValue} tnum`}>
            {transport.minutes}
            <span className={styles.statUnit}> min</span>
          </p>
          <p className={styles.statLabel}>Journey time</p>
        </div>

        <div>
          <p className={`${styles.statValue} tnum`}>
            {miles}
            <span className={styles.statUnit}> mi ({kilometres} km)</span>
          </p>
          <p className={styles.statLabel}>To the city centre</p>
        </div>

        {transport.cost_note && (
          <div className={styles.fareCell}>
            {/* Deliberately smaller than the two figures beside it: the cost
                note is free prose in the destination's own currency (A16) and
                runs from "~€6 one way" to a full sentence. Sizing it like a
                number would break the row on the longer ones. */}
            <p className={styles.statNote}>{transport.cost_note}</p>
            <p className={styles.statLabel}>Approximate fare</p>
          </div>
        )}
      </div>

      {transport.notes && <p className={styles.notes}>{transport.notes}</p>}
    </section>
  );
}
