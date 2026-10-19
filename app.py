"""Bridgefield Advisory — bilingual B2B site and single-instance admin.
Run: uvicorn app:app --reload. Set env secrets before a public deployment.
"""
from __future__ import annotations
import os, re, secrets, time, hmac, hashlib, uuid, smtplib, html, io, zipfile, json, shutil, subprocess
from pathlib import Path
from contextlib import asynccontextmanager
from email.message import EmailMessage
from urllib.parse import urlparse
from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from argon2 import PasswordHasher, exceptions as argon_errors
from dotenv import load_dotenv
from PIL import Image, UnidentifiedImageError
import database as db
from content import PATHS, PAGES, HOME, UI, SERVICES, PROCESS, WHY, AUDIENCES, SOLUTIONS, FAQS, LEGAL, url

ROOT=Path(__file__).resolve().parent
load_dotenv(ROOT/'.env')
# Resolve file paths relative to project root; absolute paths are also accepted.
def resolved(p):
    v=Path(p)
    return v if v.is_absolute() else ROOT / v

db.DB_PATH=str(resolved(os.getenv('DB_PATH','./data/bridgefield.sqlite3')))
UPLOAD_DIR=resolved(os.getenv('UPLOAD_DIR','./private_uploads'))
MEDIA_DIR=resolved(os.getenv('MEDIA_DIR','./media_uploads'))
MEDIA_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
try: UPLOAD_DIR.chmod(0o700)
except Exception: pass
COMPANY=os.getenv('SITE_NAME','Bridgefield Advisory')
WORDMARK=os.getenv('BRAND_WORDMARK','bridgefield')
SITE_DOMAIN=os.getenv('SITE_DOMAIN','https://example.com').rstrip('/')
COOKIE_SECURE=os.getenv('COOKIE_SECURE','false').lower()=='true'
SESSION_SECRET=os.getenv('SESSION_SECRET') or secrets.token_urlsafe(48)
ADMIN_USER=os.getenv('ADMIN_USER','admin')
ADMIN_HASH=os.getenv('ADMIN_PASSWORD_HASH','')
CONTACT_EMAIL=os.getenv('CONTACT_EMAIL','hello@example.com')
CONTACT_PHONE=os.getenv('CONTACT_PHONE','')
LINKEDIN_URL=os.getenv('LINKEDIN_URL','')
BOOKING_URL=os.getenv('BOOKING_URL','')
ph=PasswordHasher()
rate_state={}

def limited(key, limit=12, window=3600):
    now=time.monotonic()
    timestamps=[x for x in rate_state.get(key,[]) if now-x<window]
    if len(timestamps)>=limit:
        rate_state[key]=timestamps
        return True
    timestamps.append(now)
    rate_state[key]=timestamps
    if len(rate_state)>10000:
        for k in list(rate_state)[:1000]: rate_state.pop(k,None)
    return False

@asynccontextmanager
async def lifespan(app):
    db.init()
    yield

app=FastAPI(title='Bridgefield Advisory', docs_url=None, redoc_url=None, lifespan=lifespan)
app.add_middleware(SessionMiddleware,secret_key=SESSION_SECRET,https_only=COOKIE_SECURE,same_site='lax',max_age=60*60*6)
app.mount('/static',StaticFiles(directory=str(ROOT/'static')),name='static')
templates=Jinja2Templates(directory=str(ROOT/'templates'))

def csrf(request):
    if 'csrf' not in request.session: request.session['csrf']=secrets.token_urlsafe(24)
    return request.session['csrf']

def check_csrf(request, token):
    expected=request.session.get('csrf','')
    if not expected or not hmac.compare_digest(expected,token or ''):
        raise HTTPException(403,'Invalid or expired form token. Refresh the page and try again.')

def setting(key, fallback):
    row=db.one('SELECT value FROM settings WHERE key=?',(key,))
    return row['value'] if row else fallback

def get_page(locale,ident):
    if ident=='home':return override(locale,ident,HOME[locale])
    if ident in PAGES[locale]:return override(locale,ident,PAGES[locale][ident])
    if ident in LEGAL[locale]:
        title,body=LEGAL[locale][ident]
        return override(locale,ident,{'title':title,'body':body})
    raise KeyError(ident)

def page_fields(ident):
    if ident=='home':return ['eyebrow','title','summary','services_title','services_desc','markets_title','markets_desc','why_title','why_desc','process_title','solutions_title','insights_title','final_title','final_body','meta_title','meta_description']
    if ident in LEGAL['en']:return ['title','body','meta_title','meta_description']
    return ['eyebrow','title','intro','challenge','challenge_text','features','deliverables','faqs','meta_title','meta_description']

def ctx(request, locale='en', **kw):
    if locale not in ('de','en'): locale='en'
    ident=kw.get('page_id','home')
    suffix=''
    canonical=kw.get('canonical','')
    if ident in PATHS and canonical:
        own_url=SITE_DOMAIN+url(locale,ident)
        if canonical.startswith(own_url): suffix=canonical[len(own_url):]
    alt_en=SITE_DOMAIN+url('en',ident)+suffix if ident in PATHS else ''
    alt_de=SITE_DOMAIN+url('de',ident)+suffix if ident in PATHS else ''
    switch_link=url('de' if locale=='en' else 'en',ident)+suffix if ident in PATHS else url('en','home')
    meta=db.one('SELECT value FROM page_overrides WHERE locale=? AND page_id=? AND field=?',(locale,ident,'meta_description'))
    meta_t=db.one('SELECT value FROM page_overrides WHERE locale=? AND page_id=? AND field=?',(locale,ident,'meta_title'))
    copy=kw.get('page') or kw.get('home') or kw.get('article') or {}
    preferred_summary=(copy.get('intro') or copy.get('summary') or copy.get('excerpt_'+locale) or '') if isinstance(copy,dict) else ''
    structured_data=None
    if os.getenv('PUBLISH_STRUCTURED_DATA','false').lower()=='true':
        provider={'@type':'Organization','name':setting('site_name',COMPANY),'url':SITE_DOMAIN}
        if ident in ('recruitment','market-entry','marketing') and kw.get('page'):
            p=kw['page'];structured_data={'@context':'https://schema.org','@type':'Service','name':p['title'],'description':p['intro'],'provider':provider,'areaServed':[{'@type':'Country','name':'Germany'},{'@type':'Country','name':'Ireland'}]}
        elif kw.get('article'):
            art=kw['article'];structured_data={'@context':'https://schema.org','@type':'Article','headline':art['title_'+locale],'description':art['excerpt_'+locale],'datePublished':art['published_at'],'publisher':provider,'inLanguage':locale,'mainEntityOfPage':canonical}
        elif kw.get('job') and kw['job'].get('employer_name'):
            job=kw['job'];structured_data={'@context':'https://schema.org','@type':'JobPosting','title':job['title_'+locale],'description':job['description_'+locale],'datePosted':job['created_at'][:10],'hiringOrganization':{'@type':'Organization','name':job['employer_name']},'jobLocation':{'@type':'Place','address':{'@type':'PostalAddress','addressLocality':job['location'],'addressCountry':'DE' if job['country']=='Germany' else 'IE'}},'inLanguage':locale}
        elif ident=='home':
            structured_data={'@context':'https://schema.org','@type':'Organization','name':provider['name'],'url':SITE_DOMAIN,'areaServed':['Germany','Ireland']}
    return dict(request=request,locale=locale,ui=UI[locale],urls={k:url(locale,k) for k in PATHS},
     other_locale='de' if locale=='en' else 'en',other_lang_link=switch_link,alternate_en=alt_en,alternate_de=alt_de,structured_data=structured_data,
     company=setting('site_name',COMPANY),wordmark=setting('brand_wordmark',WORDMARK),meta_title=meta_t['value'] if meta_t else None,brand_caption=UI[locale]['brand_small'],contact_email=setting('contact_email',CONTACT_EMAIL),
     contact_phone=setting('contact_phone',CONTACT_PHONE),linkedin_url=setting('linkedin_url',LINKEDIN_URL),booking_url=setting('booking_url',BOOKING_URL),
     csrf=csrf(request),year=__import__('datetime').datetime.now().year,
     consent_enabled=False,inquiries_enabled=os.getenv('ACCEPT_INQUIRIES','false').lower()=='true',applications_enabled=os.getenv('ACCEPT_APPLICATIONS','false').lower()=='true',meta_description=(meta['value'] if meta else (preferred_summary or (kw.get('page_title','')+'. '+('Cross-border recruitment, market entry and marketing for Germany and Ireland.' if locale=='en' else 'Recruiting, Markteintritt und Marketing zwischen Deutschland und Irland.')))[:160]), **kw)

def render(request, name, locale='en', status=200, **kwargs):
    return templates.TemplateResponse(request,name,ctx(request,locale,**kwargs),status_code=status)

def override(locale, ident, page):
    new=page.copy()
    for row in db.many('SELECT field,value FROM page_overrides WHERE locale=? AND page_id=?',(locale,ident)):
        if row['field'] in new or row['field'] in ('meta_title','meta_description'):
            if row['field'] in ('features','deliverables','faqs'):
                try: new[row['field']]=json.loads(row['value'])
                except (ValueError,TypeError):pass
            else:new[row['field']]=row['value']
    return new

def local_path(locale, path):
    for ident, v in PATHS.items():
        if v[0 if locale=='en' else 1]==path:return ident
    return None

def public_jobs():
    return db.many('SELECT * FROM jobs WHERE published=1 ORDER BY created_at DESC')

def public_articles():
    return db.many('SELECT * FROM articles WHERE published=1 ORDER BY published_at DESC')

def user_ip(request):
    return request.client.host if request.client else 'unknown'

def redirect(url_, status=303):return RedirectResponse(url_,status_code=status)

@app.middleware('http')
async def security_headers(request,call_next):
    resp=await call_next(request)
    resp.headers['X-Content-Type-Options']='nosniff'
    resp.headers['X-Frame-Options']='DENY'
    resp.headers['Referrer-Policy']='strict-origin-when-cross-origin'
    resp.headers['Permissions-Policy']='camera=(), microphone=(), geolocation=()'
    resp.headers['Content-Security-Policy']="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'; form-action 'self'"
    if request.url.path.startswith('/admin') or request.url.path.startswith('/forms'):
        resp.headers['Cache-Control']='no-store'
    return resp

@app.get('/',include_in_schema=False)
async def root(): return redirect('/en/',302)

@app.get('/favicon.ico',include_in_schema=False)
async def favicon(): return FileResponse(ROOT/'static/img/favicon.svg',media_type='image/svg+xml')

@app.get('/robots.txt',include_in_schema=False)
async def robots():
    return PlainTextResponse('User-agent: *\nDisallow: /admin/\nDisallow: /forms/\nSitemap: '+SITE_DOMAIN+'/sitemap.xml\n')

@app.get('/sitemap.xml',include_in_schema=False)
async def sitemap():
    from xml.sax.saxutils import escape
    excluded={'imprint','privacy','terms','accessibility','cookies','thanks','cases'}
    entries=[]
    for ident in PATHS:
        if ident in excluded: continue
        for loc in ('en','de'):
            location=escape(SITE_DOMAIN+url(loc,ident))
            alternates=''.join(f'<xhtml:link rel="alternate" hreflang="{l}" href="{escape(SITE_DOMAIN+url(l,ident))}"/>' for l in ('en','de'))
            entries.append(f'<url><loc>{location}</loc>{alternates}</url>')
    for article in public_articles():
        for loc in ('en','de'):
            link=escape(SITE_DOMAIN+url(loc,'insights')+'/'+article['slug'])
            entries.append(f'<url><loc>{link}</loc></url>')
    for job in public_jobs():
        for loc in ('en','de'):
            link=escape(SITE_DOMAIN+url(loc,'jobs')+'/'+job['slug'])
            entries.append(f'<url><loc>{link}</loc></url>')
    xml='<?xml version="1.0" encoding="utf-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">'+''.join(entries)+'</urlset>'
    return Response(xml,media_type='application/xml')

@app.get('/{locale}/',response_class=HTMLResponse)
async def home(request:Request,locale:str):
    if locale not in ('en','de'):raise HTTPException(404)
    return render(request,'home.html',locale,home=get_page(locale,'home'),services=SERVICES[locale],process=PROCESS[locale],why=WHY[locale],audiences=AUDIENCES[locale],solutions=SOLUTIONS[locale],faqs=FAQS[locale][:5],articles=public_articles()[:3],page_id='home',page_title=HOME[locale]['title'],canonical=SITE_DOMAIN+url(locale,'home'))

EMAIL_RE=re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]{2,}$')

def valid(v,maxlen=5000):return (v or '').strip()[:maxlen]
def require_form_rate(request, kind):
    if limited(kind+':'+user_ip(request),limit=8,window=3600):raise HTTPException(429,'Too many submissions. Try again later.')
def mail_notify(subject,body):
    host=os.getenv('SMTP_HOST',''); receiver=os.getenv('NOTIFICATION_TO','')
    if not host or not receiver:return
    msg=EmailMessage()
    msg['Subject']='Website: '+subject[:100].replace('\n',' ')
    msg['From']=os.getenv('SMTP_FROM',CONTACT_EMAIL)
    msg['To']=receiver
    msg.set_content(body)
    try:
        with smtplib.SMTP(host,int(os.getenv('SMTP_PORT','587')),timeout=5) as server:
            server.starttls()
            if os.getenv('SMTP_USERNAME'):server.login(os.getenv('SMTP_USERNAME'),os.getenv('SMTP_PASSWORD',''))
            server.send_message(msg)
    except Exception:
        # Database has the authoritative record; email is best-effort.
        import logging; logging.warning('Lead email notification unsuccessful (submission remains stored)')

@app.post('/forms/inquiry')
async def inquiry(request:Request):
    form=await request.form()
    locale='de' if form.get('locale')=='de' else 'en'
    check_csrf(request,str(form.get('csrf','')))
    require_form_rate(request,'inquiry')
    if form.get('website_hp'):return redirect(url(locale,'thanks'))
    if os.getenv('ACCEPT_INQUIRIES','false').lower()!='true':raise HTTPException(503,'Inquiry processing is not enabled until legal and operational setup is complete.')
    if form.get('privacy_read')!='on':raise HTTPException(422,'Privacy acknowledgement required')
    name=valid(form.get('name'),150)
    email=valid(form.get('email'),200)
    message=valid(form.get('message'),8000)
    if not name or not EMAIL_RE.match(email) or not message:
        return render(request,'contact.html',locale,status=422,page_id='contact',page_title='Contact',error=UI[locale]['form_error'])
    kind=valid(form.get('kind'),50)
    if kind not in ('general','employer'):kind='general'
    values=(db.uid(),db.now(),kind,name,valid(form.get('company'),200),email,valid(form.get('phone'),80),valid(form.get('country'),60),valid(form.get('service'),80),valid(form.get('role_title'),180),valid(form.get('city'),150),valid(form.get('employment_type'),50),valid(form.get('salary'),80),valid(form.get('vacancies'),30),valid(form.get('timeline'),100),valid(form.get('website'),250),valid(form.get('budget'),100),message)
    db.execute('''INSERT INTO inquiries (id,created_at,kind,name,company,email,phone,country,service,role_title,city,employment_type,salary,vacancies,timeline,website,budget,message) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',values)
    mail_notify('New '+kind+' inquiry',f'An inquiry was saved in the admin dashboard. Type: {kind}; service: {values[8]}.')
    return redirect(url(locale,'thanks'))

def valid_upload(content,filename):
    ext=Path(filename).suffix.lower()
    if ext=='.pdf' and content.startswith(b'%PDF-'):return True
    if ext=='.docx' and content.startswith(b'PK'):
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as z:
                names=z.namelist()
                return 'word/document.xml' in names and len(names)<500
        except (ValueError,zipfile.BadZipFile):return False
    return False

@app.post('/forms/apply')
async def apply(request:Request, cv:UploadFile=File(...)):
    form=await request.form()
    locale='de' if form.get('locale')=='de' else 'en'
    check_csrf(request,str(form.get('csrf','')))
    require_form_rate(request,'apply')
    if form.get('website_hp'):return redirect(url(locale,'thanks'))
    if form.get('privacy_read')!='on':raise HTTPException(422,'Privacy acknowledgement required')
    if os.getenv('ACCEPT_APPLICATIONS','false').lower()!='true':raise HTTPException(503,'Applications are not currently enabled.')
    name=valid(form.get('name'),150); email=valid(form.get('email'),200)
    if not name or not EMAIL_RE.match(email):raise HTTPException(422,'Name and valid email are required')
    # No unlimited reads: cap stream at 5 MiB + 1 byte.
    content=await cv.read(5*1024*1024+1)
    filename=Path(cv.filename or 'resume').name[:150]
    if len(content)>5*1024*1024 or not valid_upload(content,filename):
        raise HTTPException(422,'CV must be a valid PDF or DOCX file smaller than 5 MB.')
    job_id=valid(form.get('job_id'),100)
    if job_id and not db.one('SELECT id FROM jobs WHERE id=? AND published=1',(job_id,)):
        raise HTTPException(422,'This job is no longer accepting applications.')
    file_id=secrets.token_hex(24)
    file_path=UPLOAD_DIR/file_id
    file_path.write_bytes(content)
    file_path.chmod(0o600)
    # Fail closed when antivirus is not available. 'off' is for isolated local testing only.
    mode=os.getenv('CV_SCAN_MODE','clamscan')
    if mode!='off':
        executable=shutil.which('clamscan') if mode=='clamscan' else None
        if not executable:
            file_path.unlink(missing_ok=True)
            raise HTTPException(503,'CV malware scanning is not configured.')
        try:
            scan=subprocess.run([executable,'--no-summary',str(file_path)],capture_output=True,timeout=45,check=False)
        except (OSError,subprocess.TimeoutExpired):
            file_path.unlink(missing_ok=True)
            raise HTTPException(503,'CV malware scanning is temporarily unavailable.')
        if scan.returncode != 0:
            file_path.unlink(missing_ok=True)
            raise HTTPException(422 if scan.returncode==1 else 503,'CV did not pass the file security check.')
    db.execute('''INSERT INTO applications (id,created_at,name,email,phone,country,linkedin,job_id,cover_letter,filename,file_path) VALUES (?,?,?,?,?,?,?,?,?,?,?)''',
      (db.uid(),db.now(),name,email,valid(form.get('phone'),80),valid(form.get('country'),100),valid(form.get('linkedin'),250),job_id or None,valid(form.get('cover_letter'),4000),filename,str(file_path)))
    mail_notify('New candidate application','A candidate application was saved to the protected admin dashboard.')
    return redirect(url(locale,'thanks'))

def audit(action, record_id=''):
    db.execute('INSERT INTO admin_audit(id,created_at,action,record_id) VALUES(?,?,?,?)',(db.uid(),db.now(),action,record_id))

# === ADMIN ===
def current_role(request):
    if not request.session.get('admin'):return None
    name=request.session.get('username')
    if name=='_environment_admin_':return 'admin' if ADMIN_HASH else None
    user=db.one('SELECT role,enabled FROM users WHERE username=?',(name,))
    return user['role'] if user and user['enabled'] else None

def authenticated(request):return current_role(request) is not None

def require_admin(request, roles=None):
    role=current_role(request)
    if role is None or (roles is not None and role not in roles):
        raise HTTPException(403,'Insufficient administrator permissions')


def admin_context(request,**kwargs):return dict(request=request,company=setting('site_name',COMPANY),csrf=csrf(request),role=current_role(request),**kwargs)

def admin_render(request,name,**kwargs):
    return templates.TemplateResponse(request,'admin/'+name,admin_context(request,**kwargs))

@app.get('/admin')
async def admin_index(request:Request):
    if not authenticated(request):return redirect('/admin/login')
    role=current_role(request)
    visible={'admin':['inquiries','applications','jobs','articles'],'content':['articles'],'marketing':['inquiries','articles'],'recruitment':['applications','jobs']}[role]
    counts={key:db.one(f'SELECT COUNT(*) AS n FROM {key}')['n'] for key in visible}
    return admin_render(request,'index.html',counts=counts,audits=(db.many('SELECT * FROM admin_audit ORDER BY created_at DESC LIMIT 12') if role=='admin' else []),inquiries=(db.many('SELECT * FROM inquiries ORDER BY created_at DESC LIMIT 40') if 'inquiries' in visible else []),applications=(db.many('SELECT * FROM applications ORDER BY created_at DESC LIMIT 40') if 'applications' in visible else []))

@app.get('/admin/login')
async def admin_login_page(request:Request):
    return admin_render(request,'login.html',configured=bool((ADMIN_HASH or db.one('SELECT username FROM users LIMIT 1')) and os.getenv('SESSION_SECRET')))

@app.post('/admin/login')
async def admin_login(request:Request):
    form=await request.form(); check_csrf(request,str(form.get('csrf','')))
    if limited('login:'+user_ip(request),limit=6,window=900):raise HTTPException(429,'Too many login attempts')
    if (not ADMIN_HASH and not db.one('SELECT username FROM users LIMIT 1')) or not os.getenv('SESSION_SECRET'):
        return admin_render(request,'login.html',error='Admin setup is incomplete. Configure SESSION_SECRET and an administrator.',configured=False)
    username=str(form.get('username',''))
    db_user=db.one('SELECT username,password_hash,role,enabled FROM users WHERE username=?',(username,))
    stored_hash=db_user['password_hash'] if db_user and db_user['enabled'] else (ADMIN_HASH if username==ADMIN_USER else '')
    try:
        valid_password=bool(stored_hash) and ph.verify(stored_hash,str(form.get('password','')))
    except (argon_errors.VerifyMismatchError,argon_errors.InvalidHashError,argon_errors.VerificationError):valid_password=False
    if not valid_password:
        return admin_render(request,'login.html',error='Invalid credentials',configured=True)
    request.session.clear();request.session['admin']=True
    request.session['username']=username if db_user and db_user['enabled'] else '_environment_admin_'
    csrf(request)
    audit('admin.login',username)
    return redirect('/admin')

@app.post('/admin/logout')
async def admin_logout(request:Request):
    form=await request.form();check_csrf(request,str(form.get('csrf','')))
    request.session.clear()
    return redirect('/admin/login')

@app.get('/admin/jobs')
async def admin_jobs(request:Request):
    require_admin(request,roles=('admin','recruitment'))
    return admin_render(request,'jobs.html',jobs=db.many('SELECT * FROM jobs ORDER BY created_at DESC'))

@app.get('/admin/jobs/new')
async def admin_jobs_new(request:Request):
    require_admin(request,roles=('admin','recruitment'));return admin_render(request,'job_edit.html',job=None)

@app.get('/admin/jobs/{ident}')
async def admin_job_edit(request:Request,ident:str):
    require_admin(request,roles=('admin','recruitment'))
    job=db.one('SELECT * FROM jobs WHERE id=?',(ident,))
    if not job:raise HTTPException(404)
    return admin_render(request,'job_edit.html',job=job)

@app.post('/admin/jobs/save')
async def admin_job_save(request:Request):
    require_admin(request,roles=('admin','recruitment'))
    form=await request.form();check_csrf(request,str(form.get('csrf','')))
    ident=valid(form.get('id'),100) or db.uid()
    slug=valid(form.get('slug'),120).lower()
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',slug):raise HTTPException(422,'Slug must use lowercase letters, numbers and hyphens')
    vals=(slug,valid(form.get('title_en'),150),valid(form.get('employer_name'),200),valid(form.get('title_de'),150),valid(form.get('location'),120),valid(form.get('country'),70),valid(form.get('category'),70),valid(form.get('employment_type'),70),valid(form.get('description_en'),20000),valid(form.get('description_de'),20000),int(form.get('published')=='on'))
    if not all(v for i,v in enumerate(vals[:10]) if i!=2):raise HTTPException(422,'All bilingual job fields are required')
    if db.one('SELECT id FROM jobs WHERE id=?',(ident,)):
        db.execute('''UPDATE jobs SET slug=?,title_en=?,employer_name=?,title_de=?,location=?,country=?,category=?,employment_type=?,description_en=?,description_de=?,published=? WHERE id=?''',vals+(ident,))
    else:
        db.execute('''INSERT INTO jobs (slug,title_en,employer_name,title_de,location,country,category,employment_type,description_en,description_de,published,id,created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)''',vals+(ident,db.now()))
    audit('jobs.save',ident)
    return redirect('/admin/jobs')

@app.get('/admin/articles')
async def admin_articles(request:Request):
    require_admin(request,roles=('admin','content','marketing'))
    return admin_render(request,'articles.html',articles=db.many('SELECT * FROM articles ORDER BY published_at DESC'))

@app.get('/admin/articles/new')
async def admin_article_new(request:Request):
    require_admin(request,roles=('admin','content','marketing'));return admin_render(request,'article_edit.html',article=None)

@app.get('/admin/articles/{ident}')
async def admin_article_edit(request:Request,ident:str):
    require_admin(request,roles=('admin','content','marketing'))
    article=db.one('SELECT * FROM articles WHERE id=?',(ident,))
    if not article:raise HTTPException(404)
    return admin_render(request,'article_edit.html',article=article,media=db.many('SELECT * FROM media ORDER BY created_at DESC'))

@app.post('/admin/articles/save')
async def admin_article_save(request:Request):
    require_admin(request,roles=('admin','content','marketing'))
    form=await request.form();check_csrf(request,str(form.get('csrf','')))
    ident=valid(form.get('id'),100) or db.uid()
    slug=valid(form.get('slug'),120).lower()
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',slug):raise HTTPException(422,'Invalid slug')
    cover=valid(form.get('cover_image'),120)
    if cover and not db.one('SELECT file_name FROM media WHERE file_name=?',(cover,)):raise HTTPException(422,'Cover image does not exist')
    vals=(slug,valid(form.get('category'),70),valid(form.get('title_en'),200),valid(form.get('title_de'),200),valid(form.get('excerpt_en'),400),valid(form.get('excerpt_de'),400),valid(form.get('body_en'),30000),valid(form.get('body_de'),30000),int(form.get('published')=='on'),valid(form.get('published_at'),30) or db.now()[:10],cover)
    if not all(vals[:8]):raise HTTPException(422,'All article fields are required')
    if db.one('SELECT id FROM articles WHERE id=?',(ident,)):
        db.execute('''UPDATE articles SET slug=?,category=?,title_en=?,title_de=?,excerpt_en=?,excerpt_de=?,body_en=?,body_de=?,published=?,published_at=?,cover_image=? WHERE id=?''',vals+(ident,))
    else:
        db.execute('''INSERT INTO articles (slug,category,title_en,title_de,excerpt_en,excerpt_de,body_en,body_de,published,published_at,cover_image,id) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',vals+(ident,))
    audit('articles.save',ident)
    return redirect('/admin/articles')

@app.get('/admin/pages')
async def admin_pages(request:Request):
    require_admin(request,roles=('admin','content','marketing'))
    return admin_render(request,'pages.html',pages=[('home',HOME['en']['title'])]+[(ident,PAGES['en'][ident]['title']) for ident in PAGES['en']]+[(ident,LEGAL['en'][ident][0]) for ident in LEGAL['en']])

@app.get('/admin/pages/{ident}')
async def admin_page_edit(request:Request,ident:str):
    require_admin(request,roles=('admin','content','marketing'))
    if ident!='home' and ident not in PAGES['en'] and ident not in LEGAL['en']:raise HTTPException(404)
    values={locale:get_page(locale,ident) for locale in ('en','de')}
    for loc in values:
        for field in ('features','faqs'):
            if field in values[loc]: values[loc][field]='\n'.join(str(a)+' | '+str(b) for a,b in values[loc][field])
        if 'deliverables' in values[loc]: values[loc]['deliverables']='\n'.join(values[loc]['deliverables'])
    return admin_render(request,'page_edit.html',ident=ident,en=values['en'],de=values['de'],fields=page_fields(ident))

@app.post('/admin/pages/{ident}')
async def admin_page_save(request:Request,ident:str):
    require_admin(request,roles=('admin','content','marketing'))
    if ident!='home' and ident not in PAGES['en'] and ident not in LEGAL['en']:raise HTTPException(404)
    form=await request.form();check_csrf(request,str(form.get('csrf','')))
    for locale in ('en','de'):
        for field in page_fields(ident):
            v=valid(form.get(locale+'_'+field),20000)
            if field in ('features','faqs'):
                pairs=[]
                for line in v.splitlines():
                    if line.strip():
                        if ' | ' not in line:raise HTTPException(422,'Each feature/FAQ must be formatted: heading | description')
                        heading,desc=line.split(' | ',1)
                        pairs.append([heading.strip()[:200],desc.strip()[:1200]])
                v=json.dumps(pairs,ensure_ascii=False)
            elif field=='deliverables':v=json.dumps([line.strip()[:200] for line in v.splitlines() if line.strip()],ensure_ascii=False)
            if v:db.execute('INSERT INTO page_overrides(locale,page_id,field,value) VALUES(?,?,?,?) ON CONFLICT(locale,page_id,field) DO UPDATE SET value=excluded.value',(locale,ident,field,v))
    audit('page.copy.save',ident)
    return redirect('/admin/pages')

@app.get('/admin/inquiries')
async def admin_inquiries(request:Request):
    require_admin(request,roles=('admin','marketing'))
    return admin_render(request,'submissions.html',kind='inquiries',rows=db.many('SELECT * FROM inquiries ORDER BY created_at DESC LIMIT 500'))

@app.get('/admin/applications')
async def admin_applications(request:Request):
    require_admin(request,roles=('admin','recruitment'))
    return admin_render(request,'submissions.html',kind='applications',rows=db.many('SELECT * FROM applications ORDER BY created_at DESC LIMIT 500'))

@app.post('/admin/submissions/status')
async def admin_status(request:Request):
    require_admin(request)
    form=await request.form();check_csrf(request,str(form.get('csrf','')))
    kind=str(form.get('kind',''))
    if kind not in ('inquiries','applications'):raise HTTPException(422)
    require_admin(request,roles=('admin','recruitment') if kind=='applications' else ('admin','marketing'))
    status=str(form.get('status',''))
    if status not in ('new','in_progress','closed','delete_requested'):raise HTTPException(422)
    db.execute(f'UPDATE {kind} SET status=? WHERE id=?',(status,str(form.get('id',''))))
    audit(kind+'.status',str(form.get('id','')))
    return redirect('/admin/'+kind)

@app.post('/admin/submissions/delete')
async def admin_delete_submission(request:Request):
    require_admin(request)
    form=await request.form();check_csrf(request,str(form.get('csrf','')))
    kind=str(form.get('kind',''))
    if kind not in ('inquiries','applications') or form.get('confirm')!='DELETE':raise HTTPException(422,'Explicit deletion confirmation required')
    require_admin(request,roles=('admin','recruitment') if kind=='applications' else ('admin','marketing'))
    record_id=str(form.get('id',''))
    if kind=='applications':
        application=db.one('SELECT file_path FROM applications WHERE id=?',(record_id,))
        if application:
            path=Path(application['file_path']).resolve()
            if path.parent==UPLOAD_DIR.resolve():path.unlink(missing_ok=True)
    db.execute(f'DELETE FROM {kind} WHERE id=?',(record_id,))
    audit(kind+'.permanently_deleted',record_id)
    return redirect('/admin/'+kind)

@app.get('/admin/cv/{ident}')
async def admin_download_cv(request:Request,ident:str):
    require_admin(request,roles=('admin','recruitment'))
    application=db.one('SELECT filename,file_path FROM applications WHERE id=?',(ident,))
    if not application:raise HTTPException(404)
    p=Path(application['file_path']).resolve()
    if p.parent!=UPLOAD_DIR.resolve() or not p.is_file():raise HTTPException(404)
    audit('applications.cv_download',ident)
    return FileResponse(str(p),filename=application['filename'],media_type='application/octet-stream',headers={'Cache-Control':'no-store','X-Content-Type-Options':'nosniff'})

@app.get('/admin/settings')
async def admin_settings(request:Request):
    require_admin(request,roles=('admin',))
    keys={'site_name':COMPANY,'brand_wordmark':WORDMARK,'contact_email':CONTACT_EMAIL,'contact_phone':CONTACT_PHONE,'linkedin_url':LINKEDIN_URL,'booking_url':BOOKING_URL}
    return admin_render(request,'settings.html',settings={key:setting(key,default) for key,default in keys.items()})

@app.post('/admin/settings')
async def admin_settings_save(request:Request):
    require_admin(request,roles=('admin',))
    form=await request.form();check_csrf(request,str(form.get('csrf','')))
    for key in ('site_name','brand_wordmark','contact_email','contact_phone','linkedin_url','booking_url'):
        value=valid(form.get(key),300)
        if key in ('booking_url','linkedin_url') and value and (urlparse(value).scheme!='https' or not urlparse(value).netloc):
            raise HTTPException(422,'External links must use HTTPS')
        if key=='contact_email' and value and not EMAIL_RE.match(value):raise HTTPException(422,'Invalid contact email address')
        db.execute('INSERT INTO settings(key,value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value',(key,value))
    audit('settings.save')
    return redirect('/admin/settings')

@app.get('/media/{filename}')
async def public_media(filename:str):
    if not re.fullmatch(r'[a-f0-9]{32}\.webp',filename):raise HTTPException(404)
    if not db.one('SELECT id FROM media WHERE file_name=?',(filename,)):raise HTTPException(404)
    location=MEDIA_DIR/filename
    if not location.is_file():raise HTTPException(404)
    return FileResponse(location,media_type='image/webp',headers={'Cache-Control':'public, max-age=3600','X-Content-Type-Options':'nosniff'})

@app.get('/admin/media')
async def admin_media(request:Request):
    require_admin(request,roles=('admin','content','marketing'))
    return admin_render(request,'media.html',media=db.many('SELECT * FROM media ORDER BY created_at DESC'))

@app.post('/admin/media')
async def admin_media_upload(request:Request, image:UploadFile=File(...)):
    require_admin(request,roles=('admin','content','marketing'))
    form=await request.form();check_csrf(request,str(form.get('csrf','')))
    data=await image.read(4*1024*1024+1)
    if len(data)>4*1024*1024:raise HTTPException(422,'Image exceeds 4 MB')
    try:
        Image.MAX_IMAGE_PIXELS=12_000_000
        with Image.open(io.BytesIO(data)) as incoming:
            if incoming.format not in ('JPEG','PNG','WEBP') or incoming.width*incoming.height>12_000_000:
                raise HTTPException(422,'Only valid JPEG, PNG or WEBP images up to 12 megapixels are allowed')
            incoming.load()
            photo=incoming.convert('RGB')
            photo.thumbnail((1800,1800),Image.Resampling.LANCZOS)
            name=uuid.uuid4().hex+'.webp'
            photo.save(MEDIA_DIR/name,'WEBP',quality=83,method=5)
    except (UnidentifiedImageError,OSError,ValueError,Image.DecompressionBombError):
        raise HTTPException(422,'Invalid image file')
    alt=valid(form.get('alt_text'),220)
    db.execute('INSERT INTO media(id,file_name,alt_text,created_at) VALUES(?,?,?,?)',(db.uid(),name,alt,db.now()))
    audit('media.upload',name)
    return redirect('/admin/media')

@app.post('/admin/media/delete')
async def admin_media_delete(request:Request):
    require_admin(request,roles=('admin','content','marketing'))
    form=await request.form();check_csrf(request,str(form.get('csrf','')))
    filename=str(form.get('file_name',''))
    if form.get('confirm')!='DELETE':raise HTTPException(422,'Confirm deletion')
    if db.one('SELECT id FROM articles WHERE cover_image=?',(filename,)):
        raise HTTPException(409,'This image is still used as an article cover')
    record=db.one('SELECT id FROM media WHERE file_name=?',(filename,))
    if not record:raise HTTPException(404)
    db.execute('DELETE FROM media WHERE file_name=?',(filename,))
    if re.fullmatch(r'[a-f0-9]{32}\.webp',filename):(MEDIA_DIR/filename).unlink(missing_ok=True)
    audit('media.delete',filename)
    return redirect('/admin/media')

@app.get('/{locale}/{any_path:path}',response_class=HTMLResponse)
async def pages(request:Request,locale:str,any_path:str):
    if locale not in ('en','de'):raise HTTPException(404)
    path=any_path.strip('/')
    job_prefix=PATHS['jobs'][0 if locale=='en' else 1]+'/'
    insight_prefix=PATHS['insights'][0 if locale=='en' else 1]+'/'
    if path.startswith(job_prefix):
        slug=path[len(job_prefix):]
        j=db.one('SELECT * FROM jobs WHERE slug=? AND published=1',(slug,))
        if not j:raise HTTPException(404)
        return render(request,'job_detail.html',locale,job=j,page_id='jobs',page_title=j['title_'+locale],canonical=SITE_DOMAIN+url(locale,'jobs')+'/'+slug)
    if path.startswith(insight_prefix):
        slug=path[len(insight_prefix):]
        a=db.one('SELECT * FROM articles WHERE slug=? AND published=1',(slug,))
        if not a:raise HTTPException(404)
        return render(request,'article.html',locale,article=a,page_id='insights',page_title=a['title_'+locale],canonical=SITE_DOMAIN+url(locale,'insights')+'/'+slug)
    ident=local_path(locale,path)
    if not ident or ident=='home':raise HTTPException(404)
    base=dict(page_id=ident,canonical=SITE_DOMAIN+url(locale,ident))
    if ident in PAGES[locale]:
        p=get_page(locale,ident)
        return render(request,'landing.html',locale,page=p,page_title=p['title'],services=SERVICES[locale],faqs=FAQS[locale],**base)
    if ident=='jobs': return render(request,'jobs.html',locale,jobs=public_jobs(),page_title=UI[locale]['nav_jobs'],**base)
    if ident=='insights':return render(request,'insights.html',locale,articles=public_articles(),page_title=UI[locale]['nav_insights'],**base)
    if ident=='contact':return render(request,'contact.html',locale,page_title=UI[locale]['nav_contact'],**base)
    if ident=='cases':return render(request,'simple.html',locale,title=('Client stories' if locale=='en' else 'Kundenprojekte'),body=UI[locale]['no_cases'],page_title=('Client stories' if locale=='en' else 'Kundenprojekte'),**base)
    if ident=='faq':return render(request,'faq.html',locale,faqs=FAQS[locale],page_title=UI[locale]['faq_title'] if 'faq_title' in UI[locale] else ('Frequently asked questions' if locale=='en' else 'Häufige Fragen'),**base)
    if ident=='thanks':return render(request,'simple.html',locale,title=UI[locale]['thanks_title'],body=UI[locale]['thanks_body'],page_title=UI[locale]['thanks_title'],**base)
    if ident in LEGAL[locale]:
        page=get_page(locale,ident)
        title,body=page['title'],page['body']
        return render(request,'legal.html',locale,title=title,body=body,page_title=title,**base)
    raise HTTPException(404)


@app.exception_handler(404)
async def notfound(request:Request, exc):
    locale='de' if request.url.path.startswith('/de/') else 'en'
    return render(request,'simple.html',locale,status=404,title=('Page not found' if locale=='en' else 'Seite nicht gefunden'),body=('The page you requested could not be found.' if locale=='en' else 'Die angeforderte Seite wurde nicht gefunden.'),page_title='404',page_id='home')
