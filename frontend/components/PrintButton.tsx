"use client";

export function PrintButton() {
  return (
    <button onClick={() => window.print()} className="glass btn-glass">
      Print certificate
    </button>
  );
}
