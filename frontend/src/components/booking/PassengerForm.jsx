import { useState } from "react";

import { toISODate } from "../../lib/format";
import Button from "../ui/Button";
import ErrorBanner from "../ui/ErrorBanner";
import Field from "../ui/Field";
import styles from "./PassengerForm.module.css";

/* Deliberately permissive — one "@" with something either side. The server
 * validates properly with EmailStr; this only exists to catch a typo before a
 * round-trip, and a stricter regex would reject valid addresses. */
const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function blankPassenger() {
  return { first_name: "", last_name: "", date_of_birth: "" };
}

export function validate(passengers, contact) {
  const errors = {};

  passengers.forEach((p, i) => {
    if (!p.first_name.trim()) errors[`p${i}.first_name`] = "Enter a first name.";
    if (!p.last_name.trim()) errors[`p${i}.last_name`] = "Enter a last name.";
    if (p.date_of_birth && p.date_of_birth > toISODate(new Date())) {
      errors[`p${i}.date_of_birth`] = "Date of birth can't be in the future.";
    }
  });

  if (!contact.email.trim()) errors["contact.email"] = "Enter an email address.";
  else if (!EMAIL.test(contact.email.trim())) {
    errors["contact.email"] = "Enter a valid email address.";
  }

  return errors;
}

export default function PassengerForm({ count, submitting, submitError, onSubmit }) {
  const [passengers, setPassengers] = useState(() =>
    Array.from({ length: count }, blankPassenger),
  );
  const [contact, setContact] = useState({ email: "", phone: "" });
  const [errors, setErrors] = useState({});

  function updatePassenger(index, key, value) {
    setPassengers((current) =>
      current.map((p, i) => (i === index ? { ...p, [key]: value } : p)),
    );
  }

  function handleSubmit(event) {
    event.preventDefault();

    const found = validate(passengers, contact);
    setErrors(found);
    if (Object.keys(found).length > 0) {
      // Move focus to the first problem so keyboard and screen-reader users
      // aren't left guessing why nothing happened.
      document.querySelector('[aria-invalid="true"]')?.focus();
      return;
    }

    onSubmit({
      contact_email: contact.email.trim(),
      contact_phone: contact.phone.trim() || null,
      passengers: passengers.map((p) => ({
        first_name: p.first_name.trim(),
        last_name: p.last_name.trim(),
        date_of_birth: p.date_of_birth || null,
      })),
    });
  }

  return (
    <form onSubmit={handleSubmit} noValidate>
      {submitError && (
        <div className={styles.banner}>
          <ErrorBanner>{submitError}</ErrorBanner>
        </div>
      )}

      <section className={styles.section}>
        <h2 className={styles.legend}>
          {count === 1 ? "Passenger" : `Passengers (${count})`}
        </h2>

        {passengers.map((passenger, index) => (
          <fieldset key={index} className={styles.fieldset}>
            {count > 1 && (
              <legend className={styles.passengerLegend}>
                Passenger {index + 1}
              </legend>
            )}

            <div className={styles.grid}>
              <Field label="First name" error={errors[`p${index}.first_name`]}>
                {(props) => (
                  <input
                    {...props}
                    type="text"
                    autoComplete="given-name"
                    maxLength={60}
                    value={passenger.first_name}
                    onChange={(e) =>
                      updatePassenger(index, "first_name", e.target.value)
                    }
                  />
                )}
              </Field>

              <Field label="Last name" error={errors[`p${index}.last_name`]}>
                {(props) => (
                  <input
                    {...props}
                    type="text"
                    autoComplete="family-name"
                    maxLength={60}
                    value={passenger.last_name}
                    onChange={(e) =>
                      updatePassenger(index, "last_name", e.target.value)
                    }
                  />
                )}
              </Field>

              <Field
                label="Date of birth"
                hint="Optional"
                error={errors[`p${index}.date_of_birth`]}
              >
                {(props) => (
                  <input
                    {...props}
                    type="date"
                    max={toISODate(new Date())}
                    value={passenger.date_of_birth}
                    onChange={(e) =>
                      updatePassenger(index, "date_of_birth", e.target.value)
                    }
                  />
                )}
              </Field>
            </div>
          </fieldset>
        ))}
      </section>

      <section className={styles.section}>
        <h2 className={styles.legend}>Contact details</h2>

        <div className={styles.grid}>
          <Field
            label="Email"
            error={errors["contact.email"]}
            hint="Your confirmation is shown on screen — no email is sent."
          >
            {(props) => (
              <input
                {...props}
                type="email"
                autoComplete="email"
                value={contact.email}
                onChange={(e) =>
                  setContact((c) => ({ ...c, email: e.target.value }))
                }
              />
            )}
          </Field>

          <Field label="Phone" hint="Optional">
            {(props) => (
              <input
                {...props}
                type="tel"
                autoComplete="tel"
                maxLength={40}
                value={contact.phone}
                onChange={(e) =>
                  setContact((c) => ({ ...c, phone: e.target.value }))
                }
              />
            )}
          </Field>
        </div>
      </section>

      <div className={styles.actions}>
        <Button type="submit" size="lg" disabled={submitting}>
          {submitting ? "Confirming…" : "Confirm booking"}
        </Button>
      </div>
    </form>
  );
}
