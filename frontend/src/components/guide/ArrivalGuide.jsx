import { formatDistance } from "../../lib/format";

/* ---------------------------------------------------------------------------
 * DELIBERATELY UNSTYLED — task 14 builds the real UI.
 *
 * This renders the guide data faithfully so the whole happy path is walkable
 * and the content is reviewable, but it has no stylesheet of its own on
 * purpose. In particular:
 *
 *   - The destination city name is SERIF #2 of 4. It is Inter here; the
 *     `.display` class goes on at task 14 along with the rest of <GuideHeader>.
 *   - <TransferCallout> gets the --accent-wash block at task 14.
 *   - <AttractionCard> becomes real cards at task 14. Attraction names stay
 *     Inter 600 — they are the most tempting place to reach for the serif and
 *     the instruction was city name only.
 *
 * Rendered conditionally by the caller so a missing guide degrades quietly
 * (PLAN.md R7).
 * ------------------------------------------------------------------------- */
export default function ArrivalGuide({ guide }) {
  const { transport } = guide;

  return (
    <section>
      <h2>Arriving in {guide.city}</h2>
      <p>{guide.intro}</p>

      <h3>Getting into the city</h3>
      <p>
        {formatDistance(guide.distance_km)} from {guide.airport.name} (
        {guide.airport.iata_code}) to the city centre.
      </p>
      <p>
        <strong>{transport.name}</strong> ({transport.mode}) — about{" "}
        {transport.minutes} minutes
        {transport.cost_note ? `, ${transport.cost_note}` : ""}.
      </p>
      {transport.notes && <p>{transport.notes}</p>}

      <h3>While you're there</h3>
      <ul>
        {guide.attractions.map((attraction) => (
          <li key={attraction.name}>
            <strong>{attraction.name}</strong> ({attraction.category}) —{" "}
            {attraction.description}
          </li>
        ))}
      </ul>

      <p>
        <small>Distances and journey times are approximate.</small>
      </p>
    </section>
  );
}
