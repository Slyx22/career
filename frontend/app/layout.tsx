import type { Metadata, Viewport } from "next";
import "@fontsource-variable/bricolage-grotesque";
import "@fontsource/instrument-sans/400.css";
import "@fontsource/instrument-sans/500.css";
import "@fontsource/instrument-sans/600.css";
import "./globals.css";
import AuthProvider from "@/components/AuthProvider";
import { MobileTabBar } from "@/components/MobileTabBar";

// Fonts are self-hosted via @fontsource (no request to Google, works offline).

export const metadata: Metadata = {
  // Makes share-preview image links absolute (needed by LinkedIn/WhatsApp).
  metadataBase: new URL("https://srmaps.co.za"),
  title: "Career Readiness Analyzer",
  description:
    "Upload your CV and discover how closely your skills match the requirements of your target career.",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover", // lets the glass tab bar sit above the iPhone home indicator
  themeColor: "#eef0f7",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="font-body text-ink antialiased">
        <AuthProvider>
          {children}
          <MobileTabBar />
        </AuthProvider>
      </body>
    </html>
  );
}
