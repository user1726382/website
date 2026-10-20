# Production security and release acceptance checklist
Status: BLOCKED — do not enable recruitment or personal-data forms.

## Code/repository
- [ ] Restore referenced templates, static assets and scripts currently absent from main branch.
- [ ] Add automated unit/integration tests for both languages, admin roles, CSRF, candidate files, retention and rights.
- [ ] Verify no secrets, production data, CVs or credentials are committed.
- [ ] Add secret scanning, dependency audits and container image scans to CI.
- [ ] Verify dependency versions, supply-chain provenance and patch process.
- [ ] Review server-side template escaping, file path handling, authorization, content security policy and request size.
- [ ] Independent code review and penetration test of admin, forms and upload functionality.

## Deployment
- [ ] Approved production host, HTTPS/TLS, domain, DNS, secure proxy and host header validation.
- [ ] Secure session cookies; long random session secret; admin MFA; account recovery and revocation.
- [ ] Restricted admin interface; rate limiting; IP/proxy attribution; monitored alerts.
- [ ] CV malware scan and quarantine, MIME/signature checks, size caps and private storage; reject when scanner unavailable.
- [ ] Encrypted database, private files, offsite backups and verified restore; no public static access to files.
- [ ] Network separation from homelab and personal devices; firewall, patching, incident owner.
- [ ] Approved email sender, SPF/DKIM/DMARC and secure notifications with no CV attachments.
- [ ] Retention/deletion jobs, DSAR and incident runbooks tested end to end.
- [ ] DPA/vendor review and documented hosting geography and transfers.
- [ ] Legal identity, privacy notices, contract terms and licence status signed off.
- [ ] Test WCAG keyboard/screen-reader/contrast/zoom; document applicability and exceptions.
- [ ] Verify robots/indexing, sitemap, canonical and hreflang only after launch sign-off.

## Release record
Release version [ ]; date [ ]; technical owner [ ]; privacy owner [ ]; legal reviewer [ ]; evidence links [ ]; open risks [ ]; GO / NO GO [ ].
