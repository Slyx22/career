import { Header } from "@/components/Header";

/**
 * Shown the instant someone taps a link to a page that has to fetch data
 * (from the analysis engine, which can take a while to wake up). Without
 * it the old page stays on screen with no sign the tap worked, then jumps.
 */
export function PageSkeleton({
  width = "max-w-2xl",
  blocks = 3,
  message,
}: {
  width?: string;
  blocks?: number;
  message?: string;
}) {
  return (
    <div className="min-h-screen">
      <Header />
      <main className={`page-top page-bottom mx-auto ${width} space-y-5 px-4 sm:px-6`} aria-busy="true">
        <div className="space-y-3 px-1">
          <div className="skeleton h-8 w-2/3" />
          <div className="skeleton h-4 w-1/2" />
        </div>
        {Array.from({ length: blocks }, (_, i) => (
          <div key={i} className="glass-sheet space-y-3 p-6 sm:p-8">
            <div className="skeleton h-5 w-1/3" />
            <div className="skeleton h-4 w-full" />
            <div className="skeleton h-4 w-5/6" />
          </div>
        ))}
        <p className="px-1 text-center text-sm text-slate" role="status">
          {message ?? "Loading…"}
        </p>
      </main>
    </div>
  );
}
