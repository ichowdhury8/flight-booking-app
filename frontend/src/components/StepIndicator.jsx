import { Fragment } from "react";

import styles from "./StepIndicator.module.css";

const STEPS = ["Search", "Passengers", "Confirmation"];

export default function StepIndicator({ step }) {
  return (
    <ol className={styles.steps}>
      {STEPS.map((label, index) => {
        const number = index + 1;
        const state =
          number === step ? "current" : number < step ? "done" : "upcoming";

        return (
          <Fragment key={label}>
            {index > 0 && <li className={styles.sep} aria-hidden="true" />}
            <li
              className={`${styles.step} ${styles[state] ?? ""}`}
              aria-current={number === step ? "step" : undefined}
            >
              <span className={styles.marker} aria-hidden="true">
                {number}
              </span>
              <span
                className={`${styles.label} ${
                  number === step ? styles.currentLabel : ""
                }`}
              >
                {label}
              </span>
            </li>
          </Fragment>
        );
      })}
    </ol>
  );
}
