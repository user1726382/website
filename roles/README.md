# The Link — Roles

This section contains **23 bilingual German-speaking role categories**. The site presents professional career pages with **Apply Now** mailto actions. Do not claim a named employer has an active vacancy without written authorisation. Until an actual employer authorises a specific opening, keep `status: "career-profile"` and do not use `JobPosting` schema, employer claims, deadlines or claims of active hiring.

## Update a role

1. Edit **`roles/roles.json`**, the single source for titles, salary bands, descriptions, requirements, categories, email address and vacancy status.
2. Run `node scripts/build-roles.mjs && node scripts/build-roles-de.mjs` from the repository root (Node.js 18+). The scripts regenerate both English and German listings and every `roles/<slug>/index.html` and `roles/de/<slug>/index.html`. German translations are maintained in `roles/roles-de.json`.
3. Review the generated HTML and test the landing-page search, filters, mobile layout, role links, and email subjects.
4. Commit the JSON and generated pages together to the `gh-pages` branch.

`roles/styles.css` and `roles/roles-ui.js` are shared presentation/interaction assets. No database or recruitment SaaS is used.

## Candidate interest and privacy

The contact email is currently `leoedwalshe@gmail.com`, as configured on the homepage. A mailto link **cannot attach a CV automatically**; candidates must add an attachment themselves. Copy-email is offered if no mail client opens.

**Before publicly collecting candidate CVs, the business must complete and verify the operator identity, recruitment-specific GDPR transparency notices, legal basis, retention, candidate rights process, vendor/transfer arrangements and any applicable Irish employment agency licensing.** The existing legal pages still contain incomplete operator information. The site-wide `noindex,nofollow` settings remain unchanged. The static feature is not a legal-compliance certification.

## Confirmed vacancies

The **Apply Now** label opens a role-specific email to The Link, including for general role categories. Once an employer authorises a specific vacancy, set `status: "open"` and `authorised: true` and replace the generic company copy with accurate employer terms, benefits and dates. It does not automatically generate `JobPosting` structured data; only add that after all required details have been verified.

## Languages

The homepage's DE/EN switch points its Roles link to the matching language. Role pages use a DE/EN link to switch between matching English and German pages, preserving the selected role. Both languages use the same salaries, slugs, status and contact email from `roles/roles.json`; German descriptions, responsibilities and labels are in `roles/roles-de.json`.

## Salary methodology

See [`SALARY_METHODOLOGY.md`](SALARY_METHODOLOGY.md) for all 23 Irish base benchmarks, assumed language premiums, the additional 10% commercial uplift, and cited 2026 salary guides. The displayed salary bands are modelled market targets and are not employer-approved offers. German fluency premiums are assumptions, not empirically verified universal premiums.
