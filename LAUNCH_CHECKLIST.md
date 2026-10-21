# The Link — production verification and outstanding owner decisions

Updated 21 October 2026. This document is for internal project management, not a legal certification.

## Implemented
- Employer-first bilingual homepage, direct phone and email CTAs.
- English and German employer, consulting, about, insights and contact pages.
- Bilingual relocation guidance and salary explorer with 23 role categories.
- Email-client-based employer hiring brief. No server-side form submission or database exists.
- Static CSS/JS; no third-party analytics, tracking pixels, chatbots or applicant ranking added.
- Robots and sitemap for public marketing pages; legal pages remain noindex until completed.
- Career profiles are not employer-authorised vacancies. Enquiries must not imply an application to a specific employer.

## Critical owner inputs / prerequisites
1. **Legal operator:** Confirmed: The Link Consulting GbR, Frankfurt am Main, Germany; partners Leo Walshe and Josephine Douglas. **Outstanding:** full street address and postcode, representation arrangements under GbR agreement, whether registered as eGbR, Gewerbeanmeldung, and any applicable VAT / business identification. Update both imprints with verified details.
2. **Recruitment licensing:** confirm Irish Employment Agency Act licensing applicability, obtain any required authorisation before operating a regulated employment agency. WRC guidance: https://workplacerelations.ie/en/what_you_should_know/employer-obligations/employment-agencies/ and https://www.workplacerelations.ie/en/what_you_should_know/employer-obligations/employment-agencies/faq/employment-agencies-faq.html
3. **Candidate privacy:** controller identified as The Link Consulting GbR and privacy coordinator Leo Walshe. Complete the full address, lawful bases, sources, retention, suppliers, security, recipients, rights, contact, transfers and supervisory authority before requesting/processing CVs. Complete Article 13/14 information.
4. **Commercial engagement terms:** verify contracting entity, pricing, scope and any recruitment guarantees before publishing promises.
5. **Email and domain:** current contact uses leoedwalshe@gmail.com; configure professional domain and email (SPF/DKIM/DMARC) when available.
6. **Employer enquiry form:** currently uses mailto: and opens the user's email application. No automatic submission, server validation, spam protection or secure storage is claimed. Implement a compliant hosted form only after provider selection and privacy review.
7. **Vacancies:** all 23 entries in roles/roles.json have status career-profile. Publish JobPosting markup and Apply Now only for verified active vacancies with employer authorisation.
8. **Analytics:** no analytics added pending provider and privacy/consent review.
9. **Testing:** independently test iOS Safari, Android Chrome, desktop Chrome/Firefox, keyboard accessibility, all links and email/telephone actions. GitHub connector cannot run a graphical browser.
10. **Search Console:** verify domain ownership and submit sitemap after legal operator details are completed.

## Founder responsibility allocation (operational; not formal statutory appointments)
- **Leo Walshe:** primary partner contact; website and legal-notice coordination; privacy/GDPR coordinator (not statutory DPO); candidate data handling and rights-request coordination; recruitment compliance and Irish licence enquiry; information-security and breach-response coordinator; employer enquiry and commercial contracting contact.
- **Josephine Douglas:** partner and alternative founder contact; alternative escalation if a concern relates to Leo; supports continuity. A genuinely independent statutory DPO cannot be presumed from this allocation.
- **Statutory DPO:** not appointed or advertised. Document the GDPR Art. 37 / § 38 BDSG assessment, including number of people regularly handling automated personal data, large-scale monitoring or special-category processing, any DPIA-required activities, and **the independent § 38 BDSG trigger for commercial processing for the purpose of transmitting personal data (geschäftsmäßig zum Zweck der Übermittlung)**. Candidate introductions to employers make this a priority legal-interpretation question even with two founders. Do not infer exemption solely from headcount. If required, appoint a qualified, conflict-free external DPO and notify the authority where applicable.
- **Editorial responsibility:** assess whether § 18(2) MStV applies to the published articles. Leo is proposed as editorial contact; do not claim formal statutory appointment until eligibility and full serviceable address are confirmed.
- **Irish recruitment licensing:** WRC guidance says employment agencies generally require a licence. A Frankfurt-based cross-border model needs a scope determination before regulated placement activities. Do not claim a licence without proof.
- **Operational documents to complete:** record of processing activities (Art. 30), retention/deletion schedule, candidate privacy notice, privacy rights workflow, security and breach response (including 72-hour authority notification assessment), processor contracts and international transfer review, employer engagement terms, and candidate-to-employer sharing procedure.

## Sources
- Irish WRC employment agency guidance (links above).
- Irish Revenue first-job guide: https://www.revenue.ie/en/jobs-and-pensions/starting-your-first-job/index.aspx
- Residential Tenancies Board: https://rtb.ie/renting/
- Irish DPC: https://www.dataprotection.ie/
