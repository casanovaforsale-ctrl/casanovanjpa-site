#!/usr/bin/env python3
"""Builds the Casanova Group site.

    python3 tools/build.py

Reads page bodies from src/pages/, wraps them in the shared layout and writes:
  docs/      the site GitHub Pages serves (clean URLs such as /blog/)
  preview/   the same site with links pointing at index.html files, for
             viewing straight from disk or as a hosted preview

Inside a page body, write {{root}} for the path back to the site root and
{{link:blog/}} for a link to another page. Each page starts with a
<!--meta {...} --> block holding its title, description and path.
"""
import json
import re
import shutil
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
SRC = HERE / "src" / "pages"
STATIC = HERE / "static"
SITE = "https://casanovanjpa.com"

PHONE_247 = "856-888-4334"
PHONE_CELL = "724-968-8824"
PHONE_OFFICE = "856-316-1100"
EMAIL = "casanovaforsale@gmail.com"

NAV = [
    ("Buy", "{{link:}}#buy"),
    ("Sell", "{{link:}}#sell"),
    ("Invest", "{{link:}}#invest"),
    ("Reviews", "{{link:}}#reviews"),
    ("Blog", "{{link:blog/}}"),
    ("Moving to Moorestown", "{{link:Moving-to-moorestown/}}"),
]

SOCIAL = [
    ("Facebook", "https://www.facebook.com/CasanovaRealEstateLLC/"),
    ("YouTube", "https://www.youtube.com/@CASANOVA_TOURS"),
    ("Instagram", "https://www.instagram.com/_realestatetours/"),
    ("TikTok", "https://www.tiktok.com/@realestatetours"),
    ("LinkedIn", "https://www.linkedin.com/in/rodriguezrealestate3/"),
    ("Zillow", "https://www.zillow.com/profile/CasanovaRealestate"),
]

AGENT_LD = {
    "@context": "https://schema.org",
    "@type": "RealEstateAgent",
    "@id": SITE + "/#nicholas-rodriguez-jr",
    "name": "Nicholas Rodriguez Jr.",
    "alternateName": "Casanova Group",
    "jobTitle": "Real Estate Sales Agent",
    "url": SITE + "/",
    "image": SITE + "/assets/img/og-share.jpg",
    "logo": SITE + "/favicon-512.png",
    "telephone": "+1-856-888-4334",
    "email": EMAIL,
    "priceRange": "$120,000-$310,000",
    "description": "Nicholas Rodriguez Jr. is a licensed real estate agent with Keller Williams Moorestown, serving South Jersey and Philadelphia. Licensed since March 2019 with 41 homes closed. Works with first-time buyers, sellers and investors.",
    "address": {"@type": "PostalAddress", "streetAddress": "513 S Lenola Road, Suite 200", "addressLocality": "Moorestown", "addressRegion": "NJ", "postalCode": "08057", "addressCountry": "US"},
    "geo": {"@type": "GeoCoordinates", "latitude": 39.9471107, "longitude": -74.9693536},
    "areaServed": ["Burlington County, NJ", "Camden County, NJ", "Gloucester County, NJ", "Salem County, NJ", "Atlantic County, NJ", "Philadelphia County, PA", "Bucks County, PA"],
    "openingHoursSpecification": {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], "opens": "00:00", "closes": "23:59"},
    "worksFor": {"@type": "Organization", "name": "Keller Williams Realty Moorestown"},
    "alumniOf": {"@type": "CollegeOrUniversity", "name": "Rowan University"},
    "knowsLanguage": ["en"],
    "sameAs": [u for _, u in SOCIAL],
}

GOOGLE_G = ('<svg viewBox="0 0 48 48" aria-hidden="true" focusable="false"><path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>'
            '<path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>'
            '<path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>'
            '<path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/></svg>')

EHO = ('<svg viewBox="0 0 32 32" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="2">'
       '<path d="M3 15 16 4l13 11"/><path d="M7 12v16h18V12"/><path d="M11 17h10M11 22h10"/></svg>')


def header(current):
    items = []
    for label, href in NAV:
        cur = ' aria-current="page"' if current and href == "{{link:" + current + "}}" else ""
        items.append(f'<li><a href="{href}"{cur}>{label}</a></li>')
    items.append('<li><a class="btn btn-primary" href="https://cal.com/nicholas-rodriguez-jr-r5sia3/30min" target="_blank" rel="noopener">Book a time</a></li>')
    return f"""<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="topline"><div class="wrap">
    <span>Answered 24/7: <a href="tel:+18568884334">{PHONE_247}</a></span>
    <span><a href="https://nickjr.kw.com/" target="_blank" rel="noopener">Search homes for sale</a></span>
  </div></div>
  <nav class="wrap nav" aria-label="Main">
    <a class="brand" href="{{{{link:}}}}">
      <img src="{{{{root}}}}assets/img/logo.webp" alt="" width="46" height="39">
      <span><span class="brand-name">Casanova Group</span><span class="brand-sub">Nicholas Rodriguez Jr. · Realtor</span></span>
    </a>
    <button class="menu-btn" type="button" aria-expanded="false" aria-controls="nav-links">Menu</button>
    <ul class="nav-links" id="nav-links">{''.join(items)}</ul>
  </nav>
</header>"""


def footer():
    social = "".join(f'<li><a href="{u}" target="_blank" rel="noopener">{n}</a></li>' for n, u in SOCIAL)
    return f"""<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div class="footer-brand">
        <span class="brand-name">Casanova Group</span>
        <span class="tagline">Opening doors to timeless elegance.</span>
        <p>Buyer, seller and investor representation across seven counties in South Jersey and Philadelphia.</p>
        <a class="pref-source" href="https://www.google.com/preferences/source?q=casanovanjpa.com" target="_blank" rel="noopener">{GOOGLE_G}<span>Add us as a preferred source on Google</span></a>
      </div>
      <div><h4>Reach Nick</h4><ul>
        <li><a href="tel:+18568884334">{PHONE_247}</a> (24/7)</li>
        <li><a href="tel:+17249688824">{PHONE_CELL}</a> (cell)</li>
        <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
        <li><a href="https://cal.com/nicholas-rodriguez-jr-r5sia3/30min" target="_blank" rel="noopener">Book a 30-minute call</a></li>
      </ul></div>
      <div><h4>Explore</h4><ul>
        <li><a href="https://nickjr.kw.com/" target="_blank" rel="noopener">Search homes for sale</a></li>
        <li><a href="{{{{link:blog/}}}}">Blog</a></li>
        <li><a href="{{{{link:Moving-to-moorestown/}}}}">Moving to Moorestown guide</a></li>
        <li><a href="{{{{link:openhouse-waitlist-sign-up/}}}}">Open House app for agents</a></li>
        <li><a href="{{{{link:}}}}#faq">FAQ</a></li>
        <li><a href="{{{{link:privacy/}}}}">Privacy policy</a></li>
        <li><a href="#" data-cookie-open>Cookie choices</a></li>
      </ul></div>
      <div><h4>Follow</h4><ul>{social}</ul></div>
    </div>
    <div class="legal">
      <p>Nicholas Rodriguez Jr., Sales Agent. NJ Lic #1969622 | PA Lic #RS369752. Keller Williams Realty, 513 S Lenola Rd, Ste 200, Moorestown NJ 08057. Office {PHONE_OFFICE}. Each office independently owned and operated.</p>
      <p class="eho">{EHO}<span>Equal Housing Opportunity. All real estate services are offered without regard to race, color, religion, sex, handicap, familial status, or national origin.</span></p>
      <p>© <span data-year>{date.today().year}</span> Nicholas Rodriguez Jr. All rights reserved.</p>
    </div>
  </div>
</footer>
<div class="callbar"><a href="tel:+18568884334">Call 24/7</a><a href="https://cal.com/nicholas-rodriguez-jr-r5sia3/30min" target="_blank" rel="noopener">Book a time</a></div>
<div class="cookie" id="cookie" role="dialog" aria-label="Cookies" hidden>
  <p>This site uses Google Analytics cookies to count visits. You can say no and everything still works.</p>
  <div class="btn-row"><button class="btn btn-primary" id="cookie-yes" type="button">Accept</button><button class="btn btn-ghost" id="cookie-no" type="button">Reject</button></div>
</div>"""


def layout(meta, body):
    path = meta["path"]
    url = SITE + "/" + path
    title = meta["title"]
    desc = meta["description"]
    image = SITE + "/assets/img/" + meta.get("image", "og-share.jpg")
    ld = [AGENT_LD] + meta.get("jsonld", [])
    if meta.get("faq"):
        qa = []
        for q, a in re.findall(r"<details><summary>(.*?)</summary><div class=\"answer\">(.*?)</div></details>", body, re.S):
            text = re.sub(r"<[^>]+>", "", a).strip()
            qa.append({"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": text}})
        if qa:
            ld.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": qa})
    if path and not meta.get("noindex"):
        crumbs = [{"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"}]
        parts = [p for p in path.strip("/").split("/") if p]
        for i, p in enumerate(parts):
            crumbs.append({"@type": "ListItem", "position": i + 2, "name": meta.get("crumb", title) if i == len(parts) - 1 else p.replace("-", " ").title(),
                           "item": SITE + "/" + "/".join(parts[: i + 1]) + "/"})
        ld.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": crumbs})
    ld_html = "\n".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    robots = '<meta name="robots" content="noindex">' if meta.get("noindex") else '<meta name="robots" content="index, follow, max-image-preview:large">'
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<meta name="description" content="{desc}">
<meta name="keywords" content="{meta.get('keywords', 'South Jersey realtor, Moorestown realtor, Camden County real estate agent, first-time home buyer NJ, Philadelphia realtor, real estate investor South Jersey, Keller Williams Moorestown')}">
<meta name="author" content="Nicholas Rodriguez Jr.">
{robots}
<link rel="canonical" href="{url}">
<meta property="og:type" content="{meta.get('ogtype', 'website')}">
<meta property="og:site_name" content="Casanova Group · Nicholas Rodriguez Jr.">
<meta property="og:title" content="{meta.get('ogtitle', title)}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{image}">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{meta.get('ogtitle', title)}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{image}">
<meta name="geo.region" content="US-NJ">
<meta name="geo.placename" content="Moorestown">
<meta name="theme-color" content="#0f2533">
<link rel="icon" href="{{{{root}}}}favicon.png" type="image/png">
<link rel="apple-touch-icon" href="{{{{root}}}}apple-touch-icon.png">
<link rel="manifest" href="{{{{root}}}}site.webmanifest">
<link rel="stylesheet" href="{{{{root}}}}assets/css/fonts.css">
<link rel="stylesheet" href="{{{{root}}}}assets/css/site.css">
{ld_html}
</head>
<body>
{header(meta.get('nav', ''))}
<main id="main">
{body}
</main>
{footer()}
<script src="{{{{root}}}}assets/js/site.js" defer></script>
</body>
</html>
"""


def resolve(html, depth, preview, absolute=False):
    root = "/" if (absolute and not preview) else "../" * depth
    def link(m):
        target, frag = m.group(1), ""
        if "#" in target:
            target, frag = target.split("#", 1)
            frag = "#" + frag
        if preview:
            dest = root + target + "index.html"
        else:
            dest = root + target if (root + target) else "./"
        return dest + frag
    html = re.sub(r"\{\{link:([^}]*)\}\}", link, html)
    html = html.replace("{{root}}", root)
    return html


def main():
    pages = []
    for f in sorted(SRC.glob("*.html")):
        raw = f.read_text(encoding="utf-8")
        m = re.match(r"\s*<!--meta\s*(\{.*?\})\s*-->", raw, re.S)
        if not m:
            raise SystemExit(f"{f.name}: missing <!--meta {{...}} --> block")
        meta = json.loads(m.group(1))
        body = re.sub(r"\{\{include:([^}]+)\}\}", lambda i: (SRC.parent / "partials" / i.group(1)).read_text(encoding="utf-8"), raw[m.end():])
        pages.append((meta, body))

    for out_name, preview in (("docs", False), ("preview", True)):
        out = HERE / out_name
        if out.exists():
            shutil.rmtree(out)
        shutil.copytree(STATIC, out)
        for meta, body in pages:
            path = meta["path"]
            if meta.get("file"):
                dest, depth = out / meta["file"], 0
            else:
                dest = out / path / "index.html"
                depth = len([p for p in path.split("/") if p])
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(resolve(layout(meta, body), depth, preview, meta.get("absolute", False)), encoding="utf-8")
        if preview:
            (out / "CNAME").unlink(missing_ok=True)

    today = date.today().isoformat()
    urls = "".join(f"  <url><loc>{SITE}/{m['path']}</loc><lastmod>{m.get('updated', today)}</lastmod></url>\n"
                   for m, _ in pages if not m.get("noindex"))
    (HERE / "docs" / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n', encoding="utf-8")
    print(f"Built {len(pages)} pages into docs/ and preview/")


if __name__ == "__main__":
    main()
