"""Small, straightforward SQLite persistence layer for a single-instance deployment.
For multi-instance or serverless deployment, replace with managed PostgreSQL.
"""
import os, sqlite3, uuid, datetime
from pathlib import Path

DB_PATH = os.getenv('DB_PATH', './data/the-link.sqlite3')

def connect():
    path = Path(DB_PATH); path.parent.mkdir(parents=True, exist_ok=True)
    cx = sqlite3.connect(str(path), timeout=15)
    cx.row_factory = sqlite3.Row
    cx.execute('PRAGMA foreign_keys=ON')
    cx.execute('PRAGMA busy_timeout=15000')
    return cx

def init():
    with connect() as db:
        db.execute('PRAGMA journal_mode=WAL')
        db.executescript('''
        CREATE TABLE IF NOT EXISTS inquiries (
          id TEXT PRIMARY KEY, created_at TEXT NOT NULL, kind TEXT NOT NULL,
          name TEXT NOT NULL, company TEXT, email TEXT NOT NULL, phone TEXT,
          country TEXT, service TEXT, role_title TEXT, city TEXT,
          employment_type TEXT, salary TEXT, vacancies TEXT,
          timeline TEXT, website TEXT, budget TEXT, message TEXT,
          status TEXT NOT NULL DEFAULT 'new');
        CREATE TABLE IF NOT EXISTS applications (
          id TEXT PRIMARY KEY, created_at TEXT NOT NULL, name TEXT NOT NULL,
          email TEXT NOT NULL, phone TEXT, country TEXT, linkedin TEXT,
          job_id TEXT, cover_letter TEXT, filename TEXT NOT NULL,
          file_path TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'new');
        CREATE TABLE IF NOT EXISTS jobs (
          id TEXT PRIMARY KEY, slug TEXT UNIQUE NOT NULL, title_en TEXT NOT NULL,
          employer_name TEXT, title_de TEXT NOT NULL, location TEXT NOT NULL, country TEXT NOT NULL,
          category TEXT NOT NULL, employment_type TEXT NOT NULL,
          description_en TEXT NOT NULL, description_de TEXT NOT NULL,
          published INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS articles (
          id TEXT PRIMARY KEY, slug TEXT UNIQUE NOT NULL, category TEXT NOT NULL,
          title_en TEXT NOT NULL, title_de TEXT NOT NULL,
          excerpt_en TEXT NOT NULL, excerpt_de TEXT NOT NULL,
          body_en TEXT NOT NULL, body_de TEXT NOT NULL,
          published INTEGER NOT NULL DEFAULT 0, published_at TEXT NOT NULL, cover_image TEXT);
        CREATE TABLE IF NOT EXISTS media (id TEXT PRIMARY KEY, file_name TEXT UNIQUE NOT NULL, alt_text TEXT NOT NULL, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password_hash TEXT NOT NULL, role TEXT NOT NULL, enabled INTEGER NOT NULL DEFAULT 1);
        CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS admin_audit (
          id TEXT PRIMARY KEY, created_at TEXT NOT NULL, action TEXT NOT NULL,
          record_id TEXT);
        CREATE TABLE IF NOT EXISTS page_overrides (
          locale TEXT NOT NULL, page_id TEXT NOT NULL, field TEXT NOT NULL,
          value TEXT NOT NULL, PRIMARY KEY(locale,page_id,field));
        ''')
        cols=[row[1] for row in db.execute('PRAGMA table_info(jobs)').fetchall()]
        if 'employer_name' not in cols:db.execute('ALTER TABLE jobs ADD COLUMN employer_name TEXT')
        cols_art=[row[1] for row in db.execute('PRAGMA table_info(articles)').fetchall()]
        if 'cover_image' not in cols_art:db.execute('ALTER TABLE articles ADD COLUMN cover_image TEXT')
        if not db.execute('SELECT COUNT(*) FROM articles').fetchone()[0]:
            for a in ARTICLES:
                db.execute('''INSERT INTO articles (id,slug,category,title_en,title_de,excerpt_en,excerpt_de,body_en,body_de,published,published_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)''', (str(uuid.uuid4()), *a))

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def uid(): return str(uuid.uuid4())

def one(sql, args=()):
    with connect() as db:
        r=db.execute(sql,args).fetchone()
        return dict(r) if r else None

def many(sql, args=()):
    with connect() as db: return [dict(row) for row in db.execute(sql,args).fetchall()]

def execute(sql,args=()):
    with connect() as db: db.execute(sql,args)

ARTICLES = [
 ('expanding-to-germany','Market Entry','Entering Germany: Start With the Customer, Not the Office','Markteintritt Deutschland: Beginnen Sie bei Ihren Kunden','A practical sequence for testing a German market opportunity before committing significant resources.','Eine praktische Vorgehensweise, um Marktchancen in Deutschland vor größeren Investitionen zu prüfen.',
  'Start by defining the customer segment you want to reach. A broad market description rarely translates into a useful commercial plan. Write down the buyer, buying problem, likely alternatives and why your offer should matter.\n\nNext, interview potential customers and map competing offers. Keep assumptions separate from findings. Focus on how purchasing decisions are made, what local proof buyers expect and which channels are viable.\n\nOnly then prioritize the route to market: direct outreach, partnerships, digital demand generation or a combination. Set a small number of measurable learning goals for the first 90 days. A useful market-entry plan identifies what must be proven before spending more.',
  'Definieren Sie zuerst die Kundengruppe, die Sie ansprechen möchten. Eine allgemeine Marktbetrachtung ersetzt keinen konkreten Vertriebsplan. Beschreiben Sie Käufer, Problem, Alternativen und Nutzen Ihres Angebots.\n\nSprechen Sie anschließend mit potenziellen Kunden und analysieren Sie Wettbewerber. Trennen Sie Annahmen klar von validierten Erkenntnissen. Entscheidend sind Kaufprozesse, relevante Nachweise und geeignete Kanäle.\n\nErst danach sollten Sie den Marktzugang priorisieren: Direktvertrieb, Partnerschaften, digitale Nachfragegenerierung oder eine Kombination. Legen Sie konkrete Lernziele für die ersten 90 Tage fest.',1,'2026-10-01'),
 ('hiring-german-speaking-talent','Recruitment','Hiring German-Speaking Talent in Ireland','Deutschsprachige Fachkräfte in Irland gewinnen','How to sharpen a multilingual hiring brief, reach candidates and reduce friction during selection.','Wie Sie mehrsprachige Rollen definieren, Kandidaten ansprechen und Auswahlprozesse verbessern.',
  'A good multilingual hiring process begins with role clarity. Separate the language proficiency actually needed for the job from preferences that can unnecessarily narrow the pool. Explain whether communication is customer-facing, internal or technical.\n\nA strong vacancy announcement should be transparent about location, working arrangements and responsibilities. Consider whether candidates are already based in Ireland or whether the role requires relocation. Avoid promises about relocation support unless arrangements are in place.\n\nUse a structured interview process and consistent criteria for all applicants. Coordinate candidate communication promptly and document decisions appropriately. Monitor where qualified candidates drop out, then improve the process rather than simply increasing outreach volume.',
  'Gutes mehrsprachiges Recruiting beginnt mit einem präzisen Rollenprofil. Unterscheiden Sie zwischen tatsächlich erforderlichen Sprachkenntnissen und optionalen Wünschen, die den Kandidatenkreis unnötig einschränken.\n\nDie Stellenanzeige sollte transparent über Arbeitsort, Arbeitsmodell und Aufgaben informieren. Berücksichtigen Sie, ob Bewerbende bereits in Irland leben oder ein Umzug erforderlich wäre.\n\nNutzen Sie strukturierte Gespräche und einheitliche Bewertungskriterien. Achten Sie auf zeitnahe Kommunikation und prüfen Sie, an welchen Stellen qualifizierte Kandidaten aus dem Prozess aussteigen.',1,'2026-09-25'),
 ('localizing-marketing','Marketing','Localization Is More Than Translation','Marketinglokalisierung ist mehr als Übersetzung','Build messages that make sense to your audience rather than simply converting English copy into German.','Entwickeln Sie Botschaften für Ihre Zielgruppe, statt englische Texte nur ins Deutsche zu übertragen.',
  'Translation answers what words mean. Localization asks what the audience expects. Before rewriting your website for a new market, consider which customer problems resonate, which evidence builds credibility and which calls to action are appropriate.\n\nReview page structure, not just text. A headline that performs well in one market may be too vague for another. Localize examples, terminology and contact information. Keep forms short and make the next step obvious.\n\nTest one high-value landing page first. Evaluate relevant inquiries rather than traffic alone, then refine the messaging before applying it site-wide.',
  'Übersetzung beantwortet die Frage nach der Bedeutung von Wörtern. Lokalisierung berücksichtigt Erwartungen der Zielgruppe. Bevor Sie eine Website für einen neuen Markt überarbeiten, prüfen Sie Kundenprobleme, Vertrauensfaktoren und passende Handlungsaufforderungen.\n\nBetrachten Sie nicht nur die Texte, sondern auch Seitenstruktur und Beispiele. Lokalisieren Sie Fachbegriffe, Kontaktdaten und Formulare. Machen Sie den nächsten Schritt für Interessenten eindeutig.\n\nTesten Sie zunächst eine relevante Landingpage und messen Sie qualifizierte Anfragen statt ausschließlich Besucherzahlen.',1,'2026-09-18'),
 ('first-90-days-ireland','Market Entry','Your First 90 Days Exploring Ireland','Die ersten 90 Tage beim Markteintritt in Irland','A focused framework for validating demand and preparing an Irish commercial launch.','Ein strukturierter Ansatz zur Nachfrageprüfung und Vorbereitung des Irlandgeschäfts.',
  'Divide the first 90 days into three practical stages. During discovery, define target customers and interview potential buyers or partners. Record their buying priorities, objections and alternatives.\n\nDuring planning, choose a small number of channels and test your core value proposition. Draft local marketing copy and an initial outreach sequence. Identify whether local hiring or external support is needed.\n\nDuring execution, run limited commercial tests, review qualified conversations and adjust the approach. The goal is not a guaranteed number of sales: it is a more informed decision about the next investment.',
  'Teilen Sie die ersten 90 Tage in drei Phasen. In der Analyse definieren Sie Zielkunden und sprechen mit potenziellen Käufern oder Partnern. Dokumentieren Sie Anforderungen, Einwände und Alternativen.\n\nIn der Planung wählen Sie wenige geeignete Kanäle, testen Ihr Nutzenversprechen und entwickeln erste lokale Marketinginhalte. Prüfen Sie den Personal- und Unterstützungsbedarf.\n\nIn der Umsetzung führen Sie begrenzte Markttests durch, bewerten qualifizierte Gespräche und passen Ihren Ansatz an. Ziel ist eine bessere Investitionsentscheidung, keine garantierte Umsatzzahl.',1,'2026-09-10'),
]
