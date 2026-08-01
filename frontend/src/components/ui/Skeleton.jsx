import styles from "./Skeleton.module.css";

export default function Skeleton({ height, width, className = "" }) {
  return (
    <div
      className={`${styles.skeleton} ${className}`}
      style={{ height, width }}
      aria-hidden="true"
    />
  );
}

export function FlightCardSkeleton() {
  return <div className={`${styles.skeleton} ${styles.cardSkeleton}`} aria-hidden="true" />;
}
