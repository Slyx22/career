"use client";

import { useEffect, useState } from "react";
import { CertificateVerification } from "@/lib/types";
import {
  facebookUrl,
  linkedInAddToProfileUrl,
  linkedInPostUrl,
  shareText,
  shareTitle,
  verifyUrl,
  whatsAppUrl,
  xUrl,
} from "@/lib/certificate";

const btn =
  "focus-ring inline-flex min-h-[44px] items-center justify-center gap-2 rounded-full border border-white/70 bg-white/55 px-4 py-2.5 text-sm font-medium text-ink transition-colors hover:bg-white/80";
const primary = "btn-primary";

export function ShareCertificate({ cert }: { cert: CertificateVerification }) {
  const id = cert.certificate_id ?? "";
  const link = verifyUrl(id);
  const [copied, setCopied] = useState(false);

  async function copyLink() {
    try {
      await navigator.clipboard.writeText(link);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    } catch {
      window.prompt("Copy this link:", link);
    }
  }

  async function nativeShare() {
    try {
      await navigator.share({ title: shareTitle(cert), text: shareText(cert), url: link });
    } catch {
      /* cancelled */
    }
  }

  // Decided after mounting, so the server and browser render the same HTML.
  const [canNativeShare, setCanNativeShare] = useState(false);
  useEffect(() => {
    setCanNativeShare(typeof navigator !== "undefined" && typeof navigator.share === "function");
  }, []);

  return (
    <div className="glass-sheet p-6 sm:p-8">
      <h2 className="font-display text-xl font-semibold tracking-tight">Share your certificate</h2>
      <p className="mt-1 text-sm text-slate">
        Anyone with the link can check it&apos;s genuine. It shows your name, the career, your score and the dates,
        never your CV.
      </p>

      <div className="mt-5 grid grid-cols-1 gap-3 sm:grid-cols-2">
        <a className={primary} href={linkedInAddToProfileUrl(cert)} target="_blank" rel="noopener noreferrer">
          Add to LinkedIn profile
        </a>
        <a className={btn} href={linkedInPostUrl(id)} target="_blank" rel="noopener noreferrer">
          Post on LinkedIn
        </a>
        <a className={btn} href={whatsAppUrl(cert)} target="_blank" rel="noopener noreferrer">
          Share on WhatsApp
        </a>
        <a className={btn} href={facebookUrl(id)} target="_blank" rel="noopener noreferrer">
          Share on Facebook
        </a>
        <a className={btn} href={xUrl(cert)} target="_blank" rel="noopener noreferrer">
          Share on X
        </a>
        <button type="button" className={btn} onClick={copyLink}>
          {copied ? "Link copied ✓" : "Copy link"}
        </button>
        {canNativeShare && (
          <button type="button" className={`${btn} sm:col-span-2`} onClick={nativeShare}>
            More sharing options&hellip;
          </button>
        )}
      </div>

      <h3 className="mt-7 text-sm font-semibold text-slate">Download</h3>
      <div className="mt-2 flex flex-wrap gap-3">
        <a className={btn} href={`/api/certificate/${encodeURIComponent(id)}/pdf`}>
          PDF certificate
        </a>
        <a className={btn} href={`/api/certificate/${encodeURIComponent(id)}/image?shape=square`}>
          Image for posts and status
        </a>
        <a className={btn} href={`/api/certificate/${encodeURIComponent(id)}/image?shape=wide`}>
          Wide image
        </a>
      </div>
      <p className="mt-5 text-xs text-slate">
        Tip: on LinkedIn, &ldquo;Add to profile&rdquo; puts it under Licenses &amp; certifications with a link back to
        this verification page.
      </p>
    </div>
  );
}
