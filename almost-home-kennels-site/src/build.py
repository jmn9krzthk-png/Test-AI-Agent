"""Build the Almost Home Kennels site.
Outputs:
  preview/  flat .html files with relative links (for the Claude artifact preview)
  dist/     production build: /slug/index.html clean URLs, sitemap.xml, robots.txt, redirects
Run: python3 build.py   (from this folder)
"""
import json, os, re, shutil, html as H

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SITE = os.path.join(ROOT, 'site')          # images + icons live here
BASE = 'https://almosthomekennelsmo.com'
TODAY = '2026-11-20'
PHONE = '636-459-9900'
EMAIL = 'Almosthomekennelsmo1@yahoo.com'
PORTAL = 'https://almosthomekennelsmo.propetware.com'
FB = 'https://www.facebook.com/AlmostHomeKennels'
TOWNS = ['Wright City', 'Warrenton', 'Wentzville', 'Foristell', 'Lake St. Louis', "O'Fallon", 'Innsbrook', 'New Melle', 'Marthasville', 'Truxton', 'Troy']

home_body = open(os.path.join(HERE, 'home_body.html'), encoding='utf-8').read()
SEC = {}
for m in re.finditer(r'  <!-- ([A-Z ]+) -->\n(.*?)(?=\n  <!-- [A-Z ]+ -->|\n</main>)', home_body, re.S):
    SEC[m.group(1)] = m.group(2)
LIGHTBOX = home_body[home_body.index('<div class="lb"'):]
LIGHTBOX = LIGHTBOX[:LIGHTBOX.index('</div>', LIGHTBOX.index('close')) + 6]

# ---------------------------------------------------------------- page registry
# slug: (nav label or None, title tag, meta description, h1-ish name for breadcrumbs)
PAGES = {}
def page(slug, title, desc, crumb, body, schema=None, hero_img=None, gallery=False, noindex=False, parent=None, og=None, ptype='WebPage'):
    PAGES[slug] = dict(title=title, desc=desc, crumb=crumb, body=body, schema=schema or [], hero_img=hero_img,
                       gallery=gallery, noindex=noindex, parent=parent, og=og, ptype=ptype)

NAV = [('pricing-and-services', 'Pricing & Services'), ('new-clients', 'New Clients'), ('about', 'About'),
       ('faq', 'FAQ'), ('contact', 'Contact')]

# ---------------------------------------------------------------- helpers
class Ctx:
    def __init__(self, mode): self.mode = mode
    def link(self, slug):
        if self.mode == 'preview': return 'index.html' if slug == '' else slug + '.html'
        return '/' if slug == '' else '/' + slug + '/'
    def img(self, f): return ('img/' if self.mode == 'preview' else '/img/') + f
    def asset(self, f): return f if self.mode == 'preview' else '/' + f

def canon(slug): return BASE + '/' + (slug + '/' if slug else '')
def esc(s): return H.escape(s, quote=True)

BIZ_ID = BASE + '/#business'
def business():
    return {
        "@type": ["LocalBusiness"], "@id": BIZ_ID, "name": "Almost Home Kennels",
        "alternateName": "Almost Home Kennels MO",
        "description": "Dog boarding and daycare in Wright City, Missouri with supervised outdoor play, quiet rest, baths, nail care and enrichment. Someone lives on site 24/7.",
        "url": BASE + '/', "telephone": "+1-" + PHONE, "email": EMAIL,
        "logo": BASE + '/img/icon-512.png',
        "image": [BASE + '/img/og-almost-home.jpg', BASE + '/img/hero-yard.jpg', BASE + '/img/svc-daycare.jpg'],
        "priceRange": "$36–$47",
        "address": {"@type": "PostalAddress", "addressLocality": "Wright City", "addressRegion": "MO", "postalCode": "63390", "addressCountry": "US"},
        "areaServed": [{"@type": "City", "name": t + ", MO"} for t in TOWNS],
        "sameAs": [FB],
        "knowsAbout": ["Dog boarding", "Dog daycare", "Puppy boarding", "Dog bathing", "Dog nail trimming", "Canine enrichment"],
        "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Dog care services", "itemListElement": [
            offer("Overnight dog boarding", "43.00", "night"), offer("Puppy boarding (8 months & under)", "47.00", "night"),
            offer("Dog daycare", "36.00", "day"), offer("New-client trial day", "36.00", "dog")]},
        "aggregateRating": None,
    }
def offer(name, price, unit):
    return {"@type": "Offer", "itemOffered": {"@type": "Service", "name": name},
            "priceSpecification": {"@type": "UnitPriceSpecification", "price": price, "priceCurrency": "USD", "unitText": unit}}
def service(name, slug, desc, price=None, unit=None, stype=None):
    s = {"@type": "Service", "@id": canon(slug) + '#service', "name": name, "serviceType": stype or name,
         "description": desc, "provider": {"@id": BIZ_ID}, "url": canon(slug),
         "areaServed": [{"@type": "City", "name": t + ", MO"} for t in TOWNS]}
    if price:
        s["offers"] = {"@type": "Offer", "price": price, "priceCurrency": "USD",
                       "priceSpecification": {"@type": "UnitPriceSpecification", "price": price, "priceCurrency": "USD", "unitText": unit},
                       "availability": "https://schema.org/InStock", "url": canon(slug)}
    return s

def jsonld(slug, p):
    graph = []
    b = business(); b.pop('aggregateRating')
    graph.append(b if slug in ('', 'about', 'contact', 'pricing-and-services') else {"@type": "LocalBusiness", "@id": BIZ_ID, "name": "Almost Home Kennels", "url": BASE + '/', "telephone": "+1-" + PHONE})
    if slug == '':
        graph.append({"@type": "WebSite", "@id": BASE + '/#website', "url": BASE + '/', "name": "Almost Home Kennels", "publisher": {"@id": BIZ_ID}, "inLanguage": "en-US"})
    wp = {"@type": 'WebPage' if p['ptype'] in ('FAQPage', 'BlogPosting') else p['ptype'], "@id": canon(slug) + '#webpage', "url": canon(slug), "name": p['title'], "description": p['desc'],
          "isPartOf": {"@id": BASE + '/#website'}, "about": {"@id": BIZ_ID}, "inLanguage": "en-US", "dateModified": TODAY}
    if p['hero_img']: wp["primaryImageOfPage"] = {"@type": "ImageObject", "url": BASE + '/img/' + p['hero_img']}
    graph.append(wp)
    if slug:
        items = [("Home", '')]
        if p['parent']: items.append((PAGES[p['parent']]['crumb'], p['parent']))
        items.append((p['crumb'], slug))
        graph.append({"@type": "BreadcrumbList", "@id": canon(slug) + '#breadcrumb', "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": canon(s)} for i, (n, s) in enumerate(items)]})
    graph.extend(p['schema'])
    return '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + '</script>'

def crumbs(c, slug, p):
    if not slug: return ''
    parts = ['<li><a href="%s">Home</a></li>' % c.link('')]
    if p['parent']: parts.append('<li><a href="%s">%s</a></li>' % (c.link(p['parent']), esc(PAGES[p['parent']]['crumb'])))
    parts.append('<li aria-current="page">%s</li>' % esc(p['crumb']))
    return '<nav class="crumbs wrap" aria-label="Breadcrumb"><ol>%s</ol></nav>' % ''.join(parts)

def header(c, slug):
    cur = slug if slug in dict(NAV) else (PAGES[slug]['parent'] if slug in PAGES and PAGES[slug]['parent'] in dict(NAV) else None)
    links = ''.join('<a class="nl" href="%s"%s>%s</a>' % (c.link(s), ' aria-current="page"' if s == cur else '', esc(l)) for s, l in NAV)
    return f'''<a class="skip" href="#main">Skip to content</a>
<header class="top">
  <div class="wrap">
    <a class="logo" href="{c.link('')}"><img src="{c.img('logo-white.png')}" alt="Almost Home Kennels home" width="620" height="159"></a>
    <button class="menu-btn" id="menuToggle" type="button" aria-expanded="false" aria-controls="siteNav"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>Menu</button>
    <nav id="siteNav" aria-label="Main">
      {links}
      <a class="btn btn-coral" href="{c.link('client-portal')}"{' aria-current="page"' if slug == 'client-portal' else ''}>Client Portal</a>
    </nav>
  </div>
</header>'''

def footer(c):
    L = c.link
    return f'''<footer class="site">
  <div class="wrap">
    <div class="cols">
      <div>
        <img src="{c.img('logo-white.png')}" alt="Almost Home Kennels" width="620" height="159" loading="lazy" style="height:52px;width:auto">
        <address>
          <span>Almost Home Kennels</span>
          <span>Wright City, MO 63390</span>
          <span>Phone: {PHONE}</span>
          <span>{EMAIL}</span>
        </address>
      </div>
      <div><h2>Services</h2><ul>
        <li><a href="{L('dog-boarding-in-wright-city')}">Dog boarding</a></li>
        <li><a href="{L('dog-daycare-wright-city')}">Dog daycare</a></li>
        <li><a href="{L('puppy-boarding')}">Puppy boarding</a></li>
        <li><a href="{L('dog-baths-and-nail-trims')}">Baths &amp; nail trims</a></li>
        <li><a href="{L('dog-enrichment')}">Enrichment</a></li>
        <li><a href="{L('pricing-and-services')}">Pricing</a></li>
      </ul></div>
      <div><h2>Plan your visit</h2><ul>
        <li><a href="{L('new-clients')}">New clients</a></li>
        <li><a href="{L('checklists-and-scheduling')}">Checklists &amp; scheduling</a></li>
        <li><a href="{L('faq')}">FAQ</a></li>
        <li><a href="{L('areas-we-serve')}">Areas we serve</a></li>
        <li><a href="{L('contact')}">Contact</a></li>
      </ul></div>
      <div><h2>Resources</h2><ul>
        <li><a href="{L('helpful-resources')}">Helpful resources</a></li>
        <li><a href="{L('why-routine-matters-for-boarding-dogs')}">Why routine matters</a></li>
        <li><a href="{L('why-rest-is-important-for-dogs-during-their-stay')}">Why rest is important</a></li>
        <li><a href="{L('client-portal')}">Client portal</a></li>
        <li><a href="{FB}" rel="noopener" target="_blank">Facebook</a></li>
      </ul></div>
    </div>
    <div class="base"><small>© 2026 Almost Home Kennels. All rights reserved.</small><small>Dog boarding &amp; daycare in Wright City, Missouri</small></div>
  </div>
</footer>'''

FONTS = 'https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700;12..96,800&family=Figtree:wght@400;500;600;700&display=swap'

def head_tags(c, slug, p):
    url = canon(slug)
    ogimg = BASE + '/img/' + (p['og'] or 'og-almost-home.jpg')
    robots = 'noindex,follow' if p['noindex'] else 'index,follow,max-image-preview:large'
    pre = '<link rel="preload" as="image" href="%s" fetchpriority="high">' % c.img(p['hero_img']) if p['hero_img'] else ''
    return f'''<title>{esc(p['title'])}</title>
<meta name="description" content="{esc(p['desc'])}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#5F7448">
<meta name="geo.region" content="US-MO">
<meta name="geo.placename" content="Wright City">
<meta property="og:type" content="{'article' if p['ptype'] == 'BlogPosting' else 'website'}">
<meta property="og:site_name" content="Almost Home Kennels">
<meta property="og:locale" content="en_US">
<meta property="og:title" content="{esc(p['title'])}">
<meta property="og:description" content="{esc(p['desc'])}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{ogimg}">
<meta property="og:image:alt" content="Dogs playing in the yard at Almost Home Kennels in Wright City, MO">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(p['title'])}">
<meta name="twitter:description" content="{esc(p['desc'])}">
<meta name="twitter:image" content="{ogimg}">
<link rel="icon" type="image/png" href="{c.asset('favicon.png')}">
<link rel="apple-touch-icon" href="{c.asset('apple-touch-icon.png')}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="{c.asset('assets/site.css')}">
{pre}
{jsonld(slug, p)}'''

def render(c, slug):
    p = PAGES[slug]
    body = p['body'](c)
    body = body.replace('src="img/', 'src="' + c.img(''))
    extra = (LIGHTBOX.replace('src=""', 'src="data:,"') if p['gallery'] else '') + '\n<div class="toast" id="ptoast" hidden role="status"></div>' if slug == 'client-portal' else (LIGHTBOX.replace('src=""', 'src="data:,"') if p['gallery'] else '')
    inner = f'''{header(c, slug)}
{crumbs(c, slug, p)}
<main id="main">
{body}
</main>
{footer(c)}
{extra}
<script src="{c.asset('assets/site.js')}" defer></script>'''
    if c.mode == 'preview' and slug == '':
        return '<meta name="claude:viewport-fit-sides" content="cover">\n' + head_tags(c, slug, p) + '\n' + inner + '\n'
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
{head_tags(c, slug, p)}
</head>
<body data-img="{c.img('')}">
{inner}
</body>
</html>
'''

# ---------------------------------------------------------------- shared blocks
def cta_band(c, title='Ready to book a stay?', text='New clients start with a tour and a trial day. Current clients can request dates in the portal.'):
    return f'''<section style="padding-top:0"><div class="wrap"><div class="cta-band">
  <div style="display:grid;gap:10px;max-width:56ch"><h2>{title}</h2><p class="lede">{text}</p></div>
  <div class="cta"><a class="btn btn-green" href="{c.link('new-clients')}">New clients start here</a><a class="btn btn-line" href="{c.link('client-portal')}">Client portal</a></div>
</div></div></section>'''

def page_hero(eyebrow, h1, lede, img=None, alt='', ctas='', tall=False):
    pic = f'<img class="ph-img{" tall" if tall else ""}" src="img/{img}" alt="{esc(alt)}" fetchpriority="high">' if img else ''
    return f'''<section class="page-hero{'' if img else ' solo'}"><div class="wrap">
  <div><span class="eyebrow">{eyebrow}</span><h1>{h1}</h1><p class="lede">{lede}</p>{('<div class="cta">' + ctas + '</div>') if ctas else ''}</div>
  {pic}
</div></section>'''

def services_section(c, heading=True):
    s = SEC['SERVICES']
    links = {'boarding': c.link('dog-boarding-in-wright-city'), 'daycare': c.link('dog-daycare-wright-city'), 'baths': c.link('dog-baths-and-nail-trims'),
             'enrichment': c.link('dog-enrichment'), 'newclients': c.link('new-clients')}
    s = s.replace('id="svcTabs"></div>', "id=\"svcTabs\" data-links='%s'></div>" % json.dumps(links))
    s = s.replace('<p class="small" id="svcNote"></p>', '<p class="small" id="svcNote"></p>\n          <a class="more-link" id="svcMore" href="%s">More about overnight boarding →</a>' % links['boarding'])
    if not heading:
        s = re.sub(r'<div class="head">.*?</div>\s*', '', s, count=1, flags=re.S)
    return s

def estimator(c):
    return SEC['ESTIMATOR'].replace('<div class="est-grid">', '<div class="est-grid" id="estimate-tool">').replace('href="https://almosthomekennelsmo.propetware.com"', 'href="%s"' % c.link('client-portal'))

def gallery(only=None, limit=None, filters=True, eyebrow='Life at Almost Home', title='Fresh air, happy play, good naps', lede='Real dogs, real days. Tap any photo to see it bigger.'):
    s = SEC['GALLERY']
    s = s.replace('<span class="eyebrow">Life at Almost Home</span>', '<span class="eyebrow">%s</span>' % eyebrow)
    s = s.replace('<h2>Fresh air, happy play, good naps</h2>', '<h2>%s</h2>' % title)
    s = s.replace('<p class="lede">Real dogs, real days. Tap any photo to see it bigger.</p>', '<p class="lede">%s</p>' % lede)
    attrs = (' data-only="%s"' % only if only else '') + (' data-limit="%d"' % limit if limit else '')
    s = s.replace('<div class="masonry" id="gal"></div>', '<div class="masonry" id="gal"%s></div>' % attrs)
    if not filters:
        s = re.sub(r'<div class="filters" id="galFilters">.*?</div>\s*', '', s, flags=re.S)
    return s

def contact_band(c):
    return SEC['CONTACT'].replace('href="https://almosthomekennelsmo.propetware.com" target="_blank" rel="noopener">Open client portal',
                                  'href="%s">Open client portal' % c.link('client-portal')).replace('href="#new-clients"', 'href="%s"' % c.link('new-clients'))

FAQ = [
    ('Getting started', 'How do I become a new client?', 'Begin by creating an account in our online client portal and completing your dog’s information. Our team will contact you to learn more about your dog and help schedule the required tour and trial day. Dogs must complete the new-client process before booking regular daycare or boarding.'),
    ('Getting started', 'Does every dog need a trial day, and what happens during it?', 'Yes. Every new dog must complete at least one trial day, sometimes multiple trial days and some overnights, before attending regular daycare or boarding. Your dog will meet our team, get familiar with the facility and routine, enjoy supervised play, and experience appropriate rest and kennel time.'),
    ('Getting started', 'Does my dog need to be friendly with other dogs and comfortable in a kennel?', 'Yes. Dogs attending Almost Home must be comfortable around other dogs and able to rest safely in their kennel space. The required trial day helps us confirm that your dog is comfortable with our group environment and daily routine.'),
    ('Getting started', 'Can I tour the facility before booking?', 'Yes. A scheduled facility tour is part of our new-client process and must be completed before regular daycare or boarding reservations. After you create your online client account, our team will help arrange your tour and trial day.'),
    ('Reservations', 'How do I make a reservation?', 'Current clients can submit reservation requests through our online client portal. Please wait for confirmation from our team before considering your dog’s stay officially booked. New clients must complete the required tour and trial day first.'),
    ('Reservations', 'How far in advance should I book?', 'As early as possible, especially for weekends, holidays, school breaks and other busy travel dates. Space is limited, and submitting a request does not guarantee availability until our team confirms it.'),
    ('Reservations', 'Why are scheduled drop-off and pickup times required?', 'We schedule every drop-off and pickup so our small team can be ready for your arrival while keeping the dogs’ meals, rest, play and care routines running smoothly. Please arrive during your confirmed appointment window and contact us if your plans change.'),
    ('Reservations', 'What happens if I am arriving early or running late?', 'Please contact us as soon as you know your arrival time may change. Because all drop-offs and pickups are scheduled, we may need to arrange a different time. Please don’t arrive outside your confirmed window without speaking with our team first.'),
    ('Reservations', 'What are your cancellation, no-show, and holiday policies?', 'Boarding cancellations made less than 48 hours before arrival may be charged one night’s boarding rate. Daycare and grooming cancellations made less than 24 hours in advance may be charged the full cost. No-shows are charged the full service rate. A nonrefundable $50 deposit may be required for major-holiday reservations.'),
    ('Preparing', 'What should I bring, and do I need to provide food?', 'Bring enough of your dog’s regular food for the entire stay, with clear feeding instructions. Keeping your dog on their usual diet helps prevent stomach upset. Dogs should arrive on a leash with a secure collar or harness.'),
    ('Preparing', 'Can I bring bedding, toys, or comfort items?', 'We prefer to use our own bedding. If you bring it, make sure it is clean, washable and clearly labeled. Please leave toys and chews at home unless our team specifically approves them.'),
    ('Preparing', 'Can you administer my dog’s medication?', 'We can accommodate many routine medications when they are arranged with our team in advance. Provide each medication separately with your dog’s name, dosage, timing and clear written instructions.'),
    ('Daily life', 'What does my dog do throughout the day?', 'Dogs enjoy plenty of supervised outdoor play, movement, fresh air and time with our care team. Meals, individual needs and rest breaks are worked into the routine so each dog has a balanced day of activity and relaxation.'),
    ('Daily life', 'Where does my dog rest and sleep?', 'Each dog has a clean, comfortable space inside our temperature-controlled buildings for meals, rest breaks and overnight sleep.'),
    ('Daily life', 'Will I receive updates during my dog’s stay?', 'You’re welcome to check in with us during your dog’s stay. Clients who would like photos sent directly to them can purchase our photo update add-on when booking. We will always contact you if we have a concern about your dog.'),
    ('Daily life', 'Is someone on the property overnight?', 'Yes. Our kennel manager lives on the property, so someone is onsite overnight. Dogs settle into their individual accommodations for sleep and are not continuously monitored every moment, but having someone on the property provides added peace of mind.'),
    ('Health & safety', 'What vaccinations are required?', 'All dogs must be current on Rabies, Bordetella, and their Distemper/Parvo booster before attending daycare or boarding. Proof of current vaccinations must be provided before your dog’s scheduled visit.'),
    ('Health & safety', 'What is kennel cough?', 'Kennel cough is a general term for contagious respiratory infections that can spread anywhere dogs gather. Symptoms may include a dry cough, sneezing or nasal discharge. Vaccination and cleaning reduce the risk but can’t prevent every case.'),
    ('Health & safety', 'What happens if my dog becomes sick or injured?', 'We will assess your dog, separate them from group activity when appropriate, and contact you or your emergency contact. We’ll keep monitoring and seek veterinary care if we believe it’s necessary.'),
    ('Extras', 'Do you offer full service grooming?', 'We don’t offer full-service haircuts or breed-specific grooming. We do offer baths and nail care that can be added to your dog’s daycare or boarding reservation.'),
    ('Extras', 'What enrichment activities can I add to my dog’s stay?', 'Optional enrichment gives your dog extra individual attention and mental stimulation: snuffle mats, food puzzles, lick mats, stuffed toys, or other activities selected for your dog.'),
]
HOME_FAQ = [0, 4, 8, 16, 15, 19]

def faq_block(items, search=True, cats=True):
    out = []
    if search:
        out.append('<div class="faq-tools"><label for="faqQ" class="small" style="font-weight:700">Search the FAQ</label>'
                   '<input type="search" id="faqQ" placeholder="Try “vaccines”, “cancel” or “medication”" style="max-width:520px">')
        if cats:
            cs = ['All'] + list(dict.fromkeys(FAQ[i][0] for i in items))
            out.append('<div class="filters" id="faqCats" style="margin:0">' + ''.join(
                '<button type="button" class="chip" data-cat="%s" aria-pressed="%s">%s</button>' % (esc(x), 'true' if x == 'All' else 'false', esc(x)) for x in cs) + '</div>')
        out.append('</div>')
    out.append('<div class="faq-list" id="faqList">' + ''.join(
        '<details data-cat="%s"><summary>%s</summary><p>%s</p></details>' % (esc(FAQ[i][0]), esc(FAQ[i][1]), esc(FAQ[i][2])) for i in items) + '</div>')
    if search: out.append('<p class="faq-empty" id="faqEmpty" hidden>No questions match that search. Call us at %s and we’ll help.</p>' % PHONE)
    return ''.join(out)

def faq_schema(items):
    return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": FAQ[i][1], "acceptedAnswer": {"@type": "Answer", "text": FAQ[i][2]}} for i in items]}

def mini_faq(c, items, title='Common questions'):
    return f'''<section style="padding-top:0"><div class="wrap">
  <div class="head"><span class="eyebrow">FAQ</span><h2>{title}</h2></div>
  {faq_block(items, search=False)}
  <p style="margin-top:18px"><a class="more-link" href="{c.link('faq')}">See all questions →</a></p>
</div></section>'''

# ---------------------------------------------------------------- pages
def p_home(c):
    hero = SEC['HERO'].replace('href="#new-clients"', 'href="%s"' % c.link('new-clients'))
    hero = hero.replace('<img class="main"', '<img class="main" fetchpriority="high"')
    faq = f'''<section id="faq" style="padding-top:0"><div class="wrap">
  <div class="head"><span class="eyebrow">FAQ</span><h2>Questions? We've got answers.</h2></div>
  {faq_block(HOME_FAQ, cats=False)}
  <p style="margin-top:18px"><a class="more-link" href="{c.link('faq')}">See all {len(FAQ)} questions →</a></p>
</div></section>'''
    explore = f'''<section style="padding-top:0"><div class="wrap">
  <div class="head"><span class="eyebrow">Explore</span><h2>Everything your dog needs while you're away</h2></div>
  <div class="cards">
    <a class="card photo-card" href="{c.link('dog-boarding-in-wright-city')}"><img src="img/boarding-6457.jpg" alt="A dog resting comfortably in its boarding space" loading="lazy"><div class="in"><h3>Dog boarding</h3><p>Overnight stays from $43 a night with play, rest and attentive care.</p><span class="go">Learn more →</span></div></a>
    <a class="card photo-card" href="{c.link('dog-daycare-wright-city')}"><img src="img/svc-daycare.jpg" alt="Dogs playing in the shaded yard with a team member" loading="lazy"><div class="in"><h3>Dog daycare</h3><p>A full day of supervised group play for $36.</p><span class="go">Learn more →</span></div></a>
    <a class="card photo-card" href="{c.link('puppy-boarding')}"><img src="img/g-6322.jpg" alt="A puppy holding a stuffed toy" loading="lazy" style="object-position:50% 30%"><div class="in"><h3>Puppy boarding</h3><p>Pups 4 months and up, $47 a night through 8 months.</p><span class="go">Learn more →</span></div></a>
  </div>
</div></section>'''
    return hero + services_section(c) + estimator(c) + explore + gallery() + SEC['TEAM'] + SEC['QUOTE'] + faq + contact_band(c)

page('', 'Dog Boarding & Daycare, Wright City MO | Almost Home Kennels',
     'Dog boarding from $43/night and daycare for $36/day in Wright City, MO. Supervised outdoor play, quiet rest, baths, nail care and someone on site 24/7.',
     'Home', p_home, schema=[faq_schema(HOME_FAQ)], hero_img='hero-yard.jpg', gallery=True)

def p_pricing(c):
    tiles = '''<div class="price-row">
  <div class="price-tile"><span>Overnight boarding</span><b>$43</b><span>per night</span></div>
  <div class="price-tile"><span>Puppy boarding (8 months &amp; under)</span><b>$47</b><span>per night</span></div>
  <div class="price-tile"><span>Daycare</span><b>$36</b><span>per day</span></div>
  <div class="price-tile"><span>New-client trial day</span><b>$36</b><span>per dog</span></div>
</div>
<p class="small" style="margin-top:14px">Pick up by 12 PM on your last day for no extra charge. Baths, nail care, enrichment and photo updates are add-ons priced when you book. A nonrefundable $50 deposit may be required for major holidays.</p>'''
    return (page_hero('Pricing &amp; services', 'Dog boarding &amp; daycare pricing in Wright City, MO',
                      'Thoughtful care is already part of every visit. Supervised play and rest, feeding and medication management are included. Add a bath or enrichment to make it even better.',
                      'svc-daycare.jpg', 'A team member at a picnic table in the shaded play yard with several dogs',
                      f'<a class="btn btn-green" href="#estimate">Estimate a stay</a><a class="btn btn-line" href="{c.link("client-portal")}">Client portal</a>')
            + '<section style="padding-top:0"><div class="wrap">' + tiles + '</div></section>'
            + services_section(c) + estimator(c)
            + mini_faq(c, [8, 4, 19, 20], 'Pricing &amp; booking questions') + cta_band(c))
page('pricing-and-services', 'Dog Boarding & Daycare Prices | Almost Home Kennels',
     'Overnight dog boarding $43/night, puppies $47/night, daycare $36/day and trial days $36 in Wright City, MO. Add baths, nail trims and enrichment.',
     'Pricing & Services', p_pricing, hero_img='svc-daycare.jpg', schema=[faq_schema([8, 4, 19, 20])])

def p_boarding(c):
    return (page_hero('Dog boarding in Wright City, MO', 'A comfortable stay while you’re away',
                      'Thoughtful overnight care with supervised play, restful downtime, feeding, medication management and plenty of attention.',
                      'boarding-6457.jpg', 'A dog resting comfortably in its boarding space at Almost Home Kennels',
                      f'<a class="btn btn-green" href="{c.link("new-clients")}">Start here</a><a class="btn btn-line" href="#estimate">Estimate your stay</a>', tall=True)
            + '''<section style="padding-top:0"><div class="wrap">
  <div class="head"><span class="eyebrow">Why families choose Almost Home</span><h2>Boarding that feels more like home</h2>
  <p class="lede">We keep care simple, thoughtful and personal so dogs can settle in, enjoy their stay and get the attention they need while you’re away.</p></div>
  <div class="cards">
    <div class="card"><h3>Thoughtful care</h3><p>Feeding on your dog’s usual schedule, medications given as instructed, and individual attention.</p></div>
    <div class="card"><h3>Supervised play</h3><p>Safe, social time outdoors in appropriate groups, whenever the weather allows.</p></div>
    <div class="card"><h3>Rest &amp; routine</h3><p>Comfortable downtime between activities in our temperature-controlled buildings.</p></div>
    <div class="card"><h3>Someone on site 24/7</h3><p>Our kennel manager lives on the property, so someone is here day and night.</p></div>
  </div>
</div></section>
<section style="padding-top:0"><div class="wrap"><div class="price-row">
  <div class="price-tile"><span>Overnight boarding</span><b>$43</b><span>per night</span></div>
  <div class="price-tile"><span>Puppies 8 months &amp; under</span><b>$47</b><span>per night</span></div>
  <div class="price-tile"><span>Pick-up by 12 PM</span><b>$0</b><span>no charge for your last day</span></div>
</div></div></section>'''
            + estimator(c)
            + f'''<section><div class="wrap split">
  <img src="img/g-6544.jpg" alt="Two dogs napping on a daybed by a sunny window" loading="lazy">
  <div class="prose"><span class="eyebrow">A day in the life</span><h2>Play, eat, enrich, rest</h2>
  <p>Our routine gives boarding dogs something familiar to rely on: regularly scheduled outdoor time, consistent meal times, rest time to decompress, and optional enrichment or one-on-one time.</p>
  <p>Every dog is different. A young, energetic dog may need more activity, while a senior dog may benefit from more rest. We pay attention to how each dog eats, rests, plays and settles.</p>
  <p><a class="more-link" href="{c.link('why-routine-matters-for-boarding-dogs')}">Why routine matters for boarding dogs →</a></p></div>
</div></section>'''
            + mini_faq(c, [15, 13, 11, 9], 'Boarding questions') + cta_band(c))
page('dog-boarding-in-wright-city', 'Dog Boarding in Wright City, MO | Almost Home Kennels',
     'Overnight dog boarding in Wright City, MO for $43/night: supervised outdoor play, rest in temperature-controlled buildings, and someone on site 24/7.',
     'Dog Boarding', p_boarding, hero_img='boarding-6457.jpg', parent='pricing-and-services',
     schema=[service('Overnight dog boarding', 'dog-boarding-in-wright-city', 'Overnight dog boarding with supervised play, rest, feeding and medication management in Wright City, MO.', '43.00', 'night', 'Dog boarding'), faq_schema([15, 13, 11, 9])])

def p_daycare(c):
    return (page_hero('Dog daycare in Wright City, MO', 'A full day of play. A tired, happy dog.',
                      'Supervised group play, fresh air and rest breaks for social dogs. $36 per day.',
                      'svc-daycare.jpg', 'A team member at a picnic table in the shaded play yard with several dogs',
                      f'<a class="btn btn-green" href="{c.link("new-clients")}">Book a trial day</a><a class="btn btn-line" href="{c.link("client-portal")}">Client portal</a>')
            + '''<section style="padding-top:0"><div class="wrap">
  <div class="head"><span class="eyebrow">What daycare includes</span><h2>Structured play with plenty of rest</h2></div>
  <div class="cards">
    <div class="card"><h3>Outdoor group play</h3><p>Our outdoor areas give dogs room to move, explore, socialize and enjoy fresh air whenever the weather allows.</p></div>
    <div class="card"><h3>Balanced with rest</h3><p>Play is balanced with breaks so dogs don’t get overstimulated and can recharge.</p></div>
    <div class="card"><h3>Familiar faces</h3><p>A small team that learns your dog’s personality, routines, preferences and comfort level.</p></div>
    <div class="card"><h3>Add a bath before pick-up</h3><p>Baths, nail trims and enrichment can be added to any daycare day.</p></div>
  </div>
</div></section>
<section style="padding-top:0"><div class="wrap"><div class="price-row">
  <div class="price-tile"><span>Daycare</span><b>$36</b><span>per day</span></div>
  <div class="price-tile"><span>Trial day (required first)</span><b>$36</b><span>per dog</span></div>
</div></div></section>'''
            + gallery(only='play,people', limit=12, filters=False, eyebrow='Daycare at Almost Home', title='Out in the yard', lede='A look at play time. Tap any photo to see it bigger.')
            + f'''<section style="padding-top:0"><div class="wrap">
  <div class="head"><span class="eyebrow">Is daycare right for your dog?</span><h2>What we look for in group play</h2>
  <p class="lede">Daycare works best for dogs who enjoy other dogs. Every new dog starts with a trial day so we can see how they play, rest and settle.</p></div>
  {re.search(r'<div class="expect">.*?</ul></div>\s*</div>', SEC['NEW CLIENTS'], re.S).group(0)}
</div></section>'''
            + mini_faq(c, [12, 1, 2], 'Daycare questions') + cta_band(c))
page('dog-daycare-wright-city', 'Dog Daycare in Wright City, MO | Almost Home Kennels',
     'Dog daycare in Wright City, MO: a full day of supervised outdoor group play and rest breaks for $36. Every new dog starts with a trial day.',
     'Dog Daycare', p_daycare, hero_img='svc-daycare.jpg', parent='pricing-and-services', gallery=True,
     schema=[service('Dog daycare', 'dog-daycare-wright-city', 'Full day of supervised outdoor group play and rest for dogs in Wright City, MO.', '36.00', 'day', 'Dog daycare'), faq_schema([12, 1, 2])])

def p_puppy(c):
    return (page_hero('Puppy boarding &amp; daycare', 'Boarding and daycare for puppies',
                      'Puppies 4 months and older are welcome once they’re up to date on their puppy vaccines. Puppy boarding is $47 a night through 8 months of age.',
                      'g-6322.jpg', 'A black puppy lying on the floor with a stuffed toy',
                      f'<a class="btn btn-green" href="{c.link("new-clients")}">Book a trial day</a>', tall=True)
            + '''<section style="padding-top:0"><div class="wrap">
  <div class="head"><span class="eyebrow">Puppy requirements</span><h2>What your puppy needs first</h2></div>
  <div class="cards">
    <div class="card"><h3>At least 4 months old</h3><p>And up to date on puppy vaccines: Rabies, DHPP (Distemper/Parvo) and Bordetella, with proof before drop-off.</p></div>
    <div class="card"><h3>Spay or neuter by 8 months</h3><p>Dogs over 8 months of age must be spayed or neutered to attend.</p></div>
    <div class="card"><h3>A trial day first</h3><p>A full day of daycare so we can see how your pup plays, rests and settles in a kennel.</p></div>
    <div class="card"><h3>Comfortable with dogs &amp; people</h3><p>Puppies should be friendly and able to rest in a kennel or suite when needed.</p></div>
  </div>
</div></section>
<section style="padding-top:0"><div class="wrap"><div class="price-row">
  <div class="price-tile"><span>Puppy boarding (8 months &amp; under)</span><b>$47</b><span>per night</span></div>
  <div class="price-tile"><span>Daycare</span><b>$36</b><span>per day</span></div>
  <div class="price-tile"><span>Trial day</span><b>$36</b><span>per dog</span></div>
</div></div></section>'''
            + f'''<section><div class="wrap split">
  <div class="prose"><span class="eyebrow">Why rest matters for pups</span><h2>Play, then a good nap</h2>
  <p>Even dogs that love playing can become tired or overwhelmed by too much activity. Scheduled rest gives each dog time to relax before returning to play. Age, personality and normal routines all affect how much rest a dog needs, and young dogs often need more than you’d think.</p>
  <p><a class="more-link" href="{c.link('why-rest-is-important-for-dogs-during-their-stay')}">Why rest is important during a stay →</a></p></div>
  <img src="img/g-6466.jpg" alt="A beagle resting on a cozy bed with a chew toy" loading="lazy">
</div></section>'''
            + mini_faq(c, [16, 1, 2], 'Puppy questions') + cta_band(c, 'Ready for your puppy’s first visit?'))
page('puppy-boarding', 'Puppy Boarding in Wright City, MO | Almost Home Kennels',
     'Puppy boarding in Wright City, MO for pups 4 months and older: $47/night through 8 months. Vaccine and trial-day requirements explained.',
     'Puppy Boarding', p_puppy, hero_img='g-6322.jpg', parent='pricing-and-services',
     schema=[service('Puppy boarding', 'puppy-boarding', 'Overnight boarding for puppies 4 to 8 months old in Wright City, MO.', '47.00', 'night', 'Puppy boarding'), faq_schema([16, 1, 2])])

def p_baths(c):
    return (page_hero('Baths &amp; nail care', 'Dog baths and nail trims in Wright City, MO',
                      'Send them home fresh. Add a bath, nail trim or nail grind to any daycare day or boarding stay.',
                      'svc-bath.jpg', 'A black Lab standing happily in the bathing tub',
                      f'<a class="btn btn-green" href="{c.link("client-portal")}">Add to a reservation</a>')
            + '''<section style="padding-top:0"><div class="wrap">
  <div class="cards">
    <div class="card"><h3>Baths</h3><p>A bath before pick-up so your dog comes home clean after their stay.</p></div>
    <div class="card"><h3>Nail trims</h3><p>Quick, careful clipping to keep nails at a comfortable length.</p></div>
    <div class="card"><h3>Nail grinding</h3><p>A smoother finish for dogs who do well with a grinder.</p></div>
  </div>
  <p class="lede" style="margin-top:28px">Please schedule these services in advance so our team can confirm availability and have your dog ready for pick-up. We don’t offer full-service haircuts or breed-specific grooming.</p>
</div></section>'''
            + mini_faq(c, [19, 8], 'Bath &amp; nail questions') + cta_band(c))
page('dog-baths-and-nail-trims', 'Dog Baths & Nail Trims, Wright City MO | Almost Home Kennels',
     'Add a dog bath, nail trim or nail grind to any daycare or boarding reservation at Almost Home Kennels in Wright City, MO.',
     'Baths & Nail Care', p_baths, hero_img='svc-bath.jpg', parent='pricing-and-services',
     schema=[service('Dog baths and nail trims', 'dog-baths-and-nail-trims', 'Dog baths, nail trims and nail grinding as add-ons to daycare or boarding.', stype='Dog bathing and nail care'), faq_schema([19, 8])])

def p_enrich(c):
    return (page_hero('Enrichment', 'Enrichment &amp; one-on-one time for dogs',
                      'Optional enrichment gives your dog extra individual attention, mental stimulation, and engaging ways to use their natural instincts.',
                      'svc-enrich.jpg', 'A spotted dog solving a treat puzzle toy',
                      f'<a class="btn btn-green" href="{c.link("client-portal")}">Add to a reservation</a>', tall=True)
            + '''<section style="padding-top:0"><div class="wrap">
  <div class="cards">
    <div class="card"><h3>Snuffle mats</h3><p>Sniffing out hidden kibble taps into a dog’s natural foraging instinct.</p></div>
    <div class="card"><h3>Food puzzles</h3><p>Problem-solving fun that slows down eating and keeps minds busy.</p></div>
    <div class="card"><h3>Lick mats &amp; stuffed toys</h3><p>Calming, focused activities that help dogs settle and relax.</p></div>
    <div class="card"><h3>One-on-one time</h3><p>Individual attention with our team, chosen for your dog.</p></div>
    <div class="card"><h3>Photo updates</h3><p>Want pictures during the stay? Add photo updates when you book.</p></div>
  </div>
</div></section>'''
            + gallery(only='enrich', filters=False, eyebrow='Enrichment in action', title='Busy brains, happy dogs', lede='Tap any photo to see it bigger.')
            + mini_faq(c, [20, 14], 'Enrichment questions') + cta_band(c))
page('dog-enrichment', 'Dog Enrichment & One-on-One Care | Almost Home Kennels',
     'Add enrichment to your dog’s stay: snuffle mats, food puzzles, lick mats, stuffed toys and one-on-one time with our team in Wright City, MO.',
     'Enrichment', p_enrich, hero_img='svc-enrich.jpg', parent='pricing-and-services', gallery=True,
     schema=[service('Dog enrichment', 'dog-enrichment', 'Enrichment activities and one-on-one time for dogs during daycare or boarding.', stype='Canine enrichment'), faq_schema([20, 14])])

def p_new(c):
    nc = SEC['NEW CLIENTS'].replace('<h2>We\'re so excited to meet your dog</h2>', '<h2>Four steps to your first stay</h2>')
    nc = re.sub(r'<span class="eyebrow">New clients</span>\s*', '<span class="eyebrow">How it works</span>', nc, count=1)
    return (page_hero('New clients', 'We’re so excited to meet you and your dog',
                      'To keep every dog safe, comfortable and happy, all new guests complete a tour and at least one full-day trial day before regular daycare or boarding.',
                      'svc-trial.jpg', 'A papillon sitting in a colorful ball pit',
                      ('' if c.mode == 'preview' else f'<a class="btn btn-coral" href="{PORTAL}" target="_blank" rel="noopener">New client registration</a>') + f'<a class="btn btn-line" href="{c.link("faq")}">FAQs</a>', tall=True)
            + nc
            + '''<section><div class="wrap split">
  <div class="prose"><span class="eyebrow">Our promise</span><h2>Your dog’s comfort comes first</h2>
  <p>Every dog is different. Some are outgoing, some are cautious, some settle in quickly, and some need a little more time. We pay attention to those differences and do our best to understand what each dog is telling us.</p>
  <p>Our priority is always to do what is best for your dog. That means being honest with you about how they’re doing here, whether it’s their first trial day or their twentieth stay.</p></div>
  <img src="img/g-1167.jpg" alt="A team member giving a dog one-on-one time in the yard" loading="lazy">
</div></section>'''
            + mini_faq(c, [0, 1, 3, 16], 'New client questions') + cta_band(c, 'Ready to get started?', 'Create your account in our client portal. Once we receive your registration, our team will reach out to help schedule your dog’s trial day.'))
page('new-clients', 'New Clients: Tour & Trial Day | Almost Home Kennels',
     'New to Almost Home Kennels? See vaccine and age requirements, check if your dog is a good fit, and pick a trial day (Mon, Wed, Thu, Fri, $36).',
     'New Clients', p_new, hero_img='svc-trial.jpg', schema=[faq_schema([0, 1, 3, 16])])

def p_about(c):
    apart = [('A small, familiar team', 'Your dog is cared for by familiar people who take the time to learn their personality, routines, preferences and comfort level.'),
             ('Space to play', 'Our outdoor areas give dogs room to move, explore, socialize and enjoy fresh air whenever the weather allows.'),
             ('Comfortable accommodations', 'Each dog has a clean, comfortable space to eat, sleep and relax between playtimes.'),
             ('Care shaped around your dog', 'We pay attention to how each dog eats, rests, plays, interacts and settles so we can respond to their individual needs.'),
             ('Familiar food, consistent routine', 'Dogs eat the food provided from home and follow their usual feeding instructions.'),
             ('Someone on site 24/7', 'A member of our care team lives on the property, so someone is onsite day and night.'),
             ('A licensed facility', 'Almost Home maintains the required licensing and follows established standards for cleanliness, care and safety.'),
             ('Enrichment beyond play', 'Optional enrichment provides extra mental stimulation, individual attention and engaging ways to use natural instincts.')]
    cards = ''.join('<div class="card"><h3>%s</h3><p>%s</p></div>' % (esc(a), esc(b)) for a, b in apart)
    return (page_hero('About Almost Home', 'Care that feels like home',
                      'A peaceful, personal place in Wright City, MO where your dog is known, understood, and genuinely cared for.',
                      'team-group.jpg', 'The Almost Home Kennels care team with dogs in the yard',
                      f'<a class="btn btn-green" href="{c.link("new-clients")}">New clients start here</a>')
            + f'<section style="padding-top:0"><div class="wrap"><div class="head"><span class="eyebrow">What sets us apart</span><h2>Why families choose us</h2></div><div class="cards">{cards}</div></div></section>'
            + SEC['TEAM'] + SEC['QUOTE'] + gallery() + cta_band(c))
page('about', 'About Our Team | Almost Home Kennels, Wright City MO',
     'Meet Addy, Olivia, Jim and Carrie, the small team behind Almost Home Kennels in Wright City, MO. Licensed facility with someone on site 24/7.',
     'About', p_about, hero_img='team-group.jpg', gallery=True, ptype='AboutPage')

def p_faq(c):
    return (page_hero('Frequently asked questions', 'Questions? We’ve got answers.',
                      'Everything you need to know about preparing for your dog’s time at Almost Home. Search or filter by topic.')
            + '<section style="padding-top:0"><div class="wrap">' + faq_block(list(range(len(FAQ)))) + '</div></section>' + cta_band(c, 'Still have a question?', 'Call or text us at %s. We’re happy to help.' % PHONE))
page('faq', 'Dog Boarding & Daycare FAQ | Almost Home Kennels',
     'Answers about vaccines, trial days, reservations, cancellations, medications, overnight supervision and add-ons at Almost Home Kennels in Wright City, MO.',
     'FAQ', p_faq, schema=[faq_schema(list(range(len(FAQ))))], ptype='FAQPage')

def p_check(c):
    return (page_hero('Checklists &amp; scheduling', 'Everything you need for a smooth stay',
                      'Simple checklists, scheduling details and helpful reminders so you and your dog arrive prepared.',
                      'g-6427.jpg', 'A poodle mix relaxing on a raised cot', f'<a class="btn btn-green" href="{c.link("client-portal")}">Client portal</a>', tall=True)
            + '''<section style="padding-top:0"><div class="wrap">
  <div class="head"><span class="eyebrow">Drop-off &amp; pick-up</span><h2>Scheduled times keep the day running smoothly</h2>
  <p class="lede">Every arrival and departure is scheduled so our small team can be ready for you without disrupting the dogs’ meals, rest, play and care routines.</p></div>
  <div class="cards">
    <div class="card"><h3>Confirm your time</h3><p>Arrive only during your scheduled drop-off or pick-up window.</p></div>
    <div class="card"><h3>Tell us about changes</h3><p>Let our team know as soon as possible if you will be early or late.</p></div>
    <div class="card"><h3>Arrive safely</h3><p>Bring your dog on a leash with a secure collar or harness.</p></div>
  </div>
</div></section>''' + SEC['PACKING CHECKLIST'] + cta_band(c))
page('checklists-and-scheduling', 'Boarding Checklist & Scheduling | Almost Home Kennels',
     'Interactive packing checklist and drop-off/pick-up scheduling details for your dog’s daycare or boarding stay at Almost Home Kennels in Wright City, MO.',
     'Checklists & Scheduling', p_check, hero_img='g-6427.jpg')

POSTS = [
    dict(slug='why-routine-matters-for-boarding-dogs', title='Why Routine Matters for Boarding Dogs', date='2026-10-10', nice='October 10, 2026', author='Addy Phelps', img='g-6597.jpg',
         alt='An Australian Shepherd sitting on a tree stump in the yard',
         excerpt='For many dogs, staying somewhere new can be a pretty big change. A consistent routine helps boarding feel more predictable and comfortable.',
         body='''<p>For many dogs, staying somewhere new can be a pretty big change. They’re sleeping somewhere different, surrounded by unfamiliar smells and sounds, and their usual people aren’t there. Although we can’t completely eliminate that change, maintaining a consistent routine can help make boarding feel more predictable and comfortable.</p>
<h2>Dogs thrive on predictability</h2>
<p>Dogs don’t necessarily need everything to happen at the same exact time every day, but they do tend to benefit from knowing what comes next. At home, your dog probably has a familiar rhythm. When they board, that routine is interrupted. Establishing a predictable routine at Almost Home Kennels gives them something familiar to rely on.</p>
<h2>What our routine entails</h2>
<ul><li>Regularly scheduled outdoor time</li><li>Consistency through meal times</li><li>Rest time to decompress</li><li>Specialized enrichment and one-on-one time</li></ul>
<h2>Every dog is different</h2>
<p>There’s no single routine that works perfectly for every dog. A young, energetic dog may need more activity, while a senior dog may benefit from more rest. A social dog may enjoy group play, while another dog may prefer individual attention.</p>
<h2>Familiarity can make an unfamiliar place easier</h2>
<p>That’s why a good boarding routine should provide structure while still allowing room for individual needs. When your dog stays with us, our goal isn’t simply to keep them busy until you come home. It’s to provide a structured and comfortable environment where they can play, eat, enrich and rest throughout the day. Sometimes the best part of a boarding stay isn’t one big exciting activity. It’s knowing what comes next.</p>'''),
    dict(slug='why-rest-is-important-for-dogs-during-their-stay', title='Why Rest Is Important for Dogs During Their Stay', date='2026-08-19', nice='August 19, 2026', author='Carrie', img='g-6423.jpg',
         alt='A dog curled up asleep in a dog bed',
         excerpt='Playtime and attention matter, but dogs also need quiet time to rest and recharge during a stay away from home.',
         body='''<p>A stay away from home can be exciting for a dog. There are new surroundings to explore, different sounds and smells, and plenty of activity throughout the day. Although playtime and personal attention are important, dogs also need quiet time to rest and recharge.</p>
<h2>Rest prevents overstimulation</h2>
<p>Even dogs that love playing can become tired or overwhelmed by too much activity. Scheduled rest gives each dog time to relax before returning to play or other activities.</p>
<h2>Sleep supports a dog’s well-being</h2>
<p>Just like people, dogs need quality sleep to feel their best. Rest helps them maintain their energy, manage excitement and enjoy a more comfortable stay.</p>
<h2>Every dog has different needs</h2>
<p>Some dogs are highly active, while others prefer a slower pace. Age, personality and normal routines can all affect how much rest a dog needs. At Almost Home Kennels, we balance activity with appropriate quiet time so each dog has an opportunity to settle down and recharge.</p>
<p>Rest is not time taken away from the fun. It is an important part of providing dogs with a safe, comfortable and enjoyable stay.</p>'''),
]

def p_resources(c):
    cards = ''.join(f'''<a class="card photo-card" href="{c.link(p['slug'])}"><img src="img/{p['img']}" alt="{esc(p['alt'])}" loading="lazy" style="aspect-ratio:4/3"><div class="in"><span class="small"><time datetime="{p['date']}">{p['nice']}</time></span><h3>{esc(p['title'])}</h3><p>{esc(p['excerpt'])}</p><span class="go">Read more →</span></div></a>''' for p in POSTS)
    return (page_hero('Helpful resources', 'Tips for a comfortable stay',
                      'Practical guidance to help you prepare for daycare, boarding and a comfortable stay at Almost Home.')
            + f'<section style="padding-top:0"><div class="wrap"><div class="cards">{cards}</div></div></section>' + cta_band(c))
page('helpful-resources', 'Dog Boarding Tips & Resources | Almost Home Kennels',
     'Practical guidance from our team to help you prepare your dog for daycare, boarding and a comfortable stay at Almost Home Kennels.',
     'Helpful Resources', p_resources, ptype='CollectionPage')

for P in POSTS:
    def make(P):
        def body(c):
            others = [o for o in POSTS if o is not P]
            rel = ''.join(f'<a class="more-link" href="{c.link(o["slug"])}">{esc(o["title"])} →</a>' for o in others)
            return f'''<article><section class="page-hero solo"><div class="wrap"><div class="prose" style="max-width:780px">
  <span class="eyebrow">Helpful resources</span><h1>{esc(P['title'])}</h1>
  <p class="byline">By {esc(P['author'])} · <time datetime="{P['date']}">{P['nice']}</time></p>
</div></div></section>
<section style="padding-top:0"><div class="wrap" style="display:grid;gap:32px;justify-items:start">
  <img src="img/{P['img']}" alt="{esc(P['alt'])}" style="width:100%;max-width:780px;aspect-ratio:16/10;object-fit:cover;border-radius:24px" fetchpriority="high">
  <div class="prose">{P['body']}
  <p>Questions about how we care for your dog? <a href="{c.link('faq')}">Read our FAQ</a> or <a href="{c.link('contact')}">get in touch</a>.</p>
  <h2>Keep reading</h2>{rel}</div>
</div></section></article>''' + cta_band(c)
        return body
    page(P['slug'], P['title'] if len(P['title']) > 40 else P['title'] + ' | Almost Home Kennels', P['excerpt'], P['title'], make(P), hero_img=P['img'], parent='helpful-resources', og=P['img'], ptype='BlogPosting',
         schema=[{"@type": "BlogPosting", "headline": P['title'], "datePublished": P['date'], "dateModified": P['date'], "author": {"@type": "Person", "name": P['author']},
                  "publisher": {"@id": BIZ_ID}, "image": BASE + '/img/' + P['img'], "mainEntityOfPage": canon(P['slug']), "description": P['excerpt']}])

def p_areas(c):
    blurb = {'Wright City': 'Our home base in Warren County.', 'Warrenton': 'Warren County seat, along I-70.', 'Wentzville': 'St. Charles County, along I-70.',
             'Foristell': 'Along I-70 near the county line.', 'Lake St. Louis': 'St. Charles County, along I-70.', "O'Fallon": 'St. Charles County, along I-70.',
             'Innsbrook': 'Warren County.', 'New Melle': 'St. Charles County.', 'Marthasville': 'Warren County.', 'Truxton': 'Lincoln County.', 'Troy': 'Lincoln County seat.'}
    towns = ''.join('<div class="town"><b>%s, MO</b><span>%s</span></div>' % (esc(t), esc(blurb[t])) for t in TOWNS)
    return (page_hero('Areas we serve', 'Dog boarding &amp; daycare near you',
                      'Almost Home Kennels is in Wright City, Missouri. Wright City sits on I-70 between Wentzville and Warrenton, an easy drive for dog owners across Warren, St. Charles and Lincoln counties.',
                      'hero-yard.jpg', 'The kennel building and play yard with dogs around a kiddie pool',
                      f'<a class="btn btn-green" href="{c.link("new-clients")}">New clients start here</a><a class="btn btn-line" href="https://www.google.com/maps/search/?api=1&amp;query=Almost+Home+Kennels+Wright+City+MO" target="_blank" rel="noopener">Open in Google Maps</a>')
            + f'''<section style="padding-top:0"><div class="wrap">
  <div class="head"><span class="eyebrow">Communities nearby</span><h2>Families come to us from</h2></div>
  <div class="towns">{towns}</div>
  <p class="lede" style="margin-top:28px">All drop-offs and pick-ups are scheduled, so you’ll always have a confirmed time before you make the drive. See our <a href="{c.link('dog-boarding-in-wright-city')}">dog boarding</a> and <a href="{c.link('dog-daycare-wright-city')}">dog daycare</a> pages for details and pricing.</p>
</div></section>''' + cta_band(c))
page('areas-we-serve', 'Areas We Serve: Wentzville, Warrenton & More | Almost Home',
     'Dog boarding and daycare in Wright City, MO for families in Warrenton, Wentzville, Foristell, Lake St. Louis, O’Fallon, Innsbrook, Troy and nearby.',
     'Areas We Serve', p_areas, hero_img='hero-yard.jpg')

def p_contact(c):
    return (page_hero('Contact', 'Get in touch',
                      'Call, text or email us with questions. Current clients can request reservations in the client portal, and new clients can register to schedule a tour and trial day.',
                      'g-d6359.jpg', 'Two of our team members with a doodle and a Lab in the yard')
            + contact_band(c) + cta_band(c))
page('contact', 'Contact Us | Almost Home Kennels, Wright City MO',
     'Contact Almost Home Kennels in Wright City, MO: call or text 636-459-9900, email us, or use the client portal to request dog boarding and daycare.',
     'Contact', p_contact, hero_img='g-d6359.jpg', ptype='ContactPage')

def p_portal(c):
    return f'''<section class="portal-hero page-hero solo" style="padding-bottom:clamp(28px,4vw,44px)"><div class="wrap">
  <div><span class="eyebrow">Client portal</span><h1>Manage your dog’s stays</h1>
  <p class="lede">Request reservations, keep vaccine records current, and update your dog’s details, all in one place.</p></div>
</div></section>
<section id="portal"><div class="wrap">
  <div class="p-shell">
    <div class="p-top"><div><h2 id="pGreeting">Hi!</h2><span class="small">Biscuit &amp; Juniper</span></div>
      <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap"><span class="demo-tag">Preview · sample data</span><button type="button" class="linkbtn" id="pReset">Reset</button></div></div>
    <div id="ptabs" role="tablist" aria-label="Portal sections">
      <button type="button" class="chip" role="tab" data-v="overview" aria-selected="true">Overview</button>
      <button type="button" class="chip" role="tab" data-v="reservations" aria-selected="false">Reservations</button>
      <button type="button" class="chip" role="tab" data-v="book" aria-selected="false">Request a stay</button>
      <button type="button" class="chip" role="tab" data-v="dogs" aria-selected="false">My dogs</button>
      <button type="button" class="chip" role="tab" data-v="vaccines" aria-selected="false">Vaccine records</button>
    </div>
    <div id="pview" aria-live="polite"></div>
  </div>
</div></section>
<section><div class="wrap"><div class="cards">
  <a class="card" href="{c.link('checklists-and-scheduling')}"><h3>Packing checklist</h3><p>Tick off food, meds and records before drop-off.</p><span class="go">Open checklist →</span></a>
  <a class="card" href="{c.link('pricing-and-services')}"><h3>Pricing</h3><p>Boarding $43/night, daycare $36/day. Estimate your stay.</p><span class="go">See pricing →</span></a>
  <a class="card" href="{c.link('faq')}"><h3>Cancellation policy</h3><p>48 hours for boarding, 24 hours for daycare and grooming.</p><span class="go">Read the FAQ →</span></a>
</div></div></section>'''
page('client-portal', 'Client Portal | Almost Home Kennels',
     'Request dog boarding and daycare, manage vaccine records and update your dog’s details in the Almost Home Kennels client portal.',
     'Client Portal', p_portal)

def p_404(c):
    return f'''<section><div class="wrap notfound">
  <span class="eyebrow">Page not found</span><h1 style="font-size:clamp(2.4rem,6vw,4rem)">This pup wandered off.</h1>
  <p class="lede">The page you’re looking for has moved or doesn’t exist. Try one of these instead.</p>
  <div style="display:flex;gap:12px;flex-wrap:wrap;justify-content:center"><a class="btn btn-green" href="{c.link('')}">Home</a><a class="btn btn-line" href="{c.link('pricing-and-services')}">Pricing &amp; services</a><a class="btn btn-line" href="{c.link('contact')}">Contact</a></div>
  <img src="img/g-6468.jpg" alt="A white dog lying belly-up" style="width:min(360px,100%);border-radius:24px;margin-top:12px">
</div></section>'''
page('404', 'Page Not Found | Almost Home Kennels', 'This page could not be found.', 'Not found', p_404, noindex=True)

# ---------------------------------------------------------------- write
def write(path, s):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='utf-8').write(s)

css = open(os.path.join(HERE, 'base.css'), encoding='utf-8').read() + '''
body{margin:0}
.skip{position:absolute;left:-999px;top:8px;z-index:100;background:var(--paper);color:var(--ink);padding:10px 16px;border-radius:999px;font-weight:700}
.skip:focus{left:16px}
'''
js = open(os.path.join(HERE, 'site.js'), encoding='utf-8').read()

for mode in ('preview', 'dist'):
    out = os.path.join(ROOT, mode)
    shutil.rmtree(out, ignore_errors=True)
    c = Ctx(mode)
    for slug in PAGES:
        s = render(c, slug)
        if mode == 'preview':
            write(os.path.join(out, (slug or 'index') + '.html'), s)
        else:
            write(os.path.join(out, '404.html' if slug == '404' else os.path.join(slug, 'index.html') if slug else 'index.html'), s)
    write(os.path.join(out, 'assets/site.css'), css)
    write(os.path.join(out, 'assets/site.js'), js)
    shutil.copytree(os.path.join(SITE, 'img'), os.path.join(out, 'img'))
    for f in ('favicon.png', 'apple-touch-icon.png'): shutil.copy(os.path.join(SITE, f), os.path.join(out, f))
    if mode == 'dist':
        urls = [s for s in PAGES if s != '404']
        pri = {'': '1.0', 'pricing-and-services': '0.9', 'dog-boarding-in-wright-city': '0.9', 'dog-daycare-wright-city': '0.9', 'new-clients': '0.8'}
        sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'
        for s in urls:
            p = PAGES[s]
            sm += '  <url><loc>%s</loc><lastmod>%s</lastmod><priority>%s</priority>%s</url>\n' % (canon(s), TODAY, pri.get(s, '0.6'),
                  ('<image:image><image:loc>%s/img/%s</image:loc></image:image>' % (BASE, p['hero_img'])) if p['hero_img'] else '')
        sm += '</urlset>\n'
        write(os.path.join(out, 'sitemap.xml'), sm)
        write(os.path.join(out, 'robots.txt'), 'User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n' % BASE)
        # 301s for old WordPress URLs (Netlify/Cloudflare Pages format) + Apache equivalent
        red = [('/home-flatsome/', '/'), ('/contact-us/', '/contact/'), ('/sitemap_index.xml', '/sitemap.xml'), ('/page-sitemap.xml', '/sitemap.xml'),
               ('/post-sitemap.xml', '/sitemap.xml'), ('/category/helpful-resources/', '/helpful-resources/'), ('/hello-world/', '/helpful-resources/')]
        write(os.path.join(out, '_redirects'), ''.join('%s %s 301\n' % r for r in red))
        write(os.path.join(out, '.htaccess'), 'ErrorDocument 404 /404.html\n' + ''.join('Redirect 301 %s %s\n' % r for r in red))
print('pages:', len(PAGES))
