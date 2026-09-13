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
  // Try the live Python engine first.
  try {
    const res = await fetch(`${getPythonApiUrl()}/api/careers`, { cache: "no-store" });
    if (res.ok) {
      const data = await res.json();
      if (Array.isArray(data?.careers) && data.careers.length > 0) {
        return NextResponse.json(data);
      }
    }
  } catch {
    // Engine not reachable (e.g. local dev without it, or Netlify).
  }

  // Fallback to the bundled static list (always available).
  const data = await loadStaticCareers();
  if (data && Array.isArray(data?.careers) && data.careers.length > 0) {
    return NextResponse.json(data);
  }

  return NextResponse.json(
    { error: "Could not load careers." },
    { status: 503 }
  );
}
