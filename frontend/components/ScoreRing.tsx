// Readiness score as a ring, used on the home page, results and certificates.
// Server-renderable; the fill animation is CSS and respects reduced motion.
export function ScoreRing({
  score,
  size = 112,
  animate = false,
  id = "ring",
}: {
  score: number;
  size?: number;
  animate?: boolean;
  id?: string;
}) {
  const clamped = Math.max(0, Math.min(100, Math.round(score)));
  const r = 44;
  const len = 2 * Math.PI * r;
  const gradId = `${id}-grad`;
  return (
    <div
      className="relative shrink-0"
      style={{ width: size, height: size }}
      role="img"
      aria-label={`Career readiness score: ${clamped} out of 100`}
    >
      <svg viewBox="0 0 100 100" className="h-full w-full -rotate-90" aria-hidden="true">
        <circle cx="50" cy="50" r={r} fill="none" stroke="rgba(20,26,46,0.08)" strokeWidth="9" />
        {clamped > 0 && (
          <circle
            className={animate ? "ring-animate" : undefined}
            style={{ ["--ring-len" as string]: `${len}` }}
            cx="50"
            cy="50"
            r={r}
            fill="none"
            stroke={`url(#${gradId})`}
            strokeWidth="9"
            strokeLinecap="round"
            strokeDasharray={len}
            strokeDashoffset={len * (1 - clamped / 100)}
          />
        )}
        <defs>
          <linearGradient id={gradId} x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stopColor="#7C6BE0" />
            <stop offset="1" stopColor="#E3A94A" />
          </linearGradient>
        </defs>
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center" aria-hidden="true">
        <span className="font-display font-semibold leading-none" style={{ fontSize: size * 0.27 }}>
          {clamped}
        </span>
        <span className="mt-1 text-slate" style={{ fontSize: Math.max(10, size * 0.1) }}>
          out of 100
        </span>
      </div>
    </div>
  );
}
