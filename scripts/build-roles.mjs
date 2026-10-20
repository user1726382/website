// Run: node scripts/build-roles.mjs && node scripts/build-roles-de.mjs
// Single source of truth: roles/roles.json. Generated HTML must be committed with data changes.
import fs from 'node:fs';
import path from 'node:path';
const root = process.cwd();
const directory = path.join(root, 'roles');
const data = JSON.parse(fs.readFileSync(path.join(directory, 'roles.json'), 'utf8'));
const escapeHTML = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const euro = value => '€' + Number(value).toLocaleString('en-IE');
const salary = r => euro(r.minSalary) + '–' + euro(r.maxSalary);
const list = values => values.map(v => '<li>' + escapeHTML(v) + '</li>').join('');
const link = r => {
  const action = r.status === 'open' && r.authorised === true ? 'Application' : 'Interest';
  const subject = action + ' – ' + r.title + ' – Dublin';
  const message = 'Hello,\n\nI would like to ' + (action === 'Application' ? 'apply for' : 'register my interest in opportunities like') + ' the ' + r.title + ' role in Dublin.\n\nFull Name:\nCurrent Location:\nPhone Number:\nGerman Proficiency:\nEnglish Proficiency:\nRelevant Experience:\nEarliest Availability:\n\nI will attach my CV manually if I choose to share it.\n\nKind regards,\n\n[Applicant Name]';
  return 'mailto:' + data.contactEmail + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(message);
};
const action = r => r.status === 'open' && r.authorised === true ? 'Apply Now' : 'Register Interest';
const button = r => '<a class="btn" href="' + escapeHTML(link(r)) + '">' + action(r) + ' ↗</a>';
const legalNote = escapeHTML(data.marketNote);
const nav = depth => {
  const home = '../'.repeat(depth) + 'index.html';
  const roles = '../'.repeat(depth - 1);
  return '<header class="site-header"><div class="wrap site-nav"><a class="brand" href="' + home + '">The Link<span style="color:#6b9986">.</span><small>ADVISORY</small></a><nav class="navlinks" aria-label="Main navigation"><a href="' + home + '#services">Services</a><a href="' + home + '#markets">Markets</a><a href="' + home + '#about">Approach</a><a href="' + home + '#team">Our team</a><a class="current" aria-current="page" href="' + roles + '">Roles</a><a class="btn" href="mailto:' + data.contactEmail + '?subject=The%20Link%20enquiry">Contact us</a></nav></div></header>';
};
const footer = depth => {
  const up = '../'.repeat(depth);
  return '<footer class="footer"><div class="wrap"><div><strong>The Link</strong><div>Germany × Ireland</div><div>Explore careers responsibly: role profiles are not advertised vacancies.</div></div><div><a href="' + up + 'legal/en/imprint.html">Legal notice</a> · <a href="' + up + 'legal/en/privacy.html">Privacy</a> · <a href="' + up + 'legal/en/candidates.html">Candidate privacy</a> · <a href="' + up + 'legal/de/impressum.html">Impressum</a></div></div></footer>';
};
const documentHTML = (title, description, depth, main) => {
  const up = '../'.repeat(depth);
  return '<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>' + escapeHTML(title) + ' | The Link</title><meta name="description" content="' + escapeHTML(description) + '"><meta property="og:type" content="website"><meta property="og:title" content="' + escapeHTML(title) + ' | The Link"><meta property="og:description" content="' + escapeHTML(description) + '"><meta property="og:site_name" content="The Link"><link rel="stylesheet" href="' + up + 'roles/styles.css"></head><body>' + nav(depth) + main + footer(depth) + '<script defer src="' + up + 'roles/roles-ui.js"></script></body></html>';
};
const copyEmail = '<div class="copy-row"><span>Or email: <a href="mailto:' + data.contactEmail + '">' + data.contactEmail + '</a></span><button type="button" data-copy-email="' + data.contactEmail + '">Copy email</button><span class="copy-status" role="status" aria-live="polite"></span></div>';
function detail(r) {
  const sales = r.category === 'Sales & Business Development' || r.category === 'Marketing & Advertising';
  const confirmed = r.status === 'open' && r.authorised === true;
  const description = 'Explore the ' + r.title + ' career path in Dublin, Ireland. Indicative base salary ' + salary(r) + '. Register your interest in German-speaking opportunities.';
  const main = '<main><section class="detail-hero"><div class="wrap"><a class="breadcrumb" href="../">← Back to All Roles</a><div class="eyebrow" style="margin-top:24px">' + escapeHTML(r.category) + ' · ' + (confirmed ? 'Open vacancy' : 'Career profile') + '</div><h1>' + escapeHTML(r.title) + '</h1><div class="meta"><span class="chip">' + escapeHTML(r.location) + '</span><span class="chip">' + escapeHTML(r.employmentType) + '</span><span class="chip">Professional German required</span></div><div class="salary">' + salary(r) + '<small>Indicative annual gross base salary' + (sales ? '; additional performance-based pay may be available' : '') + '</small></div>' + button(r) + '<p class="disclaimer">' + legalNote + (confirmed ? '' : ' This is not a confirmed open vacancy.') + '</p></div></section>' +
  '<div class="wrap detail-body"><article><h2>About the Role</h2><p>' + escapeHTML(r.overview) + '</p><h2>Key Responsibilities</h2><ul>' + list(r.responsibilities) + '</ul><h2>Essential Requirements</h2><ul>' + list(r.essential) + '</ul><h2>Desirable Qualifications</h2><ul>' + list(r.desirable) + '</ul><h2>What You Can Expect</h2><p>Depending on the employer, opportunities may include:</p><ul>' + list(r.benefits) + '</ul><p>These are possible arrangements, not confirmed benefits or offers.' + (sales ? " Sales roles may also offer commission or bonuses, subject to the employer's plan." : '') + '</p><h2>About the Company</h2><p>' + escapeHTML(r.company) + '</p>' +
  '<div class="detail-bottom"><h2>Interested in opportunities like this?</h2><p>Contact us by email. Tell us a little about yourself and attach your CV manually if you choose to share it. A CV cannot be attached automatically.</p>' + button(r) + '<p><a href="../">← Back to All Roles</a></p><p style="font-size:13px">Before sharing personal information, read our <a href="../../legal/en/candidates.html" style="text-decoration:underline">candidate privacy information</a>.</p></div></article><aside class="sidebar"><h2>Role at a glance</h2><p><strong>Location</strong><br>' + escapeHTML(r.location) + '</p><p><strong>Base salary</strong><br>' + salary(r) + ' gross/year</p><p><strong>Type</strong><br>' + escapeHTML(r.employmentType) + '</p><p><strong>Language</strong><br>' + escapeHTML(r.language) + '</p><p><strong>Status</strong><br>' + (confirmed ? 'Open vacancy' : 'Career profile · Register interest') + '</p>' + button(r) + '<p>Opens your email app with a role-specific subject and template. Attach your CV manually.</p>' + copyEmail + '</aside></div></main>';
  return documentHTML(r.title, description, 2, main);
}
function card(r) {
  const text = [r.title,r.category,r.location,r.overview].join(' ').toLocaleLowerCase();
  return '<article class="job-card" data-search="' + escapeHTML(text) + '" data-category="' + escapeHTML(r.category) + '" data-location="' + escapeHTML(r.location) + '" data-min-salary="' + r.minSalary + '" data-max-salary="' + r.maxSalary + '"><a class="card-content" href="' + escapeHTML(r.slug) + '/" aria-label="Explore ' + escapeHTML(r.title) + '"><span class="arrow" aria-hidden="true">↗</span><span class="card-category">' + escapeHTML(r.category) + '</span><h2>' + escapeHTML(r.title) + '</h2><div class="meta"><span class="chip">' + escapeHTML(r.location) + '</span><span class="chip">German required</span><span class="chip">' + escapeHTML(r.employmentType) + '</span></div><div class="salary">' + salary(r) + '<small>Gross annual base · indicative</small></div></a><div class="card-bottom">' + button(r) + '</div></article>';
}
function listing() {
  const options = [...new Set(data.roles.map(r=>r.category))].sort().map(x=>'<option value="' + escapeHTML(x) + '">' + escapeHTML(x) + '</option>').join('');
  const main = '<main><section class="hero"><div class="wrap"><div class="eyebrow">German-speaking careers · Ireland</div><h1>Explore German-Speaking Opportunities in Ireland</h1><p>Discover exciting career opportunities with international companies in Ireland. From technology sales and customer success to finance and compliance, we help German-speaking professionals take the next step in their careers.</p><p class="intro-note">Explore ' + data.roles.length + ' career paths for German-speaking professionals. These are illustrative role profiles, not confirmed open vacancies. Register your interest in future opportunities.</p></div></section><div class="wrap"><section class="filters" aria-label="Filter career paths"><div class="filter-grid"><div class="field"><label for="role-search">Search roles</label><input id="role-search" type="search" placeholder="Job title or keyword" autocomplete="off"></div><div class="field"><label for="role-category">Category</label><select id="role-category"><option value="">All categories</option>' + options + '</select></div><div class="field"><label for="role-salary">Indicative annual salary</label><select id="role-salary"><option value="">Any salary</option><option value="35000-45000">€35k–€45k (overlapping)</option><option value="45000-60000">€45k–€60k (overlapping)</option><option value="60000+">€60k+ (overlapping)</option></select></div><div class="field"><label for="role-location">Location</label><select id="role-location"><option value="">All locations</option>' + [...new Set(data.roles.map(r=>r.location))].map(x=>'<option value="' + escapeHTML(x) + '">' + escapeHTML(x) + '</option>').join('') + '</select></div></div><div class="filter-bottom"><p id="result-count" role="status" aria-live="polite">' + data.roles.length + ' of ' + data.roles.length + ' career paths</p><button id="reset-filters" class="text-button" type="button">Clear filters</button></div></section><div class="copy-row" style="margin:0 0 22px"><span>Prefer to email us directly? <a href="mailto:' + data.contactEmail + '">' + data.contactEmail + '</a></span><button type="button" data-copy-email="' + data.contactEmail + '">Copy email</button><span class="copy-status" role="status" aria-live="polite"></span></div><div class="cards" id="role-cards">' + data.roles.map(card).join('') + '</div><div class="no-results" id="no-results" hidden><h2>No matching roles</h2><p>Try another keyword, salary range or category.</p><button id="empty-reset" class="btn" type="button">Reset filters</button></div><p class="disclaimer" style="margin-bottom:55px">' + legalNote + ' Salary ranges do not represent offers from a named employer. Please read our <a href="../legal/en/candidates.html" style="text-decoration:underline">candidate privacy information</a> before sending a CV.</p></div></main>';
  return documentHTML('Explore German-Speaking Opportunities in Ireland','Explore German-speaking career paths in Dublin across sales, customer success, support, finance and compliance.',1,main);
}
function withLanguageToggle(html,slug='') {
  const german = slug ? '../de/'+slug+'/' : 'de/';
  return html.replace('</nav></div></header>', '<a class="lang" lang="de" hreflang="de" href="'+german+'" aria-label="Auf Deutsch anzeigen">DE</a></nav></div></header>')
    .replace('<link rel="stylesheet"', '<link rel="alternate" hreflang="en" href="./"><link rel="alternate" hreflang="de" href="'+german+'"><link rel="stylesheet"');
}
fs.writeFileSync(path.join(directory,'index.html'),withLanguageToggle(listing()));
for (const r of data.roles) {
  if (!/^[a-z0-9-]+$/.test(r.slug)) throw Error('Unsafe slug: '+r.slug);
  const target = path.join(directory,r.slug);
  fs.mkdirSync(target,{recursive:true});
  fs.writeFileSync(path.join(target,'index.html'),withLanguageToggle(detail(r),r.slug));
}
console.log('Generated roles landing page and '+data.roles.length+' detail pages from roles/roles.json');
