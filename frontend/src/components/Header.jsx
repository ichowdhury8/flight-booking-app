import { Link } from "react-router-dom";

import styles from "./Header.module.css";

export default function Header() {
  return (
    <header className={styles.header}>
      <div className={`container ${styles.inner}`}>
        <Link to="/" className={styles.wordmark}>
          <span className={styles.dot} aria-hidden="true" />
          Meridian
        </Link>
      </div>
    </header>
  );
}
