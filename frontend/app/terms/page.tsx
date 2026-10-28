import Link from "next/link";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { ContactEmail } from "@/components/ContactEmail";
import { LEGAL_LAST_UPDATED, MINIMUM_AGE, SITE_NAME, SITE_URL } from "@/lib/site";

export const metadata = { title: `Terms of Service - ${SITE_NAME}` };

const h2 = "mt-9 font-display text-xl font-semibold tracking-tight";

export default function TermsPage() {
  return (
    <div className="min-h-screen">
      <Header />
      <main className="page-top mx-auto max-w-3xl px-4 sm:px-6">
        <article className="glass-sheet p-6 text-[15px] leading-relaxed sm:p-10">
        <h1 className="font-display text-3xl font-semibold tracking-tight sm:text-4xl">Terms of Service</h1>
        <p className="mt-2 text-sm text-slate">Last updated: {LEGAL_LAST_UPDATED}</p>

        <p className="mt-6">
          These terms apply when you use {SITE_NAME} (&quot;the service&quot;,
          &quot;we&quot;, &quot;us&quot;) at {SITE_URL}. By using the service you agree
          to them and to our{" "}
          <Link href="/privacy" className="underline hover:text-ink">
            Privacy Policy
          </Link>
          . If you don&apos;t agree, please don&apos;t use the service.
        </p>

        <h2 className={h2}>1. What the service does</h2>
        <p className="mt-2">
          You upload a CV and choose a career. The service compares the skills
          your CV shows with the skills that matter for that career and gives
          you a Career Readiness Score out of 100, a skills breakdown and
          suggestions. You can also create a Career Readiness Certificate.
          The service is currently free.
        </p>

        <h2 className={h2}>2. What the score and certificate are, and are not</h2>
        <ul className="mt-2 list-disc space-y-1 pl-5">
          <li>
            The score is an automated estimate based only on the text of the CV
            you upload. It measures how well your CV matches a career&apos;s
            skills on that date.
          </li>
          <li>
            It is <strong>not</strong> a qualification, a SAQA-registered
            credential, a professional accreditation, a job offer, or a
            guarantee of interviews or employment.
          </li>
          <li>
            We do not check whether what your CV says is true, and we do not
            verify your identity. The name on a certificate is the name you
            typed in.
          </li>
          <li>
            Certificates are valid for 12 months from the issue date. After
            that, the verification page shows them as expired.
          </li>
          <li>
            Career skills data comes from the O*NET Database (see section 8),
            which describes occupations in the United States. Local job
            requirements in South Africa or elsewhere may differ.
          </li>
          <li>
            South African job titles come from the Organising Framework for
            Occupations (OFO 2021). Each one is linked to the closest
            international occupation, whose skills are used for the score. The
            link is our best match, not an official equivalence, and the results
            page shows which occupation was used.
          </li>
          <li>
            The &ldquo;Required in South Africa&rdquo; checklist and recommended
            next steps are general information to help you, not legal,
            professional or career advice. Registration and licensing rules can
            change and may not be complete; always confirm with the relevant
            council, authority or employer. The checklist only shows whether
            your CV mentions an item; it does not check that you hold it.
          </li>
          <li>
            Scores are grouped into bands: Excellent match (85+), Strong match
            (70&ndash;84), Developing (50&ndash;69) and Early stage (below 50).
            Certificates scoring 70 or more show a &ldquo;Strong match&rdquo; or
            &ldquo;Excellent match&rdquo; seal. A band or seal describes how well
            your CV matched the occupation&apos;s skills on that date. It is our
            assessment, not an endorsement by any employer, and it does not mean
            an employer has seen or approved your certificate.
          </li>
          <li>
            Scoring methods improve over time. A certificate records the score
            and method version on the date issued; a new analysis may give a
            different score.
          </li>
          <li>
            The score is not career, financial or legal advice. Use it as one
            input among others.
          </li>
        </ul>

        <h2 className={h2}>3. Who can use it</h2>
        <p className="mt-2">
          You must be {MINIMUM_AGE} or older, or have permission from a parent
          or guardian who accepts these terms for you. You don&apos;t need an
          account to get a score. You need a free account to create a
          certificate, and you must keep your sign-in details safe.
        </p>

        <h2 className={h2}>4. Your responsibilities</h2>
        <p className="mt-2">You agree not to:</p>
        <ul className="mt-2 list-disc space-y-1 pl-5">
          <li>upload someone else&apos;s CV without their permission;</li>
          <li>create a certificate in another person&apos;s name, or use a certificate to pretend to be someone else;</li>
          <li>change, edit or fake a certificate, its images or its verification page, or present it as a qualification;</li>
          <li>share a certificate that isn&apos;t yours, or describe a certificate in a way that suggests we endorse you or vouch for your skills or character;</li>
          <li>upload files containing viruses or harmful code, or try to break, overload or get unauthorised access to the service;</li>
          <li>use automated tools to scrape the service or collect other people&apos;s information; or</li>
          <li>use the service for anything unlawful.</li>
        </ul>
        <p className="mt-2">
          You are responsible for the content of the CV you upload, and you
          confirm you have the right to share it with us.
        </p>

        <h2 className={h2}>5. Withdrawing certificates and access</h2>
        <p className="mt-2">
          We may withdraw a certificate, or suspend access, if we reasonably
          believe these terms were broken (for example a certificate in
          someone else&apos;s name), or if a certificate was created because of
          an error in the service. A withdrawn certificate will no longer
          verify.
        </p>

        <h2 className={h2}>6. Your content</h2>
        <p className="mt-2">
          Your CV stays yours. You let us process it only to give you your
          results and certificate, as described in the Privacy Policy.
        </p>

        <h2 className={h2}>7. Our content</h2>
        <p className="mt-2">
          The website design, scoring method, text and certificate layout
          belong to us. You may share your own results and certificate, but
          you may not copy the service or reuse its content commercially
          without permission.
        </p>
        <p className="mt-2">
          <strong>Sharing.</strong> You may share your own certificate, its
          link and its images, unchanged, on social media, in job applications
          and on profiles such as LinkedIn. When you use a share button you
          leave our site and the other platform&apos;s terms apply. We are not
          responsible for those platforms or for what other people do with what
          you share.
        </p>

        <h2 className={h2}>8. O*NET data</h2>
        <p className="mt-2">
          This site uses information from the{" "}
          <a
            href="https://www.onetcenter.org/database.html"
            className="underline hover:text-ink"
            rel="noopener noreferrer"
            target="_blank"
          >
            O*NET Database
          </a>{" "}
          by the U.S. Department of Labor, Employment and Training
          Administration (USDOL/ETA), used under the{" "}
          <a
            href="https://creativecommons.org/licenses/by/4.0/"
            className="underline hover:text-ink"
            rel="noopener noreferrer"
            target="_blank"
          >
            CC BY 4.0 licence
          </a>
          . We have modified the data for use in this service. USDOL/ETA has
          not approved, endorsed, or tested these modifications. O*NET&reg; is
          a trademark of USDOL/ETA.
        </p>

        <h2 className={h2}>9. Availability</h2>
        <p className="mt-2">
          We try to keep the service running but can&apos;t promise it will
          always be available, fast or error-free. The analysis engine may take
          up to a minute to start after a quiet period. We may change, pause or
          stop the service, or parts of it, at any time.
        </p>

        <h2 className={h2}>10. Limitation of liability</h2>
        <p className="mt-2">
          The service is provided free and &quot;as is&quot;. To the extent the law
          allows, we are not liable for any loss arising from your use of the
          service or reliance on a score or certificate, including lost job
          opportunities, income or data. Nothing in these terms limits rights
          you have under the Consumer Protection Act, 2008, or any other law
          that cannot be excluded, or our liability for gross negligence.
        </p>

        <h2 className={h2}>11. Changes to these terms</h2>
        <p className="mt-2">
          We may update these terms. We will change the date at the top, and
          for important changes we will show a notice on the site. If you keep
          using the service after a change, the new terms apply.
        </p>

        <h2 className={h2}>12. Law and contact</h2>
        <p className="mt-2">
          These terms are governed by the laws of the Republic of South
          Africa. Questions or complaints: <ContactEmail />. We will try to
          resolve any issue with you informally first.
        </p>
        </article>
      </main>
      <Footer />
    </div>
  );
}
