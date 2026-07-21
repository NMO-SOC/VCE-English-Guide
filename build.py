#!/usr/bin/env python3
"""Build a multi-page static website from the VCE English Exam Prep LaTeX booklet."""
import os, re, shutil, json, html, urllib.parse
from bs4 import BeautifulSoup

SRC = "/sessions/loving-pensive-clarke/mnt/VCE Textbook/2026 Yr12 Booklet/12 Booklet 2026"
BUILD = "/sessions/loving-pensive-clarke/mnt/outputs/site-build"
PUBLIC = os.path.join(BUILD, "public")
IMG_DIR = os.path.join(PUBLIC, "assets", "img")
PDF_DIR = os.path.join(PUBLIC, "assets", "pdf")
FILES_DIR = os.path.join(PUBLIC, "assets", "files")

for d in (PUBLIC, IMG_DIR, PDF_DIR, FILES_DIR, os.path.join(PUBLIC, "assets")):
    os.makedirs(d, exist_ok=True)

SITE_TITLE = "VCE English Exam Preparation Guide"

with open(os.path.join(SRC, "main.tex"), encoding="utf-8") as f:
    tex = f.read()

def pdf_repl(m):
    fname = m.group(2).strip()
    if not fname.lower().endswith(".pdf"):
        fname += ".pdf"
    return "\n\nZZPDFEMBED " + fname + " ZZEND\n\n"
tex = re.sub(r"\\includepdf(\[[^\]]*\])?\s*\{([^}]+)\}", pdf_repl, tex)

def att_repl(m):
    return r"\href{ZZFILE::%s}{%s}" % (m.group(1).strip(), m.group(2).strip())
tex = re.sub(r"\\textattachfile\{([^}]+)\}\{([^}]+)\}", att_repl, tex)

pre_tex = os.path.join(BUILD, "_pre.tex")
with open(pre_tex, "w", encoding="utf-8") as f:
    f.write(tex)

os.system('cd "%s" && pandoc "%s" -f latex -t html5 --section-divs --wrap=none -o "%s/_body.html"'
          % (SRC, pre_tex, BUILD))

with open(os.path.join(BUILD, "_body.html"), encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

copied_imgs = set()
for img in soup.find_all("img"):
    src = img.get("src", "")
    base = os.path.basename(src)
    srcpath = os.path.join(SRC, base)
    if os.path.exists(srcpath):
        if base not in copied_imgs:
            shutil.copy(srcpath, os.path.join(IMG_DIR, base))
            copied_imgs.add(base)
        img["src"] = "assets/img/" + urllib.parse.quote(base)
        img["loading"] = "lazy"
        cls = img.get("class", [])
        img["class"] = (cls if isinstance(cls, list) else [cls]) + ["content-img"]

for a in soup.find_all("a", href=True):
    if a["href"].startswith("ZZFILE::"):
        fn = a["href"].split("::", 1)[1]
        srcpath = os.path.join(SRC, fn)
        if os.path.exists(srcpath):
            shutil.copy(srcpath, os.path.join(FILES_DIR, fn))
        a["href"] = "assets/files/" + urllib.parse.quote(fn)
        a["class"] = a.get("class", []) + ["file-dl"]
        a["download"] = ""

pdf_pat = re.compile(r"ZZPDFEMBED\s+(\S+?\.pdf)\s+ZZEND", re.I)
copied_pdfs = set()
for p in soup.find_all(["p", "div"]):
    txt = p.get_text()
    m = pdf_pat.search(txt)
    if not m:
        continue
    fname = m.group(1)
    srcpath = os.path.join(SRC, fname)
    if os.path.exists(srcpath) and fname not in copied_pdfs:
        shutil.copy(srcpath, os.path.join(PDF_DIR, fname))
        copied_pdfs.add(fname)
    enc = urllib.parse.quote(fname)
    block = BeautifulSoup(
        '<div class="pdf-embed">'
        '<div class="pdf-embed-bar"><span class="pdf-name">%s</span>'
        '<a class="pdf-open" href="assets/pdf/%s" target="_blank" rel="noopener">Open in new tab &#8599;</a>'
        '<a class="pdf-dl" href="assets/pdf/%s" download>Download &#8595;</a></div>'
        '<iframe class="pdf-frame" src="assets/pdf/%s#view=FitH" loading="lazy" title="%s"></iframe>'
        '</div>' % (html.escape(fname), enc, enc, enc, html.escape(fname)),
        "html.parser")
    p.replace_with(block)

parts = [s for s in soup.find_all("section", class_="level1", recursive=True)
         if s.find_parent("section") is None]

def slugify(txt):
    s = re.sub(r"[^a-z0-9]+", "-", txt.lower()).strip("-")
    return s or "section"

part_meta = []
for i, sec in enumerate(parts, 1):
    h1 = sec.find("h1")
    title = h1.get_text(" ", strip=True) if h1 else "Part %d" % i
    slug = slugify(title)
    part_meta.append({"idx": i, "title": title, "slug": slug,
                      "file": "part-%02d-%s.html" % (i, slug), "sec": sec})

id_to_page = {}
for pm in part_meta:
    for el in pm["sec"].find_all(id=True):
        id_to_page[el["id"]] = pm["file"]
    if pm["sec"].get("id"):
        id_to_page[pm["sec"]["id"]] = pm["file"]

def heading_tree(sec):
    out = []
    for h in sec.find_all(["h2", "h3", "h4", "h5"]):
        anchor = h.find_parent("section")
        out.append({"id": anchor.get("id") if anchor else None,
                    "text": h.get_text(" ", strip=True), "level": int(h.name[1])})
    return out

search_index = []
for pm in part_meta:
    for h in pm["sec"].find_all(["h1", "h2", "h3", "h4", "h5"]):
        anchor = h.find_parent("section")
        hid = anchor.get("id") if anchor else None
        search_index.append({"t": h.get_text(" ", strip=True), "p": pm["title"],
                             "u": pm["file"] + ("#" + hid if hid else "")})
with open(os.path.join(PUBLIC, "assets", "search.json"), "w", encoding="utf-8") as f:
    json.dump(search_index, f, ensure_ascii=False)

def rewrite_anchors(scope, current_file):
    for a in scope.find_all("a", href=True):
        href = a["href"]
        if href.startswith("#"):
            page = id_to_page.get(href[1:])
            if page and page != current_file:
                a["href"] = page + href

def nav_html(active_file):
    items = []
    for pm in part_meta:
        cls = ' class="active"' if pm["file"] == active_file else ""
        items.append('<li%s><a href="%s"><span class="num">%02d</span>%s</a></li>'
                     % (cls, pm["file"], pm["idx"], html.escape(pm["title"])))
    return "\n".join(items)

def page_shell(title, active_file, main_html, prevnext=""):
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s &middot; %(site)s</title>
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<button id="menu-toggle" aria-label="Menu">&#9776;</button>
<div class="layout">
  <aside class="sidebar" id="sidebar">
    <a class="brand" href="index.html">
      <span class="brand-title">VCE English</span>
      <span class="brand-sub">Exam Prep Guide</span>
    </a>
    <div class="search-wrap">
      <input id="search" type="search" placeholder="Search the guide&hellip;" autocomplete="off">
      <div id="search-results"></div>
    </div>
    <nav class="toc"><ol>%(nav)s</ol></nav>
    <div class="side-foot">South Oakleigh College &middot; 2026</div>
  </aside>
  <main class="content" id="main">
    %(main)s
    %(prevnext)s
  </main>
</div>
<script src="assets/site.js"></script>
</body>
</html>""" % {"title": html.escape(title), "site": SITE_TITLE,
             "nav": nav_html(active_file), "main": main_html, "prevnext": prevnext}

for i, pm in enumerate(part_meta):
    sec = pm["sec"]
    rewrite_anchors(sec, pm["file"])
    tree = heading_tree(sec)
    lis = ['<li class="lvl%d"><a href="#%s">%s</a></li>' % (h["level"], h["id"], html.escape(h["text"]))
           for h in tree if h["id"] and h["level"] <= 4]
    toc_items = ('<details class="page-toc" open><summary>On this page</summary><ul>%s</ul></details>'
                 % "".join(lis)) if lis else ""
    prev_a = ('<a class="pn prev" href="%s"><span>&#8592; Previous</span><b>%s</b></a>'
              % (part_meta[i-1]["file"], html.escape(part_meta[i-1]["title"]))) if i > 0 else "<span></span>"
    next_a = ('<a class="pn next" href="%s"><span>Next &#8594;</span><b>%s</b></a>'
              % (part_meta[i+1]["file"], html.escape(part_meta[i+1]["title"]))) if i < len(part_meta)-1 else "<span></span>"
    prevnext = '<nav class="prevnext">%s%s</nav>' % (prev_a, next_a)
    h1 = sec.find("h1")
    if h1:
        h1.insert_before(BeautifulSoup('<div class="part-label">Part %02d</div>' % pm["idx"], "html.parser"))
    out = page_shell(pm["title"], pm["file"], toc_items + sec.decode(), prevnext=prevnext)
    with open(os.path.join(PUBLIC, pm["file"]), "w", encoding="utf-8") as f:
        f.write(out)

BLURB = {
 "Preface": "Welcome and how to use this guide.",
 "Sunset Boulevard": "Billy Wilder's film — context, themes, quote banks, scene analyses, techniques, symbols and exemplar essays.",
 "Rainbow's End": "Jane Harrison's play — context, characters, themes, quotes and sample responses.",
 "Analytical Text Response Essays": "Planning, structure, and proofreading a text-response essay.",
 "Creating Texts": "Audience, purpose, personal journeys and practice stimuli.",
 "Analysing Argument": "Language analysis — written & visual, sample articles and essays.",
 "The Exam": "Format and strategies for addressing the requirements.",
 "Practice Exams": "Full practice papers and past exams.",
 "Exam Assessment Criteria": "How Sections A, B and C are marked.",
 "Exam Checklists": "Ready-reference checklists for exam day.",
 "Key Takeaways from the 2024 Assessment Report": "What VCAA assessors flagged, section by section.",
 "Effectively Studying For Exams": "Study habits, schedules, recall and wellbeing.",
}
cards = []
for pm in part_meta:
    cards.append('<a class="card" href="%s"><div class="card-num">%02d</div>'
                 '<div class="card-body"><h3>%s</h3><p>%s</p></div></a>'
                 % (pm["file"], pm["idx"], html.escape(pm["title"]),
                    html.escape(BLURB.get(pm["title"], ""))))

landing_main = """
<section class="hero">
  <div class="hero-inner">
    <div class="hero-badge">South Oakleigh College</div>
    <h1>VCE English<br>Exam Preparation Guide</h1>
    <p class="hero-sub">Units 3/4 English &middot; Cohort of 2026 &middot; Version 3.1</p>
    <p class="hero-lede">Exemplar essays, thematic and character quote banks, scene analyses, argument-analysis frameworks, full practice exams, marking criteria and study strategies &mdash; the complete booklet, now browsable.</p>
    <div class="hero-cta">
      <a class="btn" href="%s">Start reading &#8594;</a>
      <a class="btn ghost" href="assets/pdf/Exam1.pdf" target="_blank" rel="noopener">Practice exam</a>
    </div>
  </div>
</section>
<h2 class="section-head">Contents</h2>
<div class="cards">%s</div>
""" % (part_meta[0]["file"], "".join(cards))

with open(os.path.join(PUBLIC, "index.html"), "w", encoding="utf-8") as f:
    f.write(page_shell("Home", "index.html", landing_main))

print("PARTS:", len(part_meta), "IMAGES:", len(copied_imgs), "PDFS:", len(copied_pdfs), "SEARCH:", len(search_index))
for pm in part_meta:
    print("  %02d %-45s -> %s" % (pm["idx"], pm["title"][:45], pm["file"]))
