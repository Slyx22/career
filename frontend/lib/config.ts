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
