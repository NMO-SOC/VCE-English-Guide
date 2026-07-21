#!/usr/bin/env python3
"""Build a multi-page static website (part hubs + chapter subpages) from the VCE booklet."""
import os, re, shutil, json, html, urllib.parse
from bs4 import BeautifulSoup

SRC = "/sessions/loving-pensive-clarke/mnt/VCE Textbook/2026 Yr12 Booklet/12 Booklet 2026"
BUILD = "/sessions/loving-pensive-clarke/mnt/outputs/site-build"
PUBLIC = os.path.join(BUILD, "public")
IMG_DIR = os.path.join(PUBLIC, "assets", "img")
PDF_DIR = os.path.join(PUBLIC, "assets", "pdf")
FILES_DIR = os.path.join(PUBLIC, "assets", "files")
SITE_TITLE = "VCE English Exam Preparation Guide"

for d in (PUBLIC, IMG_DIR, PDF_DIR, FILES_DIR):
    os.makedirs(d, exist_ok=True)

# ---------------- preprocess LaTeX ----------------
tex = open(os.path.join(SRC, "main.tex"), encoding="utf-8").read()
tex = re.sub(r"\\includepdf(\[[^\]]*\])?\s*\{([^}]+)\}",
             lambda m: "\n\nZZPDFEMBED %s ZZEND\n\n" % (m.group(2).strip() if m.group(2).strip().lower().endswith(".pdf") else m.group(2).strip() + ".pdf"), tex)
tex = re.sub(r"\\textattachfile\{([^}]+)\}\{([^}]+)\}",
             lambda m: r"\href{ZZFILE::%s}{%s}" % (m.group(1).strip(), m.group(2).strip()), tex)
tex = re.sub(r"\\addcontentsline\{exp\}\{examples\}\{([^}]+)\}",
             lambda m: "\n\nZZEXP %s ZZEXPEND\n\n" % m.group(1), tex)
open(os.path.join(BUILD, "_pre.tex"), "w", encoding="utf-8").write(tex)
os.system('cd "%s" && pandoc "%s/_pre.tex" -f latex -t html5 --section-divs --wrap=none -o "%s/_body.html"' % (SRC, BUILD, BUILD))
soup = BeautifulSoup(open(os.path.join(BUILD, "_body.html"), encoding="utf-8").read(), "html.parser")

# ---------------- assets ----------------
copied = set()
for img in soup.find_all("img"):
    base = os.path.basename(img.get("src", ""))
    sp = os.path.join(SRC, base)
    if os.path.exists(sp):
        if base not in copied:
            shutil.copy(sp, os.path.join(IMG_DIR, base)); copied.add(base)
        img["src"] = "assets/img/" + urllib.parse.quote(base)
        img["loading"] = "lazy"; img["class"] = ["content-img"]
n_imgs = len(copied)

for a in soup.find_all("a", href=True):
    if a["href"].startswith("ZZFILE::"):
        fn = a["href"].split("::", 1)[1]
        if os.path.exists(os.path.join(SRC, fn)):
            shutil.copy(os.path.join(SRC, fn), os.path.join(FILES_DIR, fn))
        a["href"] = "assets/files/" + urllib.parse.quote(fn)
        a["class"] = ["file-dl"]; a["download"] = ""

pdf_pat = re.compile(r"ZZPDFEMBED\s+(\S+?\.pdf)\s+ZZEND", re.I)
copied_pdfs = set()
for p in soup.find_all(["p", "div"]):
    m = pdf_pat.search(p.get_text())
    if not m: continue
    fname = m.group(1)
    if os.path.exists(os.path.join(SRC, fname)) and fname not in copied_pdfs:
        shutil.copy(os.path.join(SRC, fname), os.path.join(PDF_DIR, fname)); copied_pdfs.add(fname)
    enc = urllib.parse.quote(fname)
    p.replace_with(BeautifulSoup(
        '<div class="pdf-embed"><div class="pdf-embed-bar"><span class="pdf-name">%s</span>'
        '<a class="pdf-open" href="assets/pdf/%s" target="_blank" rel="noopener">Open in new tab &#8599;</a>'
        '<a class="pdf-dl" href="assets/pdf/%s" download>Download &#8595;</a></div>'
        '<iframe class="pdf-frame" src="assets/pdf/%s#view=FitH" loading="lazy" title="%s"></iframe></div>'
        % (html.escape(fname), enc, enc, enc, html.escape(fname)), "html.parser"))

for _t in soup.find_all("table"):
    if not _t.find("thead"):
        _t["class"] = _t.get("class", []) + ["no-thead"]

# paragraph breaks: LaTeX \\ inside paragraphs became <br>; give them real spacing
for _br in soup.find_all("br"):
    if _br.parent and _br.parent.name == "p":
        _sp = soup.new_tag("span"); _sp["class"] = "pbr"
        _br.replace_with(_sp)

# de-duplicate longtable header rows (LaTeX firsthead + continuation head)
for _t in soup.find_all("table"):
    _rows = _t.find_all("tr")
    while len(_rows) >= 2 and _rows[0].get_text("|", strip=True) and \
          _rows[0].get_text("|", strip=True) == _rows[1].get_text("|", strip=True):
        _rows[1].decompose()
        _rows = _t.find_all("tr")

exp_pat = re.compile(r"ZZEXP\s+(.+?)\s+ZZEXPEND")
exemplars = []
for _p in soup.find_all("p"):
    _m = exp_pat.search(_p.get_text())
    if _m:
        _s = _p.find_parent("section")
        exemplars.append({"title": _m.group(1).strip(), "id": _s.get("id") if _s else None})
        _p.decompose()

# ---------------- structure: parts -> chapters ----------------
def slugify(t):
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-") or "section"

parts = [s for s in soup.find_all("section", class_="level1") if s.find_parent("section") is None]

HOWTO = open(os.path.join(BUILD, "snippets/howto.html"), encoding="utf-8").read()
R2025 = open(os.path.join(BUILD, "snippets/report2025.html"), encoding="utf-8").read()

nav_items = []   # {num,title,file,chapters:[{title,file}],pages:[page dicts in order]}
all_pages = []   # linear order for prev/next: {file,title,content_fn,nav_key,chapter_file_or_None}
id_to_page = {}

part_meta = []
for i, sec in enumerate(parts, 1):
    h1 = sec.find("h1")
    title = h1.get_text(" ", strip=True) if h1 else "Part %d" % i
    part_meta.append({"idx": i, "title": title, "slug": slugify(title),
                      "file": "part-%02d-%s.html" % (i, slugify(title)), "sec": sec})

display_num = 0
for pm in part_meta:
    display_num += 1
    sec = pm["sec"]; hub = pm["file"]
    if pm["idx"] == 1:
        nav_items.append({"num": display_num, "title": "How to Use This Site", "file": hub, "chapters": []})
        all_pages.append({"file": hub, "title": "How to Use This Site", "html": HOWTO, "nav": hub})
        id_to_page[sec.get("id", "preface")] = hub
        continue
    children = sec.find_all("section", recursive=False)
    chapters = []
    used_cf = set()
    if len(children) >= 2:
        for j, ch in enumerate(children, 1):
            hh = ch.find(["h2", "h3", "h4"])
            ct = hh.get_text(" ", strip=True) if hh else "Section %d" % j
            cf = "p%02d-%s.html" % (pm["idx"], slugify(ct)[:60])
            if cf in used_cf:
                k = 2
                while "p%02d-%s-%d.html" % (pm["idx"], slugify(ct)[:60], k) in used_cf: k += 1
                cf = "p%02d-%s-%d.html" % (pm["idx"], slugify(ct)[:60], k)
            used_cf.add(cf)
            chapters.append({"title": ct, "file": cf, "sec": ch})
            for el in ch.find_all(id=True): id_to_page[el["id"]] = cf
            if ch.get("id"): id_to_page[ch["id"]] = cf
        for el in sec.find_all(id=True):
            if el["id"] not in id_to_page: id_to_page[el["id"]] = hub
        if sec.get("id"): id_to_page[sec["id"]] = hub
    else:
        for el in sec.find_all(id=True): id_to_page[el["id"]] = hub
        if sec.get("id"): id_to_page[sec["id"]] = hub
    nav_items.append({"num": display_num, "title": pm["title"], "file": hub,
                      "chapters": [{"title": c["title"], "file": c["file"]} for c in chapters]})
    all_pages.append({"file": hub, "title": pm["title"], "part": pm, "chapters": chapters, "nav": hub})
    for c in chapters:
        all_pages.append({"file": c["file"], "title": c["title"], "chapter": c,
                          "part": pm, "nav": hub})
    if pm["title"].startswith("Key Takeaways from the 2024"):
        display_num += 1
        f25 = "part-13-key-takeaways-from-the-2025-assessment-report.html"
        nav_items.append({"num": display_num, "title": "Key Takeaways from the 2025 Assessment Report",
                          "file": f25, "chapters": []})
        all_pages.append({"file": f25, "title": "Key Takeaways from the 2025 Assessment Report",
                          "html": R2025, "nav": f25})

for e in exemplars:
    e["url"] = (id_to_page.get(e["id"], "index.html") + "#" + e["id"]) if e["id"] else "index.html"

def rewrite_anchors(scope, current):
    for a in scope.find_all("a", href=True):
        if a["href"].startswith("#"):
            pg = id_to_page.get(a["href"][1:])
            if pg and pg != current: a["href"] = pg + a["href"]

# ---------------- nav / shell ----------------
def nav_html(active_nav, active_file):
    out = []
    for it in nav_items:
        num = "%02d" % it["num"]
        if it["chapters"]:
            is_open = " open" if it["file"] == active_nav else ""
            cls = ' class="active"' if active_file == it["file"] else ""
            subs = "".join('<li%s><a href="%s">%s</a></li>' %
                           (' class="active"' if c["file"] == active_file else "", c["file"], html.escape(c["title"]))
                           for c in it["chapters"])
            out.append('<li class="grp"><details%s><summary><a%s href="%s"><span class="num">%s</span>%s</a></summary>'
                       '<ul class="subnav">%s</ul></details></li>'
                       % (is_open, cls, it["file"], num, html.escape(it["title"]), subs))
        else:
            cls = ' class="active"' if it["file"] == active_file else ""
            out.append('<li%s><a href="%s"><span class="num">%s</span>%s</a></li>'
                       % (cls, it["file"], num, html.escape(it["title"])))
    return "\n".join(out)

def shell(title, active_nav, active_file, main_html, prevnext=""):
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s &middot; %s</title>
<link rel="stylesheet" href="assets/style.css?v=5">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="exam-banner" id="countdown" data-target="2026-10-27T09:00:00+11:00">
  <span class="eb-label">English exam &middot; Tue 27 October, 9:00 am</span>
  <span class="eb-time"><b id="cd-d">&ndash;</b> days <b id="cd-h">&ndash;</b> hrs <b id="cd-m">&ndash;</b> min <b id="cd-s">&ndash;</b> sec</span>
</div>
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
    <nav class="toc"><ol>%s</ol></nav>
    <div class="side-foot">South Oakleigh College &middot; 2026</div>
  </aside>
  <main class="content" id="main">
    %s
    %s
  </main>
</div>
<script src="assets/site.js?v=5"></script>
</body>
</html>""" % (html.escape(title), SITE_TITLE, nav_html(active_nav, active_file), main_html, prevnext)

def page_toc(scope):
    lis = []
    heads = scope.find_all(["h2", "h3", "h4", "h5"])
    for h in heads[1:] if heads else []:
        anc = h.find_parent("section")
        if anc and anc.get("id"):
            lis.append('<li class="lvl%s"><a href="#%s">%s</a></li>'
                       % (h.name[1], anc["id"], html.escape(h.get_text(" ", strip=True))))
    return ('<details class="page-toc" open><summary>On this page</summary><ul>%s</ul></details>' % "".join(lis)) if lis else ""

# ---------------- search index ----------------
search = []
for pg in all_pages:
    if "chapter" in pg:
        scope, part_title = pg["chapter"]["sec"], pg["part"]["title"]
    elif "part" in pg:
        scope, part_title = pg["part"]["sec"], pg["part"]["title"]
    else:
        search.append({"t": pg["title"], "p": pg["title"], "u": pg["file"]})
        continue
    if "chapters" in pg and pg["chapters"]:
        search.append({"t": pg["title"], "p": pg["title"], "u": pg["file"]})
        continue
    for h in scope.find_all(["h1", "h2", "h3", "h4", "h5"]):
        anc = h.find_parent("section")
        hid = anc.get("id") if anc else None
        search.append({"t": h.get_text(" ", strip=True), "p": part_title,
                       "u": pg["file"] + ("#" + hid if hid else "")})
json.dump(search, open(os.path.join(PUBLIC, "assets", "search.json"), "w", encoding="utf-8"), ensure_ascii=False)

# ---------------- write pages ----------------
for k, pg in enumerate(all_pages):
    prev_a = ('<a class="pn prev" href="%s"><span>&#8592; Previous</span><b>%s</b></a>'
              % (all_pages[k-1]["file"], html.escape(all_pages[k-1]["title"]))) if k else "<span></span>"
    next_a = ('<a class="pn next" href="%s"><span>Next &#8594;</span><b>%s</b></a>'
              % (all_pages[k+1]["file"], html.escape(all_pages[k+1]["title"]))) if k < len(all_pages)-1 else "<span></span>"
    pn = '<nav class="prevnext">%s%s</nav>' % (prev_a, next_a)
    num = next(it["num"] for it in nav_items if it["file"] == pg["nav"])

    if "html" in pg:
        body = pg["html"]
        body = re.sub(r'<div class="part-label">Part \d+</div>', '<div class="part-label">Part %02d</div>' % num, body)
    elif "chapters" in pg and pg["chapters"]:
        sec = pg["part"]["sec"]
        for c in pg["chapters"]: c["sec"].extract()
        rewrite_anchors(sec, pg["file"])
        h1 = sec.find("h1")
        if h1: h1.insert_before(BeautifulSoup('<div class="part-label">Part %02d</div>' % num, "html.parser"))
        cards = "".join('<a class="ch-card" href="%s"><span class="ch-num">%d</span><span>%s</span></a>'
                        % (c["file"], j+1, html.escape(c["title"])) for j, c in enumerate(pg["chapters"]))
        body = sec.decode() + '<h2 class="in-part-head">In this part</h2><div class="ch-list">%s</div>' % cards
    elif "chapter" in pg:
        sec = pg["chapter"]["sec"]
        rewrite_anchors(sec, pg["file"])
        hh = sec.find(["h2", "h3", "h4"])
        if hh: hh.name = "h1"
        crumb = ('<div class="part-label"><a href="%s">Part %02d &middot; %s</a></div>'
                 % (pg["part"]["file"], num, html.escape(pg["part"]["title"])))
        body = crumb + page_toc(sec) + sec.decode()
    else:
        sec = pg["part"]["sec"]
        rewrite_anchors(sec, pg["file"])
        h1 = sec.find("h1")
        if h1: h1.insert_before(BeautifulSoup('<div class="part-label">Part %02d</div>' % num, "html.parser"))
        body = page_toc(sec) + sec.decode()

    open(os.path.join(PUBLIC, pg["file"]), "w", encoding="utf-8").write(
        shell(pg["title"], pg["nav"], pg["file"], body, pn))

# ---------------- landing ----------------
BLURB = {
 "How to Use This Site": "Quick orientation: search, sections, practice exams and suggested study routes.",
 "Sunset Boulevard": "Billy Wilder's film — context, themes, quote banks, scene analyses, techniques, symbols and exemplar essays.",
 "Rainbow's End": "Jane Harrison's play — context, characters, themes, quotes and sample responses.",
 "Analytical Text Response Essays": "Planning, structure, and proofreading a text-response essay.",
 "Creating Texts": "Audience, purpose, personal journeys and practice stimuli.",
 "Analysing Argument": "Language analysis — written & visual, sample articles and essays.",
 "The Exam": "Format and strategies for addressing the requirements.",
 "Practice Exams": "Full practice papers and past exams.",
 "Exam Assessment Criteria": "How Sections A, B and C are marked.",
 "Exam Checklists": "Ready-reference checklists for exam day.",
 "Key Takeaways from the 2024 Assessment Report": "What VCAA assessors flagged in 2024, section by section.",
 "Key Takeaways from the 2025 Assessment Report": "What VCAA assessors flagged in 2025 — topic verbs, Framework choices and the interplay discriminator.",
 "Effectively Studying For Exams": "Study habits, schedules, recall and wellbeing.",
}
cards = "".join('<a class="card" href="%s"><div class="card-num">%02d</div><div class="card-body"><h3>%s</h3><p>%s</p></div></a>'
                % (it["file"], it["num"], html.escape(it["title"]), html.escape(BLURB.get(it["title"], "")))
                for it in nav_items)
landing = """
<section class="hero">
  <div class="hero-inner">
    <img class="hero-logo" src="assets/img/SOC%%20LOGO_VERTICAL.png" alt="South Oakleigh College logo">
    <div class="hero-badge">South Oakleigh College</div>
    <h1>VCE English<br>Exam Preparation Guide</h1>
    <p class="hero-sub">Units 3/4 English &middot; For the VCE English Cohort of 2026</p>
    <p class="hero-sub hero-sub2">Compiled by Mr. Morlin &middot; Version 4.2</p>
    <p class="hero-lede">Exemplar essays, thematic and character quote banks, scene analyses, argument-analysis frameworks, full practice exams, marking criteria and study strategies &mdash; the complete booklet, now browsable.</p>
    <div class="hero-cta"><a class="btn" href="%s">Start reading &#8594;</a></div>
  </div>
</section>
<h2 class="section-head">Contents</h2>
<div class="cards">%s</div>
<h2 class="section-head">Examples of high marking responses</h2>
<ul class="exp-list">%s</ul>
""" % (nav_items[0]["file"], cards,
       "".join('<li><a href="%s">%s</a></li>' % (e["url"], html.escape(e["title"])) for e in exemplars))
open(os.path.join(PUBLIC, "index.html"), "w", encoding="utf-8").write(shell("Home", "", "index.html", landing))

print("PAGES:", len(all_pages) + 1, "| PARTS:", len(nav_items), "| IMGS:", n_imgs, "| PDFS:", len(copied_pdfs),
      "| SEARCH:", len(search), "| EXEMPLARS:", len(exemplars))
for it in nav_items:
    print(" %02d %-46s %d chapters" % (it["num"], it["title"][:46], len(it["chapters"])))
