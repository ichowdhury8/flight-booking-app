import styles from "./Footer.module.css";

export default function Footer() {
  return (
    <footer className={styles.footer}>
      <div className={`container ${styles.inner}`}>
        {/* A3: no payment is taken and no email is sent. Say so rather than
            letting the UI imply otherwise. */}
        <span>A demonstration booking app. No payment is taken.</span>
        <span>Flight schedules and fares are illustrative.</span>
      </div>
    </footer>
  );
}
