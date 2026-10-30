/**
 * Anonymous usage tracking for the founder's /admin dashboard.
 *
 * Records which step someone reached and the career involved. Never sends
 * a name, email, CV text or account ID. The only identifier is a random ID
 * kept in this browser's local storage, so we can count unique people;
 * clearing browser data resets it. Covered in the Privacy Policy
 * ("Usage statistics").
 *
 * Tracking must never break or slow the site, so every failure is ignored.
 */

export const TRACK_EVENTS = [
  "analyze_view",
  "career_selected",
  "file_chosen",
  "check_submitted",
  "check_completed",
  "check_failed",
  "results_view",
  "certificate_clicked",
  "certificate_view",
  "share_clicked",
] as const;

export type TrackEvent = (typeof TRACK_EVENTS)[number];

export type TrackData = {
  career?: string | null; // career slug
  careerLabel?: string | null; // the job title shown to the person
  detail?: string | null; // short non-personal detail, e.g. "whatsapp" or "docx"
};

const VISITOR_KEY = "srmaps_vid";

function visitorId(): string | null {
  try {
    let id = window.localStorage.getItem(VISITOR_KEY);
    if (!id) {
      id = crypto.randomUUID();
      window.localStorage.setItem(VISITOR_KEY, id);
    }
    return id;
  } catch {
    return null;
  }
}

export function track(event: TrackEvent, data: TrackData = {}): void {
  try {
    if (typeof window === "undefined") return;
    const body = JSON.stringify({
      event,
      career: data.career ?? null,
      careerLabel: data.careerLabel ?? null,
      detail: data.detail ?? null,
      visitorId: visitorId(),
    });
    const blob = new Blob([body], { type: "application/json" });
    if (navigator.sendBeacon && navigator.sendBeacon("/api/events", blob)) return;
    void fetch("/api/events", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body,
      keepalive: true,
    }).catch(() => {});
  } catch {
    /* never let analytics break the page */
  }
}

/** Lower-case file extension, or "none". Used as the detail for file events. */
export function fileKind(name: string | undefined | null): string {
  const m = /\.([a-z0-9]{1,5})$/i.exec(name ?? "");
  return m ? m[1].toLowerCase() : "none";
}

/** Turns an error message from the engine into a short, non-personal reason. */
export function failureReason(status: number, message: string | undefined | null): string {
  const m = (message ?? "").toLowerCase();
  if (status === 503 || status === 502 || status === 504) return "engine_down";
  if (m.includes("photo") || m.includes("picture")) return "photo";
  if (m.includes("password")) return "password";
  if (m.includes("too large")) return "too_large";
  if (m.includes("type of file") || m.includes("unsupported file")) return "file_type";
  if (m.includes("no readable text") || m.includes("empty") || m.includes("unreadable")) return "no_text";
  if (m.includes("damaged") || m.includes("couldn't open") || m.includes("couldn't read")) return "damaged";
  if (status === 0) return "network";
  return "other";
}
