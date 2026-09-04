// A semicircular calibration dial, 0-100, used as the primary visual for
// a readiness score. Rendered server-side as static SVG - no client JS
// needed to display it.

function polarToCartesian(cx: number, cy: number, r: number, angleDeg: number) {
  const angleRad = ((angleDeg - 180) * Math.PI) / 180.0;
  return {
    x: cx + r * Math.cos(angleRad),
    y: cy + r * Math.sin(angleRad),
  };
}

function describeArc(cx: number, cy: number, r: number, startAngle: number, endAngle: number) {
  const start = polarToCartesian(cx, cy, r, endAngle);
  const end = polarToCartesian(cx, cy, r, startAngle);
  const largeArcFlag = endAngle - startAngle <= 180 ? "0" : "1";
  return `M ${start.x} ${start.y} A ${r} ${r} 0 ${largeArcFlag} 0 ${end.x} ${end.y}`;
}

export function ReadinessGauge({
  score,
  size = 260,
}: {
  score: number;
  size?: number;
}) {
  const cx = size / 2;
  const cy = size / 2 + 6;
  const r = size / 2 - 24;
  const clamped = Math.max(0, Math.min(100, score));
  const scoreAngle = (clamped / 100) * 180;

  const ticks = Array.from({ length: 11 }, (_, i) => i * 10);

  return (
    <svg
      viewBox={`0 0 ${size} ${size / 2 + 40}`}
      width={size}
      height={size / 2 + 40}
      role="img"
      aria-label={`Career readiness score: ${clamped} out of 100`}
    >
      <path
        d={describeArc(cx, cy, r, 0, 180)}
        fill="none"
        stroke="#D8DCD6"
        strokeWidth={14}
        strokeLinecap="butt"
      />
      <path
        d={describeArc(cx, cy, r, 0, scoreAngle)}
        fill="none"
        stroke="#B8801F"
        strokeWidth={14}
        strokeLinecap="butt"
      />
      {ticks.map((t) => {
        const angle = (t / 100) * 180;
        const inner = polarToCartesian(cx, cy, r - 12, angle);
        const outer = polarToCartesian(cx, cy, r + 2, angle);
        return (
          <line
            key={t}
            x1={inner.x}
            y1={inner.y}
            x2={outer.x}
            y2={outer.y}
            stroke="#8891A0"
            strokeWidth={1}
          />
        );
      })}
      <text
        x={cx}
        y={cy - 18}
        textAnchor="middle"
        className="font-display"
        fontSize={size * 0.22}
        fill="#141A2E"
      >
        {clamped}
      </text>
      <text
        x={cx}
        y={cy + 8}
        textAnchor="middle"
        fontSize={13}
        fill="#5B6472"
        fontFamily="var(--font-plex)"
      >
        out of 100
      </text>
    </svg>
  );
}
