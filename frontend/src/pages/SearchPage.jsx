import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { getAirports, searchFlights } from "../api/client";
import EmptyState from "../components/search/EmptyState";
import FlightCard from "../components/search/FlightCard";
import SearchForm from "../components/search/SearchForm";
import Card from "../components/ui/Card";
import ErrorBanner from "../components/ui/ErrorBanner";
import { FlightCardSkeleton } from "../components/ui/Skeleton";
import { formatDate } from "../lib/format";
import styles from "./SearchPage.module.css";

/* The URL is the state. A reload or a shared link reproduces the same results
 * with no store and no router state to rehydrate (PLAN.md §5.2). */
function readQuery(searchParams) {
  const passengers = Number(searchParams.get("passengers") ?? 1);
  return {
    origin: searchParams.get("origin") ?? "",
    destination: searchParams.get("destination") ?? "",
    date: searchParams.get("date") ?? "",
    passengers:
      Number.isInteger(passengers) && passengers >= 1 && passengers <= 9
        ? passengers
        : 1,
  };
}

export default function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const query = readQuery(searchParams);
  const hasQuery = Boolean(query.origin && query.destination && query.date);

  const [airports, setAirports] = useState([]);
  const [airportsError, setAirportsError] = useState(null);

  const [flights, setFlights] = useState(null);
  const [loading, setLoading] = useState(false);
  const [searchError, setSearchError] = useState(null);

  useEffect(() => {
    let active = true;
    getAirports()
      .then((data) => active && setAirports(data))
      .catch((error) => active && setAirportsError(error.message));
    return () => {
      active = false;
    };
  }, []);

  const { origin, destination, date, passengers } = query;

  useEffect(() => {
    if (!hasQuery) {
      setFlights(null);
      return undefined;
    }

    let active = true;
    setLoading(true);
    setSearchError(null);

    searchFlights({ origin, destination, date, passengers })
      .then((data) => active && setFlights(data))
      .catch((error) => {
        if (!active) return;
        setSearchError(error.message);
        setFlights(null);
      })
      .finally(() => active && setLoading(false));

    return () => {
      active = false;
    };
  }, [hasQuery, origin, destination, date, passengers]);

  const cityByCode = useMemo(
    () => Object.fromEntries(airports.map((a) => [a.iata_code, a.city])),
    [airports],
  );

  function handleSearch(next) {
    setSearchParams(
      {
        origin: next.origin,
        destination: next.destination,
        date: next.date,
        passengers: String(next.passengers),
      },
      { replace: false },
    );
  }

  return (
    <>
      <div className={styles.hero}>
        {/* SERIF #1 of 4 — see global.css */}
        <h1 className={`display ${styles.heroTitle}`}>Where to next?</h1>
        <p className={styles.heroSub}>
          One-way fares across six cities, for the next two weeks.
        </p>
      </div>

      <Card className={styles.formCard}>
        {airportsError ? (
          <ErrorBanner>{airportsError}</ErrorBanner>
        ) : (
          <SearchForm
            airports={airports}
            initial={query}
            onSearch={handleSearch}
            loading={loading}
          />
        )}
      </Card>

      {hasQuery && (
        <section className={styles.results} aria-live="polite">
          <div className={styles.resultsHeader}>
            <h2 className={styles.resultsTitle}>
              {loading
                ? "Searching…"
                : `${flights?.length ?? 0} flight${
                    flights?.length === 1 ? "" : "s"
                  }`}
            </h2>
            <p className={styles.resultsMeta}>
              {cityByCode[origin] ?? origin} → {cityByCode[destination] ?? destination}
              {" · "}
              <span className="tnum">{formatDate(`${date}T00:00:00`)}</span>
              {passengers > 1 && ` · ${passengers} passengers`}
            </p>
          </div>

          {searchError && <ErrorBanner>{searchError}</ErrorBanner>}

          {loading && (
            <div className={styles.list}>
              <FlightCardSkeleton />
              <FlightCardSkeleton />
              <FlightCardSkeleton />
            </div>
          )}

          {!loading && !searchError && flights?.length === 0 && (
            <EmptyState passengers={passengers} />
          )}

          {!loading && !searchError && flights?.length > 0 && (
            <ul className={styles.list}>
              {flights.map((flight) => (
                <FlightCard
                  key={flight.id}
                  flight={flight}
                  passengers={passengers}
                  searchParams={searchParams.toString()}
                />
              ))}
            </ul>
          )}
        </section>
      )}

      {!hasQuery && (
        <p className={styles.prompt}>
          Pick two cities and a date to see what's flying.
        </p>
      )}
    </>
  );
}
