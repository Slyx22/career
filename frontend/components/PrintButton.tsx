"use client";

export function PrintButton() {
  return (
    <button
      onClick={() => window.print()}
      className="focus-ring rounded border border-line px-6 py-3 font-body text-sm text-ink hover:border-ink"
    >
      Print certificate
    </button>
  );
}
