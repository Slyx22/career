import { bandFor } from "@/lib/bands";

/** The recognition seal shown on 70+ certificates. */
export function Seal({ score, size = 88 }: { score: number; size?: number }) {
  const band = bandFor(score);
  if (!band.seal) return null;
  const [first, ...rest] = band.label.split(" ");
  return (
    <div
      className="relative flex shrink-0 flex-col items-center justify-center rounded-full text-center text-white"
      style={{
        width: size,
        height: size,
        background: "radial-gradient(circle at 30% 25%, #E3A94A, #B8801F 60%, #8F6317)",
        boxShadow: "inset 0 1px 0 rgba(255,255,255,0.5), 0 10px 22px -10px rgba(143,99,23,0.7)",
      }}
      role="img"
      aria-label={`${band.label}: scored 70 or more`}
    >
      <span className="absolute inset-[5px] rounded-full border border-white/50" aria-hidden="true" />
      <span className="font-display font-semibold leading-tight" style={{ fontSize: size * 0.15 }} aria-hidden="true">
        {first}
        <br />
        {rest.join(" ")}
      </span>
      <span className="mt-0.5 opacity-90" style={{ fontSize: size * 0.11 }} aria-hidden="true">
        70+
      </span>
    </div>
  );
}
