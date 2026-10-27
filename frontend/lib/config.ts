// Server-side only. Never import this from a Client Component - the
// Python API URL should not be exposed to the browser.
export function getPythonApiUrl(): string {
  const url = process.env.PYTHON_API_URL;
  if (!url) {
    throw new Error(
      "PYTHON_API_URL is not configured. Set it in frontend/.env.local " +
        "to point at your running Python engine (see .env.example)."
    );
  }
  return url.replace(/\/$/, "");
}

// Calls the Python engine. If ENGINE_API_KEY is set (in Vercel, and the
// same value in Render), it is sent in the x-engine-key header so the
// engine only answers this website, not anyone who finds its URL.
export function engineFetch(
  path: string,
  init: RequestInit & { next?: { revalidate?: number } } = {}
): Promise<Response> {
  const headers = new Headers(init.headers);
  const key = process.env.ENGINE_API_KEY;
  if (key) headers.set("x-engine-key", key);
  return fetch(`${getPythonApiUrl()}${path}`, { ...init, headers });
}
