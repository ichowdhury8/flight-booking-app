/* Small supporting icons for the transfer mode. The mode word is always shown
   alongside, so these carry no information on their own — hence aria-hidden. */

const COMMON = {
  width: 18,
  height: 18,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.6,
  strokeLinecap: "round",
  strokeLinejoin: "round",
  "aria-hidden": "true",
};

function Rail() {
  return (
    <svg {...COMMON}>
      <rect x="5" y="3" width="14" height="13" rx="3.5" />
      <path d="M5 10h14" />
      <path d="M9.5 13h.01M14.5 13h.01" />
      <path d="M9 16l-2 4M15 16l2 4" />
    </svg>
  );
}

function Bus() {
  return (
    <svg {...COMMON}>
      <rect x="4" y="4" width="16" height="12" rx="2.5" />
      <path d="M4 10h16" />
      <circle cx="8" cy="18" r="1.4" />
      <circle cx="16" cy="18" r="1.4" />
      <path d="M6 16v1.5M18 16v1.5" />
    </svg>
  );
}

function Taxi() {
  return (
    <svg {...COMMON}>
      <path d="M3 15v-2.2a2 2 0 0 1 .3-1L5.6 8A2 2 0 0 1 7.3 7h9.4a2 2 0 0 1 1.7 1l2.3 3.8a2 2 0 0 1 .3 1V15a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1Z" />
      <path d="M3.6 12h16.8" />
      <circle cx="7.5" cy="16" r="1.4" />
      <circle cx="16.5" cy="16" r="1.4" />
      <path d="M10 7V5.5h4V7" />
    </svg>
  );
}

const ICONS = { train: Rail, metro: Rail, bus: Bus, taxi: Taxi };

export default function ModeIcon({ mode }) {
  const Icon = ICONS[mode] ?? Rail;
  return <Icon />;
}
