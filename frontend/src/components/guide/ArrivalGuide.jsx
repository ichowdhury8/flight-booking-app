import AttractionCard, { attractionStyles } from "./AttractionCard";
import TransferCallout from "./TransferCallout";
import styles from "./ArrivalGuide.module.css";

/* The custom feature. Every field below is read from SQLite via the booking
 * response — nothing here calls an external service at runtime.
 *
 * Visual hierarchy is deliberate: the transfer callout is the hero, because it
 * is the part a traveller actually acts on when they land. The attractions are
 * secondary and styled to stay that way.
 */
export default function ArrivalGuide({ guide }) {
  return (
    <section className={styles.guide} aria-labelledby="guide-city">
      <header className={styles.header}>
        {/* The country lives here, not in the heading. Nested inside the h2 it
            inherited the serif, and the spec is the city name only. */}
        <p className={styles.eyebrow}>Arrival guide · {guide.country}</p>
        {/* SERIF #2 of 4 — see global.css */}
        <h2 className={`display ${styles.city}`} id="guide-city">
          {guide.city}
        </h2>
        <p className={styles.intro}>{guide.intro}</p>
      </header>

      <TransferCallout
        transport={guide.transport}
        distanceKm={guide.distance_km}
      />

      <div className={styles.attractions}>
        <h3 className={styles.attractionsHeading}>While you're there</h3>

        <ul className={attractionStyles.list}>
          {guide.attractions.map((attraction) => (
            <AttractionCard key={attraction.name} attraction={attraction} />
          ))}
        </ul>
      </div>

      {/* A13: this content is general knowledge, not authoritative. */}
      <p className={styles.disclaimer}>
        Distances, journey times and fares are approximate.
      </p>
    </section>
  );
}
