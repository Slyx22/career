"use client";

import { useEffect } from "react";
import { track, TrackData, TrackEvent } from "@/lib/track";

/** Records an anonymous page-view event once, from a Server Component page. */
export function TrackView({ event, ...data }: { event: TrackEvent } & TrackData) {
  useEffect(() => {
    track(event, data);
    // Once per page load is what we want.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  return null;
}
