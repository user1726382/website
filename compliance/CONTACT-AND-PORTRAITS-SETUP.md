# Website contact and team-photo configuration
Last updated: 2026-10-20. Static site source: `gh-pages/index.html`.

## Temporary email
The current public contact CTA uses `mailto:leoedwlashe@gmail.com?subject=The%20Link%20enquiry`. It is an ordinary email link: no data is submitted or stored by the static website. This personal mailbox is **not** a verified business email and must be replaced once the company domain, email security and operator identity are established.

To change it, update the two `mailto:` URLs in `gh-pages/index.html` and the bilingual legal pages `legal/{en,de}/{contact,privacy,imprint}` (actual filenames differ by language). Verify the mailto link in both languages.

## Future contact form
Keep the static homepage email CTA until a dedicated backend/form provider is approved. The `main` branch contains a FastAPI `/forms/inquiry` endpoint and `ACCEPT_INQUIRIES` setting. It now additionally checks `LEGAL_IDENTITY_VERIFIED`, `PRIVACY_NOTICE_APPROVED` and `SECURITY_RELEASE_APPROVED`. These flags must only be set after **actual** approval evidence is documented; flags are not proof of compliance.

Before activating: restore missing backend templates/assets, choose approved hosting and provider DPAs, configure production HTTPS, CSRF and spam controls, enforce secure session cookies, publish actual GDPR notices, approve inquiry retention/deletion, set up SMTP/SPF/DKIM/DMARC, test delivery, rate limiting and rights requests, and replace the mailto CTA with a working, tested form.

## LinkedIn profile photos
LinkedIn profile images could not be reliably fetched as stable, reusable image assets. The homepage now has local portrait slots with graceful initials fallback:
- `gh-pages/assets/team/josephine.jpg` (Josephine)
- `gh-pages/assets/team/leo.jpg` (Leo)

Upload authorized, suitably cropped JPEG portraits to these exact paths on the `gh-pages` branch. The site will display them automatically, with no HTML change needed. Recommended: square 600×600px JPEG, under 250 KB, strip EXIF metadata. Do not link to expiring LinkedIn CDN photo URLs or use unrelated search-result faces.

The personal LinkedIn profile URLs are already linked directly from both cards. Verify permission from both people before publishing photos.

## Disclosure reminder
The website remains a noindex preview with draft legal disclosures. Contact by email is now enabled, but CV applications are still disabled. The controller, supplier contracts and email privacy disclosure must be finalized before commercial launch.
