# Bridgefield Advisory — Germany × Ireland

An original, bilingual B2B consulting website for recruitment, market entry and outsourced marketing. **Bridgefield Advisory is a provisional working brand; check naming/trademark availability before launch.** The site is an application project, not a deployed public website.

![Homepage design](preview/desktop.png)

## Included

- **Public website:** English and German homepages; recruitment, market-entry and marketing; integrated growth solutions; Germany and Ireland landing pages; employers, candidates and jobs; About, approach, case-studies placeholder, FAQ, Insights, contact, and legal-template pages. Paths and labels are localized.
- **Recruitment:** Database-backed job administration; published-only job listing; filtering by title, country and employment type; candidate applications with private CV upload.
- **Lead management:** General and employer inquiry forms, secure database persistence and optional SMTP notifications; protected review dashboard and status updates.
- **Editorial CMS:** Admin interface to edit homepage headings, page text, structured service capabilities, deliverables, FAQs, SEO titles/descriptions, legal content, blogs, bilingual vacancies and contact/booking settings.
- **Security:** Signed session cookies, Argon2 password hashes, configurable staff roles, CSRF verification, server-side validation, honeypot, per-process throttling, private CV files, MIME/signature validation, optional ClamAV scanner (required by default when enabled), no analytics scripts, security headers, audit event table and deletion/retention workflows.
- **SEO & accessibility:** Localized routes, canonical URLs, hreflang equivalents, sitemap, robots.txt, semantic headings, keyboard-accessible navigation, visible focus, reduced motion, responsive pages.

The public site is usable without third-party accounts. Forms are **deliberately disabled by default** until privacy and operational setup are completed. There are no fictional live jobs, clients, testimonials or unverified business credentials.

## Technology

This implementation uses **FastAPI + Jinja2 + modern CSS + minimal vanilla JavaScript + SQLite** rather than the prompt's preferred Next.js. That choice makes the complete project runnable and testable offline with the available environment. It avoids a frontend build chain and third-party JS dependencies. The architecture is intended for a **single-instance** deployment, such as one VPS. It is **not yet a multi-instance/serverless SaaS backend**; migrating the storage layer to PostgreSQL and using distributed rate limiting would be required for that topology.

## Local quick start

Requires Python 3.11+.

```bash
cd bridgefield-website
python -m venv .venv
source .venv/bin/activate # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python scripts/generate_secrets.py
# Copy the generated SESSION_SECRET and ADMIN_PASSWORD_HASH into .env
uvicorn app:app --reload
```

Open **http://127.0.0.1:8000/en/** or `/de/`. The administrator is at **http://127.0.0.1:8000/admin/login**. The default admin username is `admin`; the password is whichever you generated. The login remains disabled when secrets are not configured. Do not publish a site using `COOKIE_SECURE=false` on the public internet.

## Manage the website

The `/admin` application supports:

| Area | Available actions |
|---|---|
| Page copy | Edit English & German homepage, service, market, solution and legal texts; features, FAQs, deliverables and metadata |
| Articles | Publish/unpublish and edit bilingual insights; select approved cover imagery |
| Media | Upload approved JPEG/PNG/WebP images, which are resized/re-encoded and stored separately; delete unused images |
| Jobs | Add real bilingual vacancies, edit, publish, close or mark draft |
| Inquiries | Review, change status, permanently delete |
| Applications | Review, change status, download protected CV, permanently delete and remove stored CV |
| Settings | Set company name, wordmark, email, phone, social link and booking URL |
| Dashboard | Aggregate counts (by role) and admin audit activity (admin only) |

### Additional team accounts

```bash
python scripts/manage_user.py create alice --role recruitment
python scripts/manage_user.py create bob --role marketing
python scripts/manage_user.py create carol --role content
python scripts/manage_user.py disable alice
```

Staff roles:

- `admin`: all protected resources and settings.
- `recruitment`: jobs, applications, protected CVs.
- `marketing`: page copy, articles, B2B inquiries.
- `content`: page copy and articles only.

The environment-backed admin (`ADMIN_USER`, `ADMIN_PASSWORD_HASH`) is always a fallback administrator; protect this secret and remove access when no longer needed. For multiple staff, use unique accounts. MFA/SSO would be advisable for a higher-risk production recruitment environment; it is **not built in**.

## Enabling live forms

**Do not enable forms until all launch prerequisites below have been completed.**

In `.env`:

```ini
ACCEPT_INQUIRIES=true
ACCEPT_APPLICATIONS=true
CV_SCAN_MODE=clamscan
SMTP_HOST=smtp.example.org
SMTP_PORT=587
SMTP_USERNAME=...
SMTP_PASSWORD=...
SMTP_FROM=notifications@your-domain.com
NOTIFICATION_TO=team@your-domain.com
```

Inquiries are stored in SQLite even if email notification fails. Candidate application files are capped at 5 MiB and must be PDF or DOCX. Files are stored under a non-public directory, random filename and filesystem permissions 0600. By default, accepting an application **requires a working ClamAV `clamscan` command** and current virus definitions. If scanning fails or is unavailable, the application is rejected and the file is removed.

`CV_SCAN_MODE=off` exists **only for isolated local testing** (not appropriate for public production hosting). For higher scale, consider an asynchronous malware-scanning quarantine pipeline.

Also validate your privacy notice, candidate information notice, retention requirements, processor agreements, hosting location and access-control practices before enabling candidate uploads.

## Retention and deletion

In the admin dashboard, authorized staff can permanently delete an individual inquiry or application (including its CV) following an explicit confirmation. Administrative deletion leaves an event in the audit table without the deleted person's details.

A housekeeping script is provided; its periods are **examples**, not legal determinations:

```bash
python scripts/retention.py --applications-days 180 --inquiries-days 365
python scripts/retention.py --applications-days 180 --inquiries-days 365 --apply
```

Schedule it regularly only after deciding the appropriate retention periods. Plan for backups and log retention, including data subject erasure handling.

## Deployment

Docker and Caddy example files are included. For production, complete the launch checklist and then:

1. Set `SITE_DOMAIN=https://your-domain.example` and `SITE_HOST=your-domain.example` in `.env`.
2. Set a cryptographically random `SESSION_SECRET` and Argon2 admin hash; set `COOKIE_SECURE=true`.
3. Make the `data/`, `private_uploads/` and `media_uploads/` host directories writable by container UID `10001`, e.g. `sudo chown -R 10001:10001 data private_uploads media_uploads`.
4. Ensure the domain points to your server, and TCP 80/443 are open.
5. Review the ClamAV definitions/update strategy. The image attempts to fetch definitions on build, but virus signature update and verification need to be maintained operationally.
6. Run `docker compose --profile production up --build -d`.
7. Confirm TLS, CSP, backups, server firewall, form handling and access control.

For local Docker testing, `docker compose up --build` serves HTTP on `127.0.0.1:8000`. The `caddy` service is only started with the production profile.

### Production deployment cautions

- SQLite and in-memory throttling are suitable for one web worker/instance. **Do not run multiple workers sharing this setup** without review. Prefer PostgreSQL and Redis for multiple instances.
- Local files and SQLite require encrypted, tested backups; backup both data and uploaded CV files, and document deletion from backups.
- The web process should be behind an HTTPS reverse proxy. Configure trusted proxy headers/host validation for your infrastructure.
- Do not enable recruitment uploads before antivirus definitions are updated and verified. `clamscan` runs synchronously and may need optimization at scale.
- Configure SMTP delivery and monitor error logs without logging personal data.
- Undertake a professional security and GDPR/legal review before accepting live submissions.

## SEO and content details

The default domain is `https://example.com` until configured. Ensure actual domain, brand, legal entity and approved copy are set before indexation. Articles shipped with the sample project are original, general practice-oriented content rather than research on current market conditions; review them before publication. There are no invented job listings or case studies.

### Core pages

- `/en/` and `/de/`
- `/en/services/recruitment` → `/de/leistungen/personalvermittlung`
- `/en/services/market-entry` → `/de/leistungen/markteintritt`
- `/en/services/marketing` → `/de/leistungen/marketing-as-a-service`
- `/en/solutions/expand-to-germany` → `/de/loesungen/expansion-nach-deutschland`
- `/en/solutions/expand-to-ireland` → `/de/loesungen/expansion-nach-irland`
- `/en/contact` → `/de/kontakt`
- `/en/jobs` → `/de/stellenangebote`
- `/en/insights` → `/de/einblicke`

## Go-live checklist (essential)

- [ ] Confirm real registered company name, legal form, governing jurisdiction, registration numbers, business address, representatives and contact details.
- [ ] Check proposed *Bridgefield Advisory* brand and domain for trademark/name conflicts.
- [ ] Confirm which services the company can actually deliver and whether any activities need licences or special disclosures; keep regulated advice out of scope unless appropriately authorized.
- [ ] Replace and legally review the **Impressum/Legal Notice**, privacy notice, terms, candidate privacy notice and retention schedule in both languages. These ship as clearly marked **unapproved templates**.
- [ ] Verify recruitment processes and applicable German/Irish recruitment, employment and anti-discrimination obligations.
- [ ] Decide data-controller/processor roles, secure CV access policy, candidate sharing process, cross-border transfers, DSAR/erasure process and vendor contracts.
- [ ] Set up ClamAV, malware definition updates and file security monitoring; confirm that the scanner fails closed.
- [ ] Configure domain, TLS, secret management, backups, recovery, logging, SMTP and anti-spam.
- [ ] Test every form with real delivery checks, establish inquiry ownership and expected response times.
- [ ] Set approved branding, team biographies, photos and any actual partner/customer references; no fictional claims.
- [ ] Review articles and market information for factual accuracy and publish approved job adverts only.
- [ ] Test screen-reader and keyboard accessibility; conduct a formal WCAG audit if required.
- [ ] Re-test page speed and Core Web Vitals on actual hosting. Lighthouse targets have **not** been independently certified.
- [ ] Consider MFA/SSO, data encryption at rest, external penetration testing, separate candidate privacy notice and managed database before operating at volume.

## Verification

Run:

```bash
pytest -q
```

The included tests cover both languages and all public routes, sessions, CSRF, inquiries, CV upload validation and storage, admin authorization, job publishing, content editing, deletion and staged form disabling.

## Files

- `app.py` — routes, security, forms, sessions and admin operations
- `content.py` — bilingual default copy, service offerings, sitemap route definitions
- `database.py` — schema and persistence
- `templates/` — public and admin page templates
- `static/css/` — responsive design system
- `static/js/` — navigation, filters, cookie choices
- `static/img/` — original graphic assets
- `media_uploads/` — uploaded public-safe, re-encoded CMS images
- `scripts/` — admin account setup, secret generation, retention cleanup
- `tests/` — automatic integration checks
- `Dockerfile`, `compose.yaml`, `Caddyfile` — deployment starting point

## Not included / requires separate production work

- Domain registration, managed hosting, SMTP or booking accounts, confirmed legal copy and real business identity.
- Live CRM (HubSpot/Pipedrive/Zoho) or ATS integration; leads are managed via the included private admin database.
- Legal review or certified GDPR compliance.
- SSO/MFA, external penetration testing, disaster recovery service or a full external WAF.
- AI candidate ranking (deliberately not provided).
- Client portal and automated email marketing (future-ready concepts, not implemented).

Do not describe those future features or optional integrations as live before they have been connected and tested.

### Structured data

Service, organization, article and qualifying job structured data are behind `PUBLISH_STRUCTURED_DATA=false` until company claims, domain, vacancies and publisher details are verified. Once those details have been confirmed, set it to `true` and inspect the generated JSON-LD. JobPosting structured data is emitted only when an approved vacancy has a verified employer name.

The HTML preview screenshots are stored in `preview/desktop.png` and `preview/mobile.png`.
