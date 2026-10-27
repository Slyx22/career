import { CONTACT_EMAIL } from "@/lib/site";

export function ContactEmail() {
  if (!CONTACT_EMAIL) {
    return <span>our contact email (being set up; please check back soon)</span>;
  }
  return (
    <a href={`mailto:${CONTACT_EMAIL}`} className="underline hover:text-ink">
      {CONTACT_EMAIL}
    </a>
  );
}
