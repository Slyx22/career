import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";

export const metadata = { title: "Privacy Policy - Career Readiness Analyzer" };

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-paper">
      <Header />
      <main className="mx-auto max-w-2xl px-6 py-16 font-body text-sm leading-relaxed text-slate-100">
        <h1 className="font-display text-3xl text-slate-100">Privacy Policy</h1>
        <p className="mt-2 text-xs text-slate-300">Last updated: [insert date before publishing]</p>

        <div className="mt-6 rounded border border-brass bg-brass/10 px-4 py-3 text-sm text-brass-dark">
          <strong>This is a drafted template, not legal advice.</strong> It
          describes what this application actually collects and does
          today, but it has not been reviewed by a lawyer, and it doesn&apos;t
          make specific compliance claims (e.g. &quot;we are POPIA/GDPR
          compliant&quot;) that only a proper legal review can responsibly
          make. Have a qualified lawyer review this - especially regarding
          South Africa&apos;s POPIA and any other jurisdiction your users are
          in - before relying on it for a real, live product. Replace
          every [bracketed placeholder] with your real details.
        </div>

        <h2 className="mt-8 font-display text-xl text-slate-100">1. What we collect</h2>
        <ul className="mt-2 list-disc pl-5">
          <li><strong>Name and surname</strong> you type into the analysis form (used as-is; we never take your name from your CV).</li>
          <li><strong>Your uploaded CV</strong> (PDF or DOCX) - processed to extract text for scoring.</li>
          <li><strong>Your selected target career.</strong></li>
          <li><strong>Account information</strong> (e.g. email address), only if you create a free account to generate a certificate - handled by our authentication provider, Clerk, not stored by us directly.</li>
          <li><strong>Certificate data</strong>: name, career, score, and issue date, if you generate a certificate. This is intentionally public via the certificate&apos;s verification link - see Section 4.</li>
        </ul>
        <p className="mt-2">
          We do not knowingly collect any special categories of personal
          information (e.g. health, biometric, or similarly sensitive
          data) - please don&apos;t include such information in your CV.
        </p>

        <h2 className="mt-8 font-display text-xl text-slate-100">2. Why we collect it</h2>
        <p className="mt-2">
          Solely to run the career readiness analysis you request, generate
          your results and (if requested) certificate, and let you or a
          third party verify a certificate you choose to share. We do not
          use your CV content for any purpose beyond generating your
          analysis.
        </p>

        <h2 className="mt-8 font-display text-xl text-slate-100">3. What we don&apos;t do</h2>
        <ul className="mt-2 list-disc pl-5">
          <li>We do not sell your personal information.</li>
          <li>We do not show ads, and we do not share your data with advertisers.</li>
          <li>We do not publish your CV content anywhere, including on the public certificate verification page.</li>
          <li>We do not use your CV to train any AI model - the readiness score is computed by a deterministic scoring algorithm we built, not an AI model, and no AI provider ever sees your CV as part of that scoring.</li>
        </ul>

        <h2 className="mt-8 font-display text-xl text-slate-100">4. What&apos;s public</h2>
        <p className="mt-2">
          If you generate a certificate, its ID, your name, your target
          career, your score, and the issue date become viewable by
          anyone who has (or guesses) the certificate&apos;s verification
          link. This is intentional - it&apos;s how a third party checks a
          certificate is genuine. Nothing else (your CV, your email, your
          full analysis breakdown) is made public.
        </p>

        <h2 className="mt-8 font-display text-xl text-slate-100">5. Who we share data with</h2>
        <p className="mt-2">The following third-party services process data on our behalf ("subprocessors"):</p>
        <ul className="mt-2 list-disc pl-5">
          <li><strong>Clerk</strong> - authentication, if you create an account.</li>
          <li><strong>[Supabase / database provider]</strong> - stores analysis and certificate records once the Service is fully deployed. [Fill in once you connect Supabase or an alternative.]</li>
          <li><strong>[Hosting providers, e.g. Netlify, your Python-hosting provider]</strong> - run the application itself.</li>
        </ul>
        <p className="mt-2">
          We don&apos;t share your data with anyone else, and we don&apos;t sell it.
        </p>

        <h2 className="mt-8 font-display text-xl text-slate-100">6. How long we keep data</h2>
        <p className="mt-2">
          [Fill in your real retention policy once decided - for example:
          uploaded CV files are processed in memory and not stored beyond
          what&apos;s needed to generate your immediate results; analysis and
          certificate records are retained for as long as your account
          exists, or for a fixed period like 12 months for anonymous
          analyses, after which they may be deleted.]
        </p>

        <h2 className="mt-8 font-display text-xl text-slate-100">7. Your rights</h2>
        <p className="mt-2">
          Depending on where you live, you may have rights to access,
          correct, or request deletion of your personal information (for
          example, under South Africa&apos;s Protection of Personal
          Information Act (POPIA), or similar laws elsewhere). To make a
          request, contact us at [insert contact email]. Note that
          deleting an already-issued certificate&apos;s underlying record may
          break its public verification link.
        </p>

        <h2 className="mt-8 font-display text-xl text-slate-100">8. Cookies</h2>
        <p className="mt-2">
          If you create an account, Clerk sets cookies needed to keep you
          signed in. We don&apos;t use advertising or tracking cookies.
        </p>

        <h2 className="mt-8 font-display text-xl text-slate-100">9. Children</h2>
        <p className="mt-2">
          The Service isn&apos;t directed at children, and we don&apos;t knowingly
          collect personal information from anyone under [insert your
          chosen age threshold, e.g. 16].
        </p>

        <h2 className="mt-8 font-display text-xl text-slate-100">10. Changes to this policy</h2>
        <p className="mt-2">
          We may update this Privacy Policy from time to time. Material
          changes will be reflected by updating the date at the top of
          this page.
        </p>

        <h2 className="mt-8 font-display text-xl text-slate-100">11. Contact</h2>
        <p className="mt-2">
          Questions or requests about your data: [insert contact email].
        </p>

        <p className="mt-8 text-xs text-slate-300">
          See also our <a href="/terms" className="underline hover:text-slate-100">Terms of Service</a>.
        </p>
      </main>
      <Footer />
    </div>
  );
}
