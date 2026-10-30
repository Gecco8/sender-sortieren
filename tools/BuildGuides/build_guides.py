# -*- coding: utf-8 -*-
"""Erzeugt die Marken-Anleitungen unter src/ChanSortWeb/wwwroot/anleitung/.

Aufruf (aus dem Projektordner):   python tools/BuildGuides/build_guides.py
Inhalte ändern:                   tools/BuildGuides/guides_data.py bearbeiten und erneut ausführen.
"""
import html, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from guides_data import BRANDS

# Adresse für Rückmeldungen zu den Anleitungen – vor der Veröffentlichung anpassen
FEEDBACK_MAIL = "kontakt@sender-sortieren.de"
SITE_NAME = "Senderlisten-Editor"
# Adresse der Seite (ohne / am Ende). Cloudflare Pages liefert "x.html" auch als "x" aus,
# daher stehen Kanonische URLs und Sitemap ohne ".html".
SITE_URL = "https://sender-sortieren.de"

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "src", "ChanSortWeb", "wwwroot", "anleitung")

def text(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()

def attr(s):
    return html.escape(s, quote=True)

THEME_SWITCH = """<label class="theme-switch" title="Hell / Dunkel umschalten">
        <span class="theme-icon sun" aria-hidden="true">☀︎</span>
        <input type="checkbox" id="themeToggle" role="switch" aria-label="Dunkler Modus">
        <span class="switch-track"><span class="switch-thumb"></span></span>
        <span class="theme-icon moon" aria-hidden="true">☾</span>
      </label>"""

ICON = """<svg viewBox="0 0 24 24" width="16" height="16"><rect x="3" y="5" width="18" height="12" rx="2.5" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M8 20h8" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/><path d="M7 9h6M7 12.5h9" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>"""

def page(title, description, body, jsonld=None, path=""):
    ld = ""
    if jsonld:
        ld = '\n  <script type="application/ld+json">' + json.dumps(jsonld, ensure_ascii=False) + "</script>"
    return f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{attr(title)}</title>
  <meta name="description" content="{attr(description)}">
  <link rel="canonical" href="{SITE_URL}/{path}">
  <script>
    try {{ const t = localStorage.getItem('theme'); if (t === 'light' || t === 'dark') document.documentElement.dataset.theme = t; }} catch {{ }}
  </script>
  <link rel="stylesheet" href="../app.css">
  <link rel="stylesheet" href="../guide.css">
  <script src="../guide.js" defer></script>{ld}
</head>
<body>
  <header class="menubar">
    <a class="brand" href="../index.html">
      <span class="app-icon" aria-hidden="true">{ICON}</span>
      <span>{SITE_NAME}</span>
    </a>
    <nav class="menubar-nav">
      <a href="index.html">Anleitungen</a>
    </nav>
    <div class="menubar-actions">
      {THEME_SWITCH}
    </div>
  </header>

  <main class="guide">
{body}
  </main>

  <footer class="site-footer">
    Basiert auf <a href="https://github.com/PredatH0r/ChanSort" target="_blank" rel="noopener">ChanSort</a> von Horst Beham ·
    Lizenz GPLv3 · <a href="https://github.com/Gecco8/sender-sortieren" target="_blank" rel="noopener">Quellcode</a> · <a href="../impressum.html">Impressum</a> · <a href="../datenschutz.html">Datenschutz</a>
  </footer>
</body>
</html>
"""

STEPS_STRIP = """    <ol class="flow">
      <li><span class="flow-nr">1</span><b>Exportieren</b><span>Senderliste am Fernseher auf einen USB-Stick kopieren</span></li>
      <li><span class="flow-nr">2</span><b>Öffnen</b><span>Datei oder Ordner hier im Browser laden</span></li>
      <li><span class="flow-nr">3</span><b>Bearbeiten</b><span>Sortieren, löschen, umbenennen, Favoriten</span></li>
      <li><span class="flow-nr">4</span><b>Zurückspielen</b><span>Gespeicherte Datei auf den Stick und importieren</span></li>
    </ol>"""

CTA = """<a class="btn btn-primary btn-large" href="../index.html">Senderliste jetzt öffnen</a>"""

def brand_nav(current=None):
    items = []
    for b in BRANDS:
        cls = ' class="current"' if b["slug"] == current else ""
        items.append(f'<a{cls} href="{b["slug"]}.html">{html.escape(b["name"])}</a>')
    return '<nav class="brand-grid" aria-label="Weitere Marken">' + "".join(items) + "</nav>"

def build_brand(b):
    parts = []
    parts.append(f"""    <nav class="crumbs"><a href="../index.html">Start</a> › <a href="index.html">Anleitungen</a> › {html.escape(b['name'])}</nav>
    <section class="guide-hero">
      <h1>{html.escape(b['h1'])}</h1>
      <p class="lead">{b['intro']}</p>
      <div class="hero-actions">{CTA}<a class="btn btn-large" href="#geraet">Zur Anleitung</a></div>
    </section>
{STEPS_STRIP}""")

    if b.get("warning"):
        parts.append(f'    <div class="callout">{b["warning"]}</div>')

    # Gerätewahl
    if len(b["groups"]) > 1 or b.get("identify_hint"):
        chips = "".join(
            f'<a class="pick" href="#{g["id"]}"><b>{html.escape(g["title"])}</b>'
            + (f'<span>{g["identify"]}</span>' if g["identify"] else "") + "</a>"
            for g in b["groups"])
        hint = f'<p class="muted">{b["identify_hint"]}</p>' if b.get("identify_hint") else ""
        title = "Welches Gerät hast du?" if len(b["groups"]) > 1 else "Dein Gerät"
        parts.append(f"""    <section id="geraet" class="guide-section">
      <h2>{title}</h2>
      {hint}
      <div class="picks">{chips}</div>
    </section>""")
    else:
        parts.append('    <span id="geraet"></span>')

    # Anleitungen je Gruppe
    for g in b["groups"]:
        steps = "".join(f"<li>{s}</li>" for s in g["steps"])
        file_ = f'<div class="stick"><span class="stick-label">Auf dem Stick</span><span>{g["file"]}</span></div>' if g["file"] else ""
        notes = "".join(f"<li>{n}</li>" for n in g["notes"])
        notes = f'<ul class="notes">{notes}</ul>' if notes else ""
        heading = "Export auf USB" if b["slug"] != "receiver" else ""
        parts.append(f"""    <section class="window guide-window" id="{g['id']}">
      <div class="titlebar"><h2 class="titlebar-title">{html.escape(g['title'])}</h2></div>
      <div class="window-body">
        {f'<h3>{heading}</h3>' if heading else ''}
        <ol class="steps">{steps}</ol>
        {file_}
        {notes}
      </div>
    </section>""")

    # Dateien auf dem Stick
    if b["stick_files"]:
        rows = "".join(f"<tr><td>{f}</td><td>{w}</td></tr>" for f, w in b["stick_files"])
        parts.append(f"""    <section class="guide-section">
      <h2>Was liegt auf dem Stick?</h2>
      <p class="muted">Unsicher? Wähle im Editor einfach den ganzen Ordner vom Stick – das Format wird automatisch erkannt.</p>
      <table class="files"><thead><tr><th>Datei</th><th>Was tun?</th></tr></thead><tbody>{rows}</tbody></table>
    </section>""")

    # Zurückspielen
    imp = "".join(f"<li>{s}</li>" for s in b["import"])
    parts.append(f"""    <section class="guide-section">
      <h2>Zurück auf den Fernseher</h2>
      <ol class="steps">{imp}</ol>
      <p class="muted small">Tipp: Bewahre eine Kopie der Originaldatei auf. Dann kannst du jederzeit zum alten Stand zurück.</p>
    </section>""")

    # FAQ
    faq = b["faq"]
    if faq:
        items = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in faq)
        parts.append(f"""    <section class="guide-section">
      <h2>Häufige Probleme</h2>
      <div class="faq">{items}</div>
    </section>""")

    subject = f"Anleitung {b['name']}"
    mail = f"mailto:{FEEDBACK_MAIL}?subject={subject.replace(' ', '%20')}"
    parts.append(f"""    <section class="feedback">
      <div>
        <b>Hat es bei dir so geklappt?</b>
        <span>Menünamen unterscheiden sich je nach Modell und Software-Stand. Wenn es bei deinem Gerät anders heißt, schreib uns kurz Modell und Menüweg – wir ergänzen die Anleitung.</span>
      </div>
      <a class="btn" href="{mail}">Rückmeldung senden</a>
    </section>
    <section class="guide-section">
      <h2>Andere Marken</h2>
      {brand_nav(b['slug'])}
    </section>
    <p class="disclaimer">Alle Angaben ohne Gewähr. Mache vor dem Zurückspielen eine Sicherung der Originaldatei.</p>""")

    jsonld = None
    if faq:
        jsonld = {"@context": "https://schema.org", "@type": "FAQPage",
                  "mainEntity": [{"@type": "Question", "name": text(q),
                                  "acceptedAnswer": {"@type": "Answer", "text": text(a)}} for q, a in faq]}
    return page(b["title"], b["description"], "\n".join(parts), jsonld, f"anleitung/{b['slug']}")

def build_index():
    cards = "".join(
        f'<a class="brand-card" href="{b["slug"]}.html"><b>{html.escape(b["name"])}</b><span>{html.escape(b["description"].split(". ")[0].rstrip("."))}.</span></a>'
        for b in BRANDS)
    body = f"""    <nav class="crumbs"><a href="../index.html">Start</a> › Anleitungen</nav>
    <section class="guide-hero">
      <h1>Senderliste exportieren und sortieren</h1>
      <p class="lead">So bekommst du die Senderliste deines Fernsehers auf einen USB-Stick – und nach dem Sortieren wieder zurück. Wähle deine Marke.</p>
    </section>
{STEPS_STRIP}
    <section class="guide-section">
      <div class="brand-cards">{cards}</div>
    </section>
    <section class="guide-section">
      <h2>Tipps, die für alle Marken gelten</h2>
      <ul class="tips">
        <li><b>USB-Stick:</b> FAT32-formatiert, am besten bis 32 GB. Viele Fernseher erkennen NTFS oder exFAT nicht.</li>
        <li><b>Sicherung:</b> Kopiere die exportierte Originaldatei vor dem Bearbeiten auf deinen Rechner.</li>
        <li><b>Dateinamen nicht ändern:</b> Der Fernseher sucht beim Import genau den Namen, den er beim Export vergeben hat.</li>
        <li><b>Ganzen Ordner wählen:</b> Schreibt der Fernseher mehrere Dateien, wähle im Editor einfach den Ordner – das Format wird automatisch erkannt.</li>
        <li><b>Kein Anbieter beim Suchlauf:</b> Vorsortierte Listen von Kabel- oder Sat-Anbietern lassen sich oft nicht dauerhaft ändern. Wähle beim Suchlauf „Andere“ bzw. „Keiner“.</li>
        <li><b>Automatische Senderaktualisierung ausschalten:</b> Sonst sortiert der Fernseher die Liste später wieder um.</li>
      </ul>
      <div class="hero-actions">{CTA}</div>
    </section>"""
    return page("Senderliste exportieren und sortieren – Anleitungen für alle Marken",
                "Anleitungen: Senderliste vom Fernseher auf USB exportieren, im Browser sortieren und zurückspielen – für Samsung, LG, Sony, Philips, Panasonic, TCL, Hisense und weitere Marken.",
                body, path="anleitung/")

def build_sitemap():
    urls = ["", "anleitung/"] + [f"anleitung/{b['slug']}" for b in BRANDS]
    items = "".join(f"  <url><loc>{SITE_URL}/{u}</loc></url>\n" for u in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{items}</urlset>\n'

def main():
    os.makedirs(OUT, exist_ok=True)
    for b in BRANDS:
        with open(os.path.join(OUT, b["slug"] + ".html"), "w", encoding="utf-8", newline="\n") as f:
            f.write(build_brand(b))
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write(build_index())
    root = os.path.dirname(OUT)
    with open(os.path.join(root, "sitemap.xml"), "w", encoding="utf-8", newline="\n") as f:
        f.write(build_sitemap())
    with open(os.path.join(root, "robots.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n")
    print(f"{len(BRANDS)} Markenseiten + Übersicht nach {OUT} geschrieben")

if __name__ == "__main__":
    main()
