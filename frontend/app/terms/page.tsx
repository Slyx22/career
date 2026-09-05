import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";

export const metadata = { title: "Terms of Service - Career Readiness Analyzer" };

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-paper">
      <Header />
      <main className="mx-auto max-w-2xl px-6 py-16 font-body text-sm leading-relaxed text-ink">
        <h1 className="font-display text-3xl text-ink">Terms of Service</h1>
        <p className="mt-2 text-xs text-slate">Last updated: [insert date before publishing]</p>

        <div className="mt-6 rounded border border-brass bg-brass/10 px-4 py-3 text-sm text-brass-dark">
          <strong>This is a drafted template, not legal advice.</strong> It was
          written to reflect what this specific application actually does,
          but it has not been reviewed by a lawyer. Have a qualified lawyer
          - ideally one familiar with South Africa&apos;s POPIA and any other
          jurisdictions your users are in - review and customize this
          before relying on it for a real, live product. Replace every
          [bracketed placeholder] below with your real details.
        </div>

        <h2 className="mt-8 font-display text-xl text-ink">1. What this service is</h2>
        <p className="mt-2">
          Career Readiness Analyzer (&quot;the Service&quot;, &quot;we&quot;, &quot;us&quot;) lets you
          upload a CV, select a target career, and receive an automated
          Career Readiness Score, a skill breakdown, and recommendations.
          You can also generate a Career Readiness Certificate reflecting
          that assessment. The Service is provided free of charge.
        </p>

        <h2 className="mt-8 font-display text-xl text-ink">2. Not professional certification or career advice</h2>
        <p className="mt-2">
          The Career Readiness Score and Certificate reflect an automated
          comparison between the skills evidenced in your CV and a skill
          model for your selected career. They are <strong>not</strong> a
          professional accreditation, qualification, or certification, and
          do not guarantee employment, interviews, or any career outcome.
          Some of the skill-importance data behind the score is drawn from
          O*NET (a U.S. Department of Labor database) and some is an
          internal estimate - see the results page for which is which. Do
          not treat the score as definitive career guidance; use it as one
          input among others.
        </p>

        <h2 className="mt-8 font-display text-xl text-ink">3. Your account</h2>
        <p className="mt-2">
          Running an analysis does not require an account. Generating a
          Career Readiness Certificate does require a free account,
          created via our authentication provider, Clerk. You&apos;re
          responsible for the accuracy of the name/surname you enter (it
          appears on your certificate) and for keeping your account
          credentials secure.
        </p>

        <h2 className="mt-8 font-display text-xl text-ink">4. Certificate verification is public by design</h2>
        <p className="mt-2">
          Every certificate gets a unique ID and a public verification
          page at <code>/verify/[certificate-id]</code>. Anyone who has (or
          guesses) that ID can see the name, career, score, and issue date
          associated with it. This is intentional, so third parties can
          verify a certificate you choose to share - do not generate or
          share a certificate if you don&apos;t want that information to be
          checkable by anyone with the link. We do not display your CV
          content or any other private information on the verification
          page.
        </p>

        <h2 className="mt-8 font-display text-xl text-ink">5. Acceptable use</h2>
        <p className="mt-2">You agree not to:</p>
        <ul className="mt-2 list-disc pl-5">
          <li>Upload a CV or enter a name that isn&apos;t yours, or misrepresent your identity.</li>
          <li>Attempt to disrupt, overload, or reverse-engineer the Service.</li>
          <li>Use the Service to generate certificates for the purpose of deceiving a third party (e.g. an employer) about your actual skills.</li>
          <li>Upload malicious files or content that infringes someone else&apos;s rights.</li>
        </ul>

        <h2 className="mt-8 font-display text-xl text-ink">6. No warranty; limitation of liability</h2>
        <p className="mt-2">
          The Service is provided &quot;as is&quot;, free of charge, without
          warranties of any kind. To the maximum extent permitted by
          applicable law, [Company Name] is not liable for any indirect,
          incidental, or consequential damages arising from your use of
          the Service, including decisions made based on your Career
          Readiness Score or Certificate.
        </p>

        <h2 className="mt-8 font-display text-xl text-ink">7. Changes to the Service or these Terms</h2>
        <p className="mt-2">
          We may update these Terms or change, suspend, or discontinue the
          Service at any time. Continued use after an update means you
          accept the revised Terms.
        </p>

        <h2 className="mt-8 font-display text-xl text-ink">8. Contact</h2>
        <p className="mt-2">
          Questions about these Terms: [insert contact email].
        </p>

        <p className="mt-8 text-xs text-slate">
          See also our <a href="/privacy" className="underline hover:text-ink">Privacy Policy</a>.
        </p>
      </main>
      <Footer />
    </div>
  );
}
