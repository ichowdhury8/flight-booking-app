import styles from "./ErrorBanner.module.css";

export default function ErrorBanner({ children }) {
  return (
    <div className={styles.banner} role="alert">
      <span className={styles.mark} aria-hidden="true">
        !
      </span>
      <span>{children}</span>
    </div>
  );
}
