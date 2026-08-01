import styles from "./EmptyState.module.css";

/* Defensive fallback only. Every route is seeded on every day of the bookable
 * window and the date picker is bounded to match, so this should be unreachable
 * in normal use (PLAN.md R6). It exists so that if it ever is reached, the page
 * says something useful instead of rendering an empty list. */
export default function EmptyState({ passengers }) {
  return (
    <div className={styles.empty}>
      <p className={styles.title}>No flights match that search</p>
      <p className={styles.body}>
        {passengers > 1
          ? `There may not be ${passengers} seats left together on this route. Try a different date or fewer passengers.`
          : "Try a different date or a different pair of cities."}
      </p>
    </div>
  );
}
