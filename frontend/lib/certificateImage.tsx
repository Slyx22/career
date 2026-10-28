import { ImageResponse } from "next/og";
import { CertificateVerification } from "@/lib/types";
import { formatCertDate, fullName } from "@/lib/certificate";
import { SITE_NAME } from "@/lib/site";
import { bandFor } from "@/lib/bands";

const INK = "#141A2E";
const BRASS = "#B8801F";
const BRASS_DARK = "#8F6317";
const PAPER = "#FBF8F1";
const SLATE = "#5B6472";

export type ImageShape = "wide" | "square";

export const IMAGE_SIZES: Record<ImageShape, { width: number; height: number }> = {
  // Link previews (LinkedIn, WhatsApp, Facebook, X).
  wide: { width: 1200, height: 630 },
  // Posts and WhatsApp/Instagram status.
  square: { width: 1080, height: 1080 },
};

function Check({ size = 22 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" style={{ marginRight: 8 }}>
      <circle cx="12" cy="12" r="12" fill={BRASS} />
      <path d="M6.5 12.5l3.5 3.5 7.5-8" fill="none" stroke="#FFFFFF" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function ScoreRing({ score, size }: { score: number; size: number }) {
  const stroke = Math.round(size * 0.08);
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const filled = (Math.max(0, Math.min(100, score)) / 100) * c;
  return (
    <div style={{ position: "relative", width: size, height: size, display: "flex" }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="#E8DFC9" strokeWidth={stroke} />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke={BRASS}
          strokeWidth={stroke}
          strokeDasharray={`${filled} ${c}`}
          strokeLinecap="round"
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
        />
      </svg>
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <div style={{ display: "flex", fontSize: size * 0.32, fontWeight: 700, color: INK, lineHeight: 1 }}>{score}</div>
        <div style={{ display: "flex", fontSize: size * 0.1, color: SLATE, marginTop: size * 0.03 }}>out of 100</div>
      </div>
    </div>
  );
}

export function renderCertificateImage(cert: CertificateVerification, shape: ImageShape = "wide") {
  const { width, height } = IMAGE_SIZES[shape];
  const square = shape === "square";
  const name = fullName(cert);
  const career = cert.career ?? "";
  const nameSize = name.length > 26 ? (square ? 56 : 52) : square ? 72 : 64;
  const careerSize = career.length > 40 ? (square ? 30 : 28) : square ? 38 : 34;

  return new ImageResponse(
    (
      <div
        style={{
          width,
          height,
          display: "flex",
          background: PAPER,
          padding: square ? 44 : 32,
          fontFamily: "sans-serif",
        }}
      >
        <div
          style={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            border: `6px solid ${BRASS}`,
            padding: square ? 56 : 40,
            justifyContent: "space-between",
          }}
        >
          <div
            style={{
              display: "flex",
              flexDirection: square ? "column" : "row",
              alignItems: square ? "center" : "flex-start",
              justifyContent: "space-between",
            }}
          >
            <div style={{ display: "flex", flexDirection: "column", alignItems: square ? "center" : "flex-start" }}>
              <div style={{ display: "flex", fontSize: 22, letterSpacing: 6, color: BRASS_DARK }}>
                CERTIFICATE OF CAREER READINESS
              </div>
              <div style={{ display: "flex", width: 120, height: 3, background: BRASS, marginTop: 14 }} />
            </div>
            {!square && <div style={{ display: "flex", fontSize: 20, color: SLATE }}>{SITE_NAME}</div>}
          </div>

          <div
            style={{
              display: "flex",
              flexDirection: square ? "column" : "row",
              alignItems: "center",
              justifyContent: "space-between",
              gap: square ? 40 : 32,
            }}
          >
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: square ? "center" : "flex-start",
                textAlign: square ? "center" : "left",
                maxWidth: square ? 900 : 760,
              }}
            >
              <div style={{ display: "flex", fontSize: nameSize, fontWeight: 700, color: INK, lineHeight: 1.1 }}>{name}</div>
              <div style={{ display: "flex", fontSize: careerSize, color: BRASS_DARK, marginTop: 18, lineHeight: 1.25 }}>
                {career}
              </div>
              {bandFor(cert.score).seal && (
                <div
                  style={{
                    display: "flex",
                    marginTop: 22,
                    padding: "10px 22px",
                    borderRadius: 999,
                    background: BRASS,
                    color: "#FFFFFF",
                    fontSize: square ? 28 : 24,
                  }}
                >
                  {bandFor(cert.score).label} · 70+
                </div>
              )}
            </div>
            <ScoreRing score={cert.score ?? 0} size={square ? 300 : 250} />
          </div>

          <div
            style={{
              display: "flex",
              flexDirection: square ? "column" : "row",
              alignItems: square ? "center" : "flex-end",
              justifyContent: "space-between",
              gap: 10,
              fontSize: 22,
              color: SLATE,
            }}
          >
            <div style={{ display: "flex", flexDirection: "column", alignItems: square ? "center" : "flex-start" }}>
              <div style={{ display: "flex", alignItems: "center", color: INK }}>
                <Check />
                {cert.expired ? "Genuine certificate (validity ended)" : "Verified certificate"}
              </div>
              <div style={{ display: "flex", marginTop: 6 }}>
                Issued {formatCertDate(cert.issued_at)} · ID {cert.certificate_id}
              </div>
            </div>
            <div style={{ display: "flex", color: INK }}>
              {square ? `${SITE_NAME} · ` : "Check it: "}srmaps.co.za/verify/{cert.certificate_id}
            </div>
          </div>
        </div>
      </div>
    ),
    { width, height }
  );
}

/** Shown when a certificate ID doesn't exist, so a broken link still previews cleanly. */
export function renderNotFoundImage() {
  const { width, height } = IMAGE_SIZES.wide;
  return new ImageResponse(
    (
      <div
        style={{
          width,
          height,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: PAPER,
          color: INK,
          fontSize: 48,
          fontFamily: "sans-serif",
        }}
      >
        {SITE_NAME}: certificate not found
      </div>
    ),
    { width, height }
  );
}
