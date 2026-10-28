// Small stroke icons used in navigation. 24x24, inherit colour.
type P = { className?: string };
const base = {
  width: 22,
  height: 22,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.8,
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
  "aria-hidden": true,
};

export function HomeIcon({ className }: P) {
  return (
    <svg {...base} className={className}>
      <path d="M4 10.5 12 4l8 6.5V19a1 1 0 0 1-1 1h-4.5v-5.5h-5V20H5a1 1 0 0 1-1-1z" />
    </svg>
  );
}

export function ScanIcon({ className }: P) {
  return (
    <svg {...base} className={className}>
      <path d="M7 3H5a2 2 0 0 0-2 2v2M17 3h2a2 2 0 0 1 2 2v2M7 21H5a2 2 0 0 1-2-2v-2M17 21h2a2 2 0 0 0 2-2v-2" />
      <path d="M8 9h8M8 12h8M8 15h5" />
    </svg>
  );
}

export function BadgeIcon({ className }: P) {
  return (
    <svg {...base} className={className}>
      <circle cx="12" cy="9" r="5.5" />
      <path d="m9.5 13.8-1.5 6.7 4-2 4 2-1.5-6.7" />
      <path d="m10 9 1.4 1.4L14 7.8" />
    </svg>
  );
}

export function UserIcon({ className }: P) {
  return (
    <svg {...base} className={className}>
      <circle cx="12" cy="8.5" r="3.8" />
      <path d="M4.5 20c1.2-3.6 4-5.4 7.5-5.4s6.3 1.8 7.5 5.4" />
    </svg>
  );
}

/** Brand mark: a readiness ring, three-quarters full. */
export function MarkIcon({ className }: P) {
  return (
    <svg width="28" height="28" viewBox="0 0 28 28" className={className} aria-hidden="true">
      <circle cx="14" cy="14" r="10.5" fill="none" stroke="rgba(20,26,46,0.14)" strokeWidth="4" />
      <circle
        cx="14"
        cy="14"
        r="10.5"
        fill="none"
        stroke="url(#mark-grad)"
        strokeWidth="4"
        strokeLinecap="round"
        strokeDasharray="49.5 66"
        transform="rotate(-90 14 14)"
      />
      <defs>
        <linearGradient id="mark-grad" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#7C6BE0" />
          <stop offset="1" stopColor="#E3A94A" />
        </linearGradient>
      </defs>
    </svg>
  );
}
