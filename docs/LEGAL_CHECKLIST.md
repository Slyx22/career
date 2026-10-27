# Keep the Terms and Privacy Policy in step with the product

The Terms (`frontend/app/terms/page.tsx`) and Privacy Policy
(`frontend/app/privacy/page.tsx`) must describe what the app really does.
Whenever a change touches any item below, update the matching section in
the same pull request and bump `LEGAL_LAST_UPDATED` in `frontend/lib/site.ts`.

| If you change... | Update |
|---|---|
| What personal data is collected or stored (new form field, new table, new column) | Privacy §2 What we collect, §8 retention |
| Where data is stored or which service processes it (new provider, region) | Privacy §7 Who processes data for us |
| How long data is kept, or the nightly deletion job (`supabase/migrations/0007_retention.sql`) | Privacy §8 |
| What is public or shareable (certificate page, images, share buttons, previews) | Privacy §6, Terms §4 and §7 |
| How the score works, data sources, SA titles or the "Required in South Africa" checklist | Terms §2 (and method version in `certificate_service.py`) |
| Accounts, age limits, consent checkbox | Terms §3, Privacy §11, analyze form text |
| Anything shared with employers (e.g. the planned employer dashboard) | New opt-in consent, Privacy §4 "What we never do", Terms; get legal review first |
| Charging money | Terms (payments, refunds, Consumer Protection Act cooling-off), Privacy |

Before launching anything that shares people's data with employers or
takes payments, have the wording reviewed by a South African attorney
(a university law clinic can help for free).
