import { Link } from "react-router-dom";

import Button from "../components/ui/Button";
import Card from "../components/ui/Card";

/* Temporary. PassengerPage is task 11 and ConfirmationPage is task 12; this
 * exists only so the "Select" action on a flight card leads somewhere
 * self-explanatory instead of falling through to the 404 page. Delete it once
 * both real pages exist. */
export default function PlaceholderPage({ title, task }) {
  return (
    <Card style={{ maxWidth: "56ch" }}>
      <h1 style={{ fontSize: "var(--text-xl)" }}>{title}</h1>
      <p style={{ color: "var(--text-muted)", margin: "var(--space-3) 0 var(--space-5)" }}>
        Not built yet — this page arrives in task {task}. The route resolves so
        the flow can be walked end to end.
      </p>
      <Button as={Link} to="/" variant="secondary" size="sm">
        Back to search
      </Button>
    </Card>
  );
}
