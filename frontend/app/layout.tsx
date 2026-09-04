import type { Metadata } from "next";
import "./globals.css";
import AuthProvider from "@/components/AuthProvider";

// Fonts are loaded via CSS (see globals.css) rather than next/font/google.
// next/font/google requires build-time network access to
// fonts.googleapis.com, which is not guaranteed in every environment
// (e.g. sandboxed CI, offline dev). Loading via a <link> tag with solid
// system-font fallbacks keeps local builds reliable everywhere while still
// getting the intended typefaces wherever the network is available.

export const metadata: Metadata = {
  title: "Career Readiness Analyzer",
  description:
    "Upload your CV and discover how closely your skills match the requirements of your target career.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=Newsreader:ital,wght@0,400;0,500;0,600;1,400;1,500;1,600&family=IBM+Plex+Sans:wght@400;500;600&display=swap"
        />
      </head>
      <body className="font-body antialiased">
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
