import Link from "next/link";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { ContactEmail } from "@/components/ContactEmail";
import { LEGAL_LAST_UPDATED, MINIMUM_AGE, SITE_NAME, SITE_URL } from "@/lib/site";

export const metadata = { title: `Privacy Policy - ${SITE_NAME}` };

const h2 = "mt-9 font-display text-xl font-semibold tracking-tight";

export default function PrivacyPage() {
  return (
    <div className="min-h-screen">
      <Header />
      <main className="page-top mx-auto max-w-3xl px-4 sm:px-6">
        <article className="glass-sheet p-6 text-[15px] leading-relaxed sm:p-10">
        <h1 className="font-display text-3xl font-semibold tracking-tight sm:text-4xl">Privacy Policy</h1>
        <p className="mt-2 text-sm text-slate">Last updated: {LEGAL_LAST_UPDATED}</p>

        <p className="mt-6">
          This policy explains what personal information {SITE_NAME} (&quot;we&quot;,
          &quot;us&quot;), available at {SITE_URL}, collects when you use the
          service, why, and what rights you have. We are based in South
          Africa and handle personal information in line with the
          Protection of Personal Information Act, 2013 (POPIA).
        </p>

        <h2 className={h2}>1. Who is responsible for your information</h2>
        <p className="mt-2">
          {SITE_NAME} is an independent, early-stage service run in South
          Africa. For any privacy question or request, including reaching
          our Information Officer, email <ContactEmail />.
        </p>

        <h2 className={h2}>2. What we collect</h2>
        <ul className="mt-2 list-disc space-y-1 pl-5">
          <li>
            <strong>Your name and surname</strong>, as you type them into the
            analysis form. We use what you type, not the name in your CV.
          </li>
          <li>
            <strong>Your CV</strong> (PDF or DOCX). We read the text to work
            out which skills it shows. See section 5 for what happens to the
            file.
          </li>
          <li>
            <strong>The career you choose</strong> (a South African job title or
            an international one) and your <strong>results</strong>: your score,
            which skills were found or missing, recommended next steps, and
            whether your CV mentions registrations or licences usually required
            in South Africa for that job (for example SANC or a trade test). We
            keep these results, not the wording of your CV.
          </li>
          <li>
            <strong>Account details</strong> (such as your email address), only
            if you create a free account to get a certificate. Accounts are run
            by our sign-in provider, Clerk.
          </li>
          <li>
            <strong>Certificate details</strong>: name, career, score, issue and
            expiry dates and certificate ID, if you create a certificate.
          </li>
          <li>
            <strong>Feedback you choose to give</strong>, such as which future
            features interest you.
          </li>
          <li>
            <strong>Basic technical data</strong> our hosting providers record
            automatically, such as IP address and browser type in server logs,
            used to keep the service running and secure.
          </li>
        </ul>
        <p className="mt-2">
          Please leave out of your CV anything you don&apos;t need to share
          for a job application, such as your ID number, health information,
          religion, or race. We don&apos;t need it, and we don&apos;t use it.
        </p>

        <h2 className={h2}>3. Why we use it</h2>
        <ul className="mt-2 list-disc space-y-1 pl-5">
          <li>To score your CV against the career you chose and show your results.</li>
          <li>To create your certificate and let others check it is genuine.</li>
          <li>To keep your account working, if you have one.</li>
          <li>To fix problems, prevent misuse, and improve the service using overall, non-identifying statistics.</li>
        </ul>
        <p className="mt-2">
          We rely on your consent, which you give when you tick the box before
          uploading your CV, and on our legitimate interest in running a
          secure service. You can withdraw consent at any time (section 8);
          this doesn&apos;t affect processing that already happened.
        </p>

        <h2 className={h2}>4. What we never do</h2>
        <ul className="mt-2 list-disc space-y-1 pl-5">
          <li>We do not sell your personal information.</li>
          <li>We do not show ads or share your information with advertisers.</li>
          <li>We do not share your CV or results with employers or recruiters.</li>
          <li>
            We do not use your CV to train AI models. Your score comes from a
            fixed scoring method, and no AI provider receives your CV.
          </li>
        </ul>
        <p className="mt-2">
          If we ever offer a way to share your profile with employers, it will
          be a separate, optional feature that is off unless you switch it on.
        </p>

        <h2 className={h2}>5. Your CV file</h2>
        <p className="mt-2">
          Your CV is read in memory to extract its text and is not saved to our
          database or kept as a file after your analysis finishes. We keep the
          results of the analysis (section 2), not the CV itself.
        </p>

        <h2 className={h2}>6. What is public</h2>
        <p className="mt-2">
          If you create a certificate, anyone with its verification link or ID
          can see your name, the career, your score, the issue and expiry
          dates, and the certificate ID. The same details appear in the
          certificate PDF, the downloadable certificate images and the preview
          picture shown when the link is shared. That is how an employer checks
          a certificate is real. Your CV, email address and detailed results
          are never shown. We ask search engines not to list certificate pages,
          so they are found through the link you share, not by searching your
          name. Only create and share a certificate if you are comfortable with
          this.
        </p>
        <p className="mt-2">
          <strong>Sharing is your choice.</strong> If you use the share buttons
          (LinkedIn, WhatsApp, Facebook, X) or download and post an image, you
          are sharing through that platform, under its own terms and privacy
          policy. Once you share, others can save or reshare it; we can&apos;t
          undo that, but we can withdraw the certificate so the link no longer
          verifies.
        </p>

        <h2 className={h2}>7. Who processes data for us</h2>
        <p className="mt-2">
          We use these service providers (&quot;operators&quot; under POPIA) to run
          the service. They process information only to provide their service
          to us:
        </p>
        <ul className="mt-2 list-disc space-y-1 pl-5">
          <li><strong>Vercel</strong>: hosts the website.</li>
          <li><strong>Render</strong>: runs the analysis engine that reads your CV (United States).</li>
          <li><strong>Supabase</strong>: our database, which stores analysis results, certificates and feedback (Ireland, EU).</li>
          <li><strong>Clerk</strong>: sign-in and accounts.</li>
        </ul>
        <p className="mt-2">
          These providers store or process data outside South Africa (in the
          United States and the European Union). We use providers bound by
          data-protection laws or agreements that give protection comparable to
          POPIA, and by using the service you agree to this transfer.
        </p>

        <h2 className={h2}>8. How long we keep it, and your rights</h2>
        <p className="mt-2">
          We delete data automatically on this schedule, unless you ask us to
          delete it sooner:
        </p>
        <ul className="mt-2 list-disc space-y-1 pl-5">
          <li>Your CV file: never stored (see section 5).</li>
          <li>Analysis results without a certificate: deleted 12 months after the analysis.</li>
          <li>
            Certificates and the analysis behind them: kept while the
            certificate is valid (12 months) so it can be verified, then
            deleted 24 months after it expires.
          </li>
          <li>Feedback about future features: deleted after 24 months.</li>
          <li>Account details: kept until you delete your account with our sign-in provider.</li>
        </ul>
        <p className="mt-2">
          Hosting providers may keep server logs and backups for a short time
          under their own policies.
        </p>
        <p className="mt-2">Under POPIA you have the right to:</p>
        <ul className="mt-2 list-disc space-y-1 pl-5">
          <li>ask what personal information we hold about you;</li>
          <li>ask us to correct or delete it, including withdrawing a certificate;</li>
          <li>object to our processing of it;</li>
          <li>withdraw your consent; and</li>
          <li>
            complain to the Information Regulator (South Africa) at{" "}
            <a
              href="https://inforegulator.org.za"
              className="underline hover:text-ink"
              rel="noopener noreferrer"
              target="_blank"
            >
              inforegulator.org.za
            </a>
            .
          </li>
        </ul>
        <p className="mt-2">
          To make a request, email <ContactEmail /> and include your certificate
          ID or analysis link if you have one. We may ask you to confirm it is
          you, and we aim to reply within 30 days.
        </p>

        <h2 className={h2}>9. Security</h2>
        <p className="mt-2">
          We use encrypted connections (HTTPS), keep access keys on the server
          only, and limit what the public verification page shows. No online
          service is completely secure. If a breach affects your personal
          information, we will tell you and the Information Regulator as POPIA
          requires.
        </p>

        <h2 className={h2}>10. Cookies</h2>
        <p className="mt-2">
          We use only cookies needed to run the site, such as keeping you
          signed in. We don&apos;t use advertising or tracking cookies.
        </p>

        <h2 className={h2}>11. Children</h2>
        <p className="mt-2">
          The service is meant for people aged {MINIMUM_AGE} and over. If you
          are under {MINIMUM_AGE}, you may only use it with the permission of
          a parent or guardian, who must agree to this policy for you.
        </p>

        <h2 className={h2}>12. Changes</h2>
        <p className="mt-2">
          We may update this policy. We will change the date at the top, and
          for important changes we will show a notice on the site.
        </p>

        <p className="mt-8 text-xs text-ink">
          See also our{" "}
          <Link href="/terms" className="underline hover:text-ink">
            Terms of Service
          </Link>
          .
        </p>
        </article>
      </main>
      <Footer />
    </div>
  );
}
