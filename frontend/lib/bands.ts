// Mirrors python-engine/app/scoring/bands.py. A band describes how well a
// CV matches the occupation's skills; it is not an employer endorsement.
export const SEAL_THRESHOLD = 70;

const BANDS: [number, string, string][] = [
  [85, "excellent", "Excellent match"],
  [70, "strong", "Strong match"],
  [50, "developing", "Developing"],
  [0, "early", "Early stage"],
];

export function bandFor(score?: number | null) {
  const s = score ?? 0;
  const [, key, label] = BANDS.find(([min]) => s >= min) ?? BANDS[BANDS.length - 1];
  return { key, label, seal: s >= SEAL_THRESHOLD, pointsToSeal: Math.max(0, SEAL_THRESHOLD - s) };
}
