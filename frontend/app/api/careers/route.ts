import { NextResponse } from "next/server";
import { promises as fs } from "fs";
import path from "path";
import { getPythonApiUrl } from "@/lib/config";

async function loadStaticCareers() {
  try {
    const p = path.join(process.cwd(), "public", "data", "careers.json");
    const raw = await fs.readFile(p, "utf-8");
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export async function GET() {
  // Try the live Python engine first (with caching for 5 minutes).
  try {
    const res = await fetch(`${getPythonApiUrl()}/api/careers`, {
      cache: "force-cache",
      next: { revalidate: 300 } // Cache for 5 minutes (300 seconds)
    });
    if (res.ok) {
      const data = await res.json();
      if (Array.isArray(data?.careers) && data.careers.length > 0) {
        return NextResponse.json(data, {
          headers: {
            'Cache-Control': 'public, s-maxage=300, stale-while-revalidate=600'
          }
        });
      }
    }
  } catch {
    // Engine not reachable (e.g. local dev without it, or Netlify).
  }

  // Fallback to the bundled static list (always available).
  const data = await loadStaticCareers();
  if (data && Array.isArray(data?.careers) && data.careers.length > 0) {
    return NextResponse.json(data, {
      headers: {
        'Cache-Control': 'public, s-maxage=3600, stale-while-revalidate=86400' // Cache for 1 hour
      }
    });
  }

  return NextResponse.json(
    { error: "Could not load careers." },
    { status: 503 }
  );
}
