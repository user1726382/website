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
1. **Legal operator:** exact legal name, legal form, serviceable address, trading name registration, authorised representative, applicable company/CRO/VAT details. Update English and German imprint and privacy documents.
2. **Recruitment licensing:** confirm Irish Employment Agency Act licensing applicability, obtain any required authorisation before operating a regulated employment agency. WRC guidance: https://workplacerelations.ie/en/what_you_should_know/employer-obligations/employment-agencies/ and https://www.workplacerelations.ie/en/what_you_should_know/employer-obligations/employment-agencies/faq/employment-agencies-faq.html
3. **Candidate privacy:** identify controller, lawful bases, sources, retention, suppliers, security, recipients, rights, contact, transfers and supervisory authority before requesting/processing CVs. Complete Article 13/14 information.
4. **Commercial engagement terms:** verify contracting entity, pricing, scope and any recruitment guarantees before publishing promises.
5. **Email and domain:** current contact uses leoedwlashe@gmail.com; configure professional domain and email (SPF/DKIM/DMARC) when available.
6. **Employer enquiry form:** currently uses mailto: and opens the user's email application. No automatic submission, server validation, spam protection or secure storage is claimed. Implement a compliant hosted form only after provider selection and privacy review.
7. **Vacancies:** all 23 entries in roles/roles.json have status career-profile. Publish JobPosting markup and Apply Now only for verified active vacancies with employer authorisation.
8. **Analytics:** no analytics added pending provider and privacy/consent review.
9. **Testing:** independently test iOS Safari, Android Chrome, desktop Chrome/Firefox, keyboard accessibility, all links and email/telephone actions. GitHub connector cannot run a graphical browser.
10. **Search Console:** verify domain ownership and submit sitemap after legal operator details are completed.

## Sources
- Irish WRC employment agency guidance (links above).
- Irish Revenue first-job guide: https://www.revenue.ie/en/jobs-and-pensions/starting-your-first-job/index.aspx
- Residential Tenancies Board: https://rtb.ie/renting/
- Irish DPC: https://www.dataprotection.ie/
