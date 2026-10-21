(function(){'use strict';const q=s=>document.querySelector(s);const search=q('#role-search'),category=q('#role-category'),salary=q('#role-salary'),location=q('#role-location'),reset=q('#reset-filters'),count=q('#result-count'),empty=q('#no-results'),emptyReset=q('#empty-reset');if(search&&category&&salary&&location){const cards=Array.from(document.querySelectorAll('.job-card'));function apply(){const term=search.value.trim().toLocaleLowerCase(),cat=category.value,loc=location.value,band=salary.value;let n=0;for(const card of cards){const min=Number(card.dataset.minSalary),max=Number(card.dataset.maxSalary);const salaryOk=!band||(()=>{const parts=band.replace('+','').split('-').map(Number);const lo=parts[0],hi=parts.length===2?parts[1]:Infinity;return max>=lo&&min<=hi})();const yes=(!term||card.dataset.search.includes(term))&&(!cat||card.dataset.category===cat)&&(!loc||card.dataset.location===loc)&&salaryOk;card.hidden=!yes;if(yes)n++}count.textContent=document.documentElement.lang==='de'?n+' von '+cards.length+' Stellen':n+' of '+cards.length+' roles';empty.hidden=n!==0}function clear(){search.value='';category.value='';salary.value='';location.value='';apply();search.focus()}[search,category,salary,location].forEach(x=>x.addEventListener(x===search?'input':'change',apply));reset.addEventListener('click',clear);emptyReset.addEventListener('click',clear);apply()}document.querySelectorAll('[data-copy-email]').forEach(button=>button.addEventListener('click',async()=>{const address=button.dataset.copyEmail,status=button.parentElement.querySelector('.copy-status');try{if(!navigator.clipboard||!window.isSecureContext)throw Error('Clipboard unavailable');await navigator.clipboard.writeText(address);status.textContent=document.documentElement.lang==='de'?'E-Mail-Adresse kopiert.':'Email address copied.'}catch(_){status.textContent=(document.documentElement.lang==='de'?'E-Mail-Adresse zum Kopieren: ':'Copy this email address: ')+address}}));})();
/* Cross-site navigation and candidate enquiry enhancements. All existing role records are career profiles, not verified vacancies. */
(function(){'use strict';
const de=document.documentElement.lang==='de',base=new URL('../',document.currentScript.src).href;
document.querySelectorAll('.site-header .navlinks').forEach(nav=>{
  const links=de?[['Für Unternehmen','de/unternehmen/'],['Gehälter','de/gehaelter/'],['Arbeiten in Irland','de/arbeiten-in-irland/']]:[['For employers','employers/'],['Salary guide','salary-guide/'],['Working in Ireland','working-in-ireland/']];
  for(const [label,path] of links){const a=document.createElement('a');a.href=base+path;a.textContent=label;a.className='added-nav';nav.insertBefore(a,nav.querySelector('.btn'))}
});
document.querySelectorAll('.footer .wrap>div:first-child').forEach(el=>{
  const p=document.createElement('p');p.className='footer-direct';p.innerHTML='<a href="tel:+353874319648">+353 87 431 9648</a> · <a href="mailto:leoedwlashe@gmail.com">'+(de?'Kontakt aufnehmen':'Contact us')+'</a>';el.append(p)
});
document.querySelectorAll('a.btn[href^="mailto:"][href*="Application"],a.btn[href^="mailto:"][href*="Bewerbung"]').forEach(a=>{
  a.textContent=de?'Zum Berufsprofil anfragen ↗':'Enquire about this role ↗';
  a.setAttribute('aria-label',de?'Zum Berufsprofil anfragen':'Enquire about this role');
  a.href=a.href.replace('Application','Career%20enquiry').replace('Bewerbung','Karriereanfrage')
});
document.querySelectorAll('.detail-bottom p,.sidebar p').forEach(p=>{
  if(p.textContent.includes('Contact us by email. Tell us'))p.textContent='Contact us to discuss your interest in this career path. We can clarify whether a specific opportunity is available.';
  if(p.textContent.includes('Bewerben Sie sich per E-Mail.'))p.textContent='Kontaktieren Sie uns zu diesem Berufsprofil. Wir können klären, ob eine konkrete Stelle verfügbar ist.';
  if(p.textContent.includes('Attach your CV manually.'))p.textContent='Opens your email application. Please review the candidate privacy information before sharing personal details.';
  if(p.textContent.includes('Einen Lebenslauf müssen Sie selbst anhängen.'))p.textContent='Öffnet Ihr E-Mail-Programm. Bitte beachten Sie die Bewerberdatenschutzhinweise.';
});
if(document.querySelector('.detail-hero h1')){
 const area=document.querySelector('.detail-bottom'),slug=location.pathname.split('/').filter(Boolean).at(-1);
 if(area&&slug){const related=document.createElement('p');related.innerHTML='<a href="'+base+(de?'de/gehaelter/':'salary-guide/')+'">'+(de?'Gehälter vergleichen':'Compare salaries')+' ↗</a> · <a href="'+base+(de?'de/arbeiten-in-irland/':'working-in-ireland/')+'">'+(de?'Arbeiten in Irland':'Working in Ireland')+' ↗</a>';area.append(related)}
}
})();
