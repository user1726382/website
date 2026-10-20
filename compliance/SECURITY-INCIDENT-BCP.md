# Security, incident response and business continuity
DRAFT — controls are requirements, not claims of implementation.

## Security baseline
Inventory production assets and vendors; separate public web, admin, recruitment and home-lab environments. Enforce unique staff accounts, least privilege, MFA for administrative and candidate systems, prompt revocation and quarterly access review. Use HTTPS, disk encryption for candidate files and backups, separate secrets, patched systems, malware checks for uploads, secure logging, and routine vulnerability scanning. Do not store sensitive CVs on an experimental public home server without isolation and tested recovery.

## Supplier governance
Check processor contracts, hosting locations, subprocessor disclosures, access and incident notification terms. Limit third-country transfers and assess lawful transfer mechanisms. Maintain a supplier register and annual reviews.

## Incident response
1. Record incident awareness time, affected systems, reporter and incident owner.
2. Contain and preserve evidence; revoke compromised access.
3. Assess whether personal data confidentiality, integrity or availability was compromised, likelihood/severity of risk and controller/processor roles.
4. Controllers: assess supervisory authority notification within 72 hours of awareness if required by GDPR Art. 33, and affected-person notification without undue delay where Art. 34 high-risk threshold is met. Document non-notification decisions.
5. Processors: notify controller without undue delay, per Art. 33(2) and contract.
6. Restore securely, perform root-cause analysis and document corrective actions.
7. Maintain incident register, train staff and run periodic exercises.

## Continuity
Define service recovery time and data recovery point objectives, encrypted off-site backups, test restores, fallback communications, owner escalation, internet/power failure procedures and vendor outage plan. Verify backups at least quarterly. Never advertise an uptime guarantee without evidence.
