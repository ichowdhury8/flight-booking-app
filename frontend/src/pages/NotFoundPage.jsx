import { Link } from "react-router-dom";

import Button from "../components/ui/Button";
import styles from "./NotFoundPage.module.css";

export default function NotFoundPage() {
  return (
    <div className={styles.wrap}>
      {/* SERIF #4 of 4 — see global.css */}
      <h1 className={`display ${styles.title}`}>Nothing here</h1>
      <p className={styles.body}>
        That page doesn't exist. The link may be mistyped, or the booking
        reference may have expired.
      </p>
      <Button as={Link} to="/">
        Start a new search
      </Button>
    </div>
  );
}
