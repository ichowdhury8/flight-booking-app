import Field, { fieldStyles } from "../ui/Field";

export default function AirportSelect({
  label,
  value,
  onChange,
  airports,
  exclude,
  error,
  disabled,
}) {
  return (
    <Field label={label} error={error}>
      {({ className, ...controlProps }) => (
        <select
          {...controlProps}
          className={`${className} ${fieldStyles.select}`}
          value={value}
          disabled={disabled}
          onChange={(event) => onChange(event.target.value)}
        >
          <option value="">Select an airport</option>
          {airports.map((airport) => (
            <option
              key={airport.iata_code}
              value={airport.iata_code}
              /* Same-city is rejected by the API with a 400; disabling it here
                 means the user never gets that far. */
              disabled={airport.iata_code === exclude}
            >
              {airport.city} ({airport.iata_code})
            </option>
          ))}
        </select>
      )}
    </Field>
  );
}
