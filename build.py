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
def copy_if_changed(a, b):
    try:
        if os.path.exists(b) and os.path.getsize(b) == os.path.getsize(a): return
    except OSError: pass
    shutil.copy(a, b)

SITE_TITLE = "VCE English Exam Preparation Guide"

for d in (PUBLIC, IMG_DIR, PDF_DIR, FILES_DIR):
    os.makedirs(d, exist_ok=True)

# ---------------- preprocess LaTeX ----------------
tex = open(os.path.join(SRC, "main.tex"), encoding="utf-8").read()
# replace the exe-download generator text with a pointer to the web tool
tex = re.sub(r"(\\section\{English Exam Generator\}).*?(?=\\clearpage)",
             r"\1\nThe exam generator now runs directly on this site. It assembles a complete three-section practice paper from the question banks and downloads it as a Word document in the authentic task-book format.\n\n\\href{ZZFILE::__EXAMGEN__}{Open the Exam Generator}\n\nOfficial past VCE English examinations and examiner reports are published by the VCAA:\n\n\\href{https://www.vcaa.vic.edu.au/assessment/vce/examination-specifications-past-examinations-and-examination-reports/english}{Past VCE English examinations (VCAA)}\n\n", tex, flags=re.S)

# script section: link out instead of hosting the PDF
tex = tex.replace("Click the link below to open the Script:\\\\  \n\\textattachfile{SBScript.pdf}{Open SBScript.pdf}",
                  "The full script is available online:\n\n\\href{https://www.dailyscript.com/scripts/sunset_bld_3_21_49.html}{Read the Sunset Boulevard script at Daily Script}")
tex = re.sub(r"\\textattachfile\{SBScript\.pdf\}\{[^}]*\}",
             r"\\href{https://www.dailyscript.com/scripts/sunset_bld_3_21_49.html}{Read the Sunset Boulevard script at Daily Script}", tex)

# remove the seven copyrighted practice exam sections (site keeps the generator instead)
tex = re.sub(r"\\section\{Practice Exam I\}.*?(?=\\section\{English Exam Generator\})", "", tex, flags=re.S)

tex = re.sub(r"\\includepdf(\[[^\]]*\])?\s*\{([^}]+)\}",
             lambda m: "\n\nZZPDFEMBED %s ZZEND\n\n" % (m.group(2).strip() if m.group(2).strip().lower().endswith(".pdf") else m.group(2).strip() + ".pdf"), tex)
tex = re.sub(r"\\textattachfile\{([^}]+)\}\{([^}]+)\}",
             lambda m: r"\href{ZZFILE::%s}{%s}" % (m.group(1).strip(), m.group(2).strip()), tex)
tex = re.sub(r"\\addcontentsline\{exp\}\{examples\}\{([^}]+)\}",
             lambda m: "\n\nZZEXP %s ZZEXPEND\n\n" % m.group(1), tex)
open(os.path.join(BUILD, "_pre.tex"), "w", encoding="utf-8").write(tex)
os.system('cd "%s" && pandoc "%s/_pre.tex" -f latex -t html5 --section-divs --wrap=none -o "%s/_body.html"' % (SRC, BUILD, BUILD))
try:
    import lxml  # noqa
    _PARSER = "lxml"
except ImportError:
    _PARSER = "html.parser"
soup = BeautifulSoup(open(os.path.join(BUILD, "_body.html"), encoding="utf-8").read(), _PARSER)

# ---------------- assets ----------------
copied = set()
for img in soup.find_all("img"):
    base = os.path.basename(img.get("src", ""))
    sp = os.path.join(SRC, base)
    if os.path.exists(sp):
        if base not in copied:
            copy_if_changed(sp, os.path.join(IMG_DIR, base)); copied.add(base)
        img["src"] = "assets/img/" + urllib.parse.quote(base)
        img["loading"] = "lazy"; img["class"] = ["content-img"]
n_imgs = len(copied)
# favicon + social logo (no-space filename)
try:
    from PIL import Image
    _logo = Image.open(os.path.join(SRC, "SOC LOGO_VERTICAL.png")).convert("RGBA")
    _bgw = Image.new("RGBA", _logo.size, (255, 255, 255, 255))
    _bgw.paste(_logo, (0, 0), _logo)
    _sq = _bgw.convert("RGB")
    _w, _h = _sq.size
    _side = max(_w, _h)
    _canvas = Image.new("RGB", (_side, _side), (255, 255, 255))
    _canvas.paste(_sq, ((_side - _w) // 2, (_side - _h) // 2))
    _canvas.resize((48, 48)).save(os.path.join(PUBLIC, "assets", "favicon.png"))
    _canvas.resize((180, 180)).save(os.path.join(PUBLIC, "assets", "apple-touch-icon.png"))
    _canvas.resize((512, 512)).save(os.path.join(IMG_DIR, "soc-logo.png"))
except Exception as _e:
    print("icon generation skipped:", _e)

for a in soup.find_all("a", href=True):
    if a["href"] == "ZZFILE::__EXAMGEN__":
        a["href"] = "exam-generator.html"
        a["class"] = ["btn-inline"]
        continue
    if a["href"].startswith("ZZFILE::"):
        fn = a["href"].split("::", 1)[1]
        if os.path.exists(os.path.join(SRC, fn)):
            copy_if_changed(os.path.join(SRC, fn), os.path.join(FILES_DIR, fn))
        a["href"] = "assets/files/" + urllib.parse.quote(fn)
        a["class"] = ["file-dl"]; a["download"] = ""

pdf_pat = re.compile(r"ZZPDFEMBED\s+(\S+?\.pdf)\s+ZZEND", re.I)
copied_pdfs = set()
for p in soup.find_all(["p", "div"]):
    m = pdf_pat.search(p.get_text())
    if not m: continue
    fname = m.group(1)
    if os.path.exists(os.path.join(SRC, fname)) and fname not in copied_pdfs:
        copy_if_changed(os.path.join(SRC, fname), os.path.join(PDF_DIR, fname)); copied_pdfs.add(fname)
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
    for _ci, c in enumerate(chapters, 1):
        all_pages.append({"file": c["file"], "title": c["title"], "chapter": c,
                          "part": pm, "nav": hub, "chidx": _ci, "chtotal": len(chapters)})
    if pm["title"].startswith("Key Takeaways from the 2024"):
        display_num += 1
        f25 = "part-13-key-takeaways-from-the-2025-assessment-report.html"
        chs25 = [("General Exam Advice", "r25-general"),
                 ("Section A: Analytical Response to a Text", "r25-section-a"),
                 ("Section B: Creating a Text", "r25-section-b"),
                 ("Section C: Analysis of Argument and Language", "r25-section-c"),
                 ("Priority Checklist for 2026", "r25-checklist")]
        ch_pages = [{"title": t, "file": sn + ".html",
                     "html": open(os.path.join(BUILD, "snippets", sn + ".html"), encoding="utf-8").read()}
                    for t, sn in chs25]
        hub_html = open(os.path.join(BUILD, "snippets", "r25-hub.html"), encoding="utf-8").read()
        hub_html += '<h2 class="in-part-head">In this part</h2><div class="ch-list">%s</div>' % "".join(
            '<a class="ch-card" href="%s"><span class="ch-num">%d</span><span>%s</span></a>'
            % (c["file"], j + 1, html.escape(c["title"])) for j, c in enumerate(ch_pages))
        nav_items.append({"num": display_num, "title": "Key Takeaways from the 2025 Assessment Report",
                          "file": f25, "chapters": [{"title": c["title"], "file": c["file"]} for c in ch_pages]})
        all_pages.append({"file": f25, "title": "Key Takeaways from the 2025 Assessment Report",
                          "html": hub_html, "nav": f25})
        for c in ch_pages:
            all_pages.append({"file": c["file"], "title": c["title"], "html": c["html"], "nav": f25})

VOCAB_HTML = open(os.path.join(BUILD, "snippets", "vocab.html"), encoding="utf-8").read()
P06 = "part-06-analysing-argument.html"
for _it in nav_items:
    if _it["file"] == P06:
        _it["chapters"].append({"title": "High-Scoring Vocabulary Bank", "file": "vocabulary.html"})
for _pg in all_pages:
    if _pg["file"] == P06 and "chapters" in _pg:
        _pg["chapters"].append({"title": "High-Scoring Vocabulary Bank", "file": "vocabulary.html"})
_last6 = max(i for i, p in enumerate(all_pages) if p.get("nav") == P06)
all_pages.insert(_last6 + 1, {"file": "vocabulary.html", "title": "High-Scoring Vocabulary Bank",
                              "html": VOCAB_HTML, "nav": P06})

for e in exemplars:
    e["url"] = (id_to_page.get(e["id"], "index.html") + "#" + e["id"]) if e["id"] else "index.html"


# ================= study tools =================
def _clean(t): return re.sub(r"\s+", " ", t).strip()

def _heading_chain(el, stop):
    chain = []
    sec = el.find_parent("section")
    while sec is not None and sec is not stop.parent:
        hh = sec.find(["h1","h2","h3","h4","h5"], recursive=False) or sec.find(["h2","h3","h4","h5"])
        if hh: chain.append(_clean(hh.get_text()))
        if sec is stop: break
        sec = sec.find_parent("section")
    return list(reversed(chain))

flashcards = []
for pg in all_pages:
    if "chapter" not in pg or "quote-bank" not in pg["file"]: continue
    text_name = pg["part"]["title"]
    root = pg["chapter"]["sec"]
    for li in root.find_all("li"):
        q = _clean(li.get_text(" "))
        if len(q) < 20 or li.find("ul"): continue
        chain = _heading_chain(li, root)
        cat = " \u00b7 ".join(c for c in chain[1:] if c) or chain[0] if chain else pg["title"]
        flashcards.append({"q": q, "cat": (chain[0] + " \u00b7 " + cat) if len(chain) > 1 else pg["title"],
                           "text": text_name})

topics_data = {}
for pg in all_pages:
    if "chapter" not in pg or "practice-analytical-text-response-topics" not in pg["file"]: continue
    tname = pg["part"]["title"]
    lines = [ _clean(x) for x in pg["chapter"]["sec"].get_text("\n").split("\n") ]
    out, cur = [], None
    for ln in lines:
        m = re.match(r"^(\d+)\.\s+(.*)", ln)
        if m:
            if cur: out.append(_clean(cur))
            cur = m.group(2)
        elif cur is not None and ln and not ln.lower().startswith(("topics from", "practice analytical")):
            if len(ln) < 120: cur += " " + ln
            else:
                out.append(_clean(cur)); cur = None
    if cur: out.append(_clean(cur))
    topics_data.setdefault(tname, [])
    topics_data[tname] += [t for t in out if len(t) > 25]

glossary = []
for pg in all_pages:
    if "chapter" not in pg: continue
    if pg["file"] == "p02-film-techniques.html": srcname = "Film technique"
    elif pg["file"] == "p06-analysing-written-language.html": srcname = "Persuasive technique"
    else: continue
    tbl = pg["chapter"]["sec"].find("table")
    if not tbl: continue
    for tr in tbl.find_all("tr")[1:]:
        cells = [_clean(c.get_text(" ")) for c in tr.find_all(["td","th"])]
        if len(cells) >= 2 and cells[0] and len(cells[0]) < 60:
            d = cells[1] + ((" \u2014 " + cells[2]) if len(cells) > 2 and cells[2] else "")
            glossary.append({"term": cells[0], "def": d, "src": srcname})
glossary.sort(key=lambda g: g["term"].lower())

TOOL_LABEL = '<div class="part-label">Study Tools</div>'
fc_page = TOOL_LABEL + """<h1>Quote Flashcards</h1>
<p class="lede">Test yourself on the quote banks. Read the quote, recall who says it and which theme it serves, then flip.</p>
<div class="tool-bar">
  <select id="fc-text"><option value="">Both texts</option></select>
  <button id="fc-shuffle">Shuffle</button>
  <span class="tool-count" id="fc-count"></span>
</div>
<div class="fc-card" id="fc-card" tabindex="0">
  <div class="fc-inner">
    <div class="fc-face"><div class="fc-front" id="fc-front"></div><div class="fc-hint">Click card to flip</div></div>
    <div class="fc-face fc-back-face"><div class="fc-back" id="fc-back"></div></div>
  </div>
</div>
<div class="tool-bar">
  <button id="fc-prev">&#8592; Previous</button>
  <button id="fc-flip">Flip</button>
  <button id="fc-next">Next &#8594;</button>
</div>
<script>window.FLASHCARDS = %s;</script>
<script>
(function(){
  var all = window.FLASHCARDS, deck = [], i = 0, flipped = false;
  var texts = {}; all.forEach(function(c){ texts[c.text] = 1; });
  var sel = document.getElementById('fc-text');
  Object.keys(texts).forEach(function(t){ var o = document.createElement('option'); o.value = t; o.textContent = t; sel.appendChild(o); });
  function shuffle(a){ for (var j = a.length - 1; j > 0; j--){ var k = Math.floor(Math.random() * (j + 1)); var tmp = a[j]; a[j] = a[k]; a[k] = tmp; } }
  function rebuild(){ deck = all.filter(function(c){ return !sel.value || c.text === sel.value; }); shuffle(deck); i = 0; show(); }
  function show(){
    if (!deck.length) return;
    flipped = false;
    document.getElementById('fc-card').classList.remove('flipped');
    document.getElementById('fc-front').textContent = deck[i].q;
    document.getElementById('fc-back').textContent = deck[i].text + ' \u2014 ' + deck[i].cat;
    document.getElementById('fc-count').textContent = (i + 1) + ' / ' + deck.length;
  }
  function flip(){ flipped = !flipped; document.getElementById('fc-card').classList.toggle('flipped', flipped); }
  document.getElementById('fc-card').addEventListener('click', flip);
  document.getElementById('fc-flip').addEventListener('click', flip);
  document.getElementById('fc-next').addEventListener('click', function(){ i = (i + 1) %% deck.length; show(); });
  document.getElementById('fc-prev').addEventListener('click', function(){ i = (i - 1 + deck.length) %% deck.length; show(); });
  document.getElementById('fc-shuffle').addEventListener('click', rebuild);
  sel.addEventListener('change', rebuild);
  rebuild();
})();
</script>""" % json.dumps(flashcards, ensure_ascii=False)

tp_page = TOOL_LABEL + """<h1>Practice Topics &amp; Essay Timer</h1>
<p class="lede">Draw a random analytical topic and write against the clock, exam-style.</p>
<div class="tool-bar">
  <select id="tp-text"></select>
  <button id="tp-draw">Draw a topic</button>
  <a id="tp-mark" href="#" style="display:none;font-family:var(--sans);font-weight:700;background:var(--accent);color:#fff;padding:9px 16px;border-radius:9px">Mark my essay &#8594;</a>
</div>
<div class="tp-topic" id="tp-topic">Press &ldquo;Draw a topic&rdquo; to begin.</div>
<div class="timer-wrap">
  <div class="timer" id="timer">60:00</div>
  <div class="tool-bar">
    <select id="t-mins"><option value="60">60 min (exam section)</option><option value="45">45 min</option><option value="30">30 min</option><option value="20">20 min (plan only)</option></select>
    <button id="t-start">Start</button>
    <button id="t-pause" disabled>Pause</button>
    <button id="t-reset">Reset</button>
  </div>
</div>
<script>window.TOPICS = %s;</script>
<script>
(function(){
  var T = window.TOPICS, sel = document.getElementById('tp-text');
  var names = Object.keys(T);
  var o0 = document.createElement('option'); o0.value = ''; o0.textContent = 'Either text'; sel.appendChild(o0);
  names.forEach(function(n){ var o = document.createElement('option'); o.value = n; o.textContent = n + ' (' + T[n].length + ' topics)'; sel.appendChild(o); });
  document.getElementById('tp-draw').addEventListener('click', function(){
    var pool = [];
    names.forEach(function(n){ if (!sel.value || sel.value === n) T[n].forEach(function(t){ pool.push({n: n, t: t}); }); });
    var pick = pool[Math.floor(Math.random() * pool.length)];
    document.getElementById('tp-topic').textContent = '[' + pick.n + '] ' + pick.t;
    var mk = document.getElementById('tp-mark');
    mk.href = 'marker.html?section=a&topic=' + encodeURIComponent(pick.t);
    mk.style.display = '';
  });
  var total = 3600, left = 3600, iv = null;
  var disp = document.getElementById('timer'), start = document.getElementById('t-start'),
      pause = document.getElementById('t-pause'), reset = document.getElementById('t-reset'),
      mins = document.getElementById('t-mins');
  function fmt(s){ var m = Math.floor(s / 60), x = s %% 60; return m + ':' + (x < 10 ? '0' : '') + x; }
  function draw(){ disp.textContent = fmt(left); disp.classList.toggle('t-low', left <= 300 && left > 0); }
  function done(){ clearInterval(iv); iv = null; disp.textContent = "Time's up!"; disp.classList.add('t-done'); start.disabled = false; pause.disabled = true; }
  start.addEventListener('click', function(){
    if (iv) return;
    if (left <= 0){ left = total; }
    disp.classList.remove('t-done');
    iv = setInterval(function(){ left--; if (left <= 0){ done(); return; } draw(); }, 1000);
    start.disabled = true; pause.disabled = false;
  });
  pause.addEventListener('click', function(){ clearInterval(iv); iv = null; start.disabled = false; pause.disabled = true; });
  reset.addEventListener('click', function(){ clearInterval(iv); iv = null; total = left = parseInt(mins.value, 10) * 60; disp.classList.remove('t-done'); draw(); start.disabled = false; pause.disabled = true; });
  mins.addEventListener('change', function(){ if (!iv){ total = left = parseInt(mins.value, 10) * 60; draw(); } });
  draw();
})();
</script>""" % json.dumps(topics_data, ensure_ascii=False)

gl_items = "".join('<div class="gl-item" data-term="%s"><b>%s</b> <span class="gl-src">%s</span><p>%s</p></div>'
                   % (html.escape(g["term"].lower()), html.escape(g["term"]), html.escape(g["src"]), html.escape(g["def"]))
                   for g in glossary)
gl_page = TOOL_LABEL + """<h1>Glossary of Techniques</h1>
<p class="lede">Every film and persuasive technique from the guide in one alphabetical reference.</p>
<div class="tool-bar"><input id="gl-filter" type="search" placeholder="Filter terms&hellip;" style="flex:1;max-width:340px"></div>
<div class="gl-list" id="gl-list">%s</div>
<script>
(function(){
  var inp = document.getElementById('gl-filter'), items = document.querySelectorAll('.gl-item');
  inp.addEventListener('input', function(){
    var q = inp.value.trim().toLowerCase();
    items.forEach(function(it){ it.style.display = !q || it.textContent.toLowerCase().indexOf(q) > -1 ? '' : 'none'; });
  });
})();
</script>""" % gl_items

qz_page = TOOL_LABEL + """<h1>Technique Quiz</h1>
<p class="lede">A definition appears &mdash; pick the technique it describes. Ten questions per round, drawn from the glossary.</p>
<div class="tool-bar">
  <span class="tool-count" id="qz-progress" style="margin-left:0"></span>
  <span class="tool-count" id="qz-score"></span>
</div>
<div class="qz-box">
  <div class="qz-def" id="qz-def"></div>
  <div class="qz-opts" id="qz-opts"></div>
  <div class="qz-feedback" id="qz-feedback"></div>
</div>
<div class="tool-bar">
  <button id="qz-next" style="display:none">Next question &#8594;</button>
  <button id="qz-restart" style="display:none">New round</button>
</div>
<script>window.QUIZ = %s;</script>
<script>
(function(){
  var all = window.QUIZ, round = [], qi = 0, score = 0, answered = false;
  function shuffle(a){ for (var j = a.length - 1; j > 0; j--){ var k = Math.floor(Math.random() * (j + 1)); var t = a[j]; a[j] = a[k]; a[k] = t; } return a; }
  function start(){
    round = shuffle(all.slice()).slice(0, 10); qi = 0; score = 0;
    document.getElementById('qz-restart').style.display = 'none';
    ask();
  }
  function ask(){
    answered = false;
    var q = round[qi];
    var pool = shuffle(all.filter(function(g){ return g.term !== q.term; })).slice(0, 3);
    var opts = shuffle(pool.concat([q]));
    document.getElementById('qz-progress').textContent = 'Question ' + (qi + 1) + ' of ' + round.length;
    document.getElementById('qz-score').textContent = 'Score: ' + score;
    document.getElementById('qz-def').textContent = q.def;
    document.getElementById('qz-feedback').textContent = '';
    document.getElementById('qz-next').style.display = 'none';
    var box = document.getElementById('qz-opts'); box.innerHTML = '';
    opts.forEach(function(o){
      var b = document.createElement('button'); b.className = 'qz-opt'; b.textContent = o.term;
      b.addEventListener('click', function(){ pick(b, o, q); });
      box.appendChild(b);
    });
  }
  function pick(btn, o, q){
    if (answered) return;
    answered = true;
    var btns = document.querySelectorAll('.qz-opt');
    btns.forEach(function(b){ b.disabled = true; if (b.textContent === q.term) b.classList.add('qz-right'); });
    if (o.term === q.term){ score++; document.getElementById('qz-feedback').textContent = 'Correct.'; }
    else { btn.classList.add('qz-wrong'); document.getElementById('qz-feedback').textContent = 'Not quite \u2014 this one is \u201c' + q.term + '\u201d.'; }
    document.getElementById('qz-score').textContent = 'Score: ' + score;
    if (qi < round.length - 1){ document.getElementById('qz-next').style.display = ''; }
    else {
      document.getElementById('qz-feedback').textContent += ' Round over: ' + score + ' / ' + round.length + '.';
      document.getElementById('qz-restart').style.display = '';
    }
  }
  document.getElementById('qz-next').addEventListener('click', function(){ qi++; ask(); });
  document.getElementById('qz-restart').addEventListener('click', start);
  start();
})();
</script>""" % json.dumps([{"term": g["term"], "def": g["def"]} for g in glossary], ensure_ascii=False)

EXAMGEN = json.load(open(os.path.join(BUILD, "examgen", "examgen.json"), encoding="utf-8"))
SLOTCFG = json.load(open(os.path.join(BUILD, "examgen", "slots.json"), encoding="utf-8"))
eg_page = TOOL_LABEL + """<h1>Exam Generator</h1>
<p class="lede">Generate a unique three-section practice examination on the spot &mdash; the complete task book as a Word document, identical in format to the real paper: cover page, instructions, Section A topics for both texts, a Creating Texts prompt with stimulus material, Section C source material and the assessment criteria.</p>
<div class="tool-bar">
  <button id="eg-go">Generate exam &#8595;</button>
  <span class="tool-count" id="eg-note"></span>
</div>
<p style="font-family:var(--sans);font-size:13.5px;color:var(--muted)">Every exam is assembled fresh from the question banks the moment you click. Print it and sit it under timed conditions &mdash; then mark it against the <a href="part-09-exam-assessment-criteria.html">assessment criteria</a> or with the <a href="marker.html">Essay Marker</a>.</p>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>
<script>window.EG_DATA = %s; window.EG_SLOTS = %s;</script>
<script>
(function(){
  var D = window.EG_DATA, S = window.EG_SLOTS, note = document.getElementById('eg-note');
  function pick(a){ return a[Math.floor(Math.random() * a.length)]; }
  function two(a){ var x = pick(a), y = pick(a), t = 0;
    while (y === x && a.length > 1 && t++ < 12) y = pick(a);
    return [x, y]; }
  function xesc(s){ return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
  function fill(s){ return s.split(String.fromCharCode(10)).map(xesc)
    .join('</w:t><w:br/><w:t xml:space="preserve">'); }
  function loadImg(url){ return new Promise(function(res, rej){
    var im = new Image(); im.onload = function(){ res(im); }; im.onerror = rej; im.src = url; }); }
  function slotPng(im, px){ var c = document.createElement('canvas');
    c.width = px[0]; c.height = px[1];
    var g = c.getContext('2d');
    g.fillStyle = '#ffffff'; g.fillRect(0, 0, c.width, c.height);
    if (im){ var r = Math.min(c.width / im.width, c.height / im.height);
      var w = im.width * r, h = im.height * r;
      g.drawImage(im, (c.width - w) / 2, (c.height - h) / 2, w, h); }
    return c.toDataURL('image/png').split(',')[1]; }
  document.getElementById('eg-go').addEventListener('click', function(){
    note.textContent = 'Assembling exam\u2026';
    fetch('assets/exam/web-template.docx').then(function(r){
      if (!r.ok) throw new Error('template fetch failed');
      return r.arrayBuffer();
    }).then(function(buf){ return JSZip.loadAsync(buf); }).then(function(zip){
      return zip.file('word/document.xml').async('string').then(function(xml){
        var sb = two(D.sb), re = two(D.re), b = pick(D.b),
            c = pick(D.c.filter(function(x){ return x.imgs.length; }));
        var repl = { '{A7}': sb[0], '{A8}': sb[1], '{A10}': re[0], '{A11}': re[1],
                     '{G9}': b.title || '', '{G11}': b.s1 || '', '{G15}': b.s3 || '' };
        Object.keys(repl).forEach(function(k){ xml = xml.split(k).join(fill(repl[k])); });
        zip.file('word/document.xml', xml);
        var jobs = [];
        function put(slot, url){
          jobs.push((url ? loadImg(url) : Promise.resolve(null)).then(function(im){
            zip.file(S.slots[slot], slotPng(im, S.px[slot]), { base64: true });
          }));
        }
        put('g13', b.img ? 'assets/exam/b/' + b.img : null);
        ['n13', 'n16', 'n17'].forEach(function(slot, k){
          put(slot, c.imgs[k] ? 'assets/exam/c/' + encodeURIComponent(c.imgs[k]) : null);
        });
        return Promise.all(jobs).then(function(){
          return zip.generateAsync({ type: 'blob',
            mimeType: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' });
        });
      });
    }).then(function(blob){
      var id = Math.random().toString(36).slice(2, 7).toUpperCase();
      var a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = 'Practice-Exam-' + id + '.docx';
      document.body.appendChild(a); a.click(); a.remove();
      note.textContent = 'Downloaded Practice-Exam-' + id + '.docx';
    }).catch(function(e){ note.textContent = 'Generation failed: ' + e; });
  });
})();
</script>""" % (json.dumps(EXAMGEN, ensure_ascii=False), json.dumps(SLOTCFG))

hub_tools = TOOL_LABEL + """<h1>Study Tools</h1>
<p class="lede">Interactive revision tools built from the guide&rsquo;s own content.</p>
<h2 class="in-part-head">Tools</h2>
<div class="ch-list">
  <a class="ch-card" href="flashcards.html"><span class="ch-num">1</span><span>Quote Flashcards</span></a>
  <a class="ch-card" href="practice-topics.html"><span class="ch-num">2</span><span>Practice Topics &amp; Essay Timer</span></a>
  <a class="ch-card" href="glossary.html"><span class="ch-num">3</span><span>Glossary of Techniques</span></a>
  <a class="ch-card" href="marker.html"><span class="ch-num">4</span><span>Essay Marker</span></a>
  <a class="ch-card" href="technique-quiz.html"><span class="ch-num">5</span><span>Technique Quiz</span></a>
  <a class="ch-card" href="exam-generator.html"><span class="ch-num">6</span><span>Exam Generator</span></a>
</div>
<p style="font-family:var(--sans);font-size:14px;color:var(--muted)">The Essay Marker gives a calibrated score out of 10 with criteria-based feedback for Sections A, B and C. It needs an AI connection: a free GitHub Models token or an Anthropic API key (set up inside the tool; stored only in your browser).</p>"""

display_num += 1
tools_num = display_num
nav_items.append({"num": tools_num, "title": "Study Tools", "file": "study-tools.html",
                  "chapters": [{"title": "Quote Flashcards", "file": "flashcards.html"},
                               {"title": "Practice Topics & Essay Timer", "file": "practice-topics.html"},
                               {"title": "Glossary of Techniques", "file": "glossary.html"},
                               {"title": "Essay Marker", "file": "marker.html"},
                               {"title": "Technique Quiz", "file": "technique-quiz.html"},
                               {"title": "Exam Generator", "file": "exam-generator.html"}]})
all_pages.append({"file": "study-tools.html", "title": "Study Tools", "html": hub_tools, "nav": "study-tools.html"})
all_pages.append({"file": "flashcards.html", "title": "Quote Flashcards", "html": fc_page, "nav": "study-tools.html"})
all_pages.append({"file": "practice-topics.html", "title": "Practice Topics & Essay Timer", "html": tp_page, "nav": "study-tools.html"})
all_pages.append({"file": "glossary.html", "title": "Glossary of Techniques", "html": gl_page, "nav": "study-tools.html"})
all_pages.append({"file": "technique-quiz.html", "title": "Technique Quiz", "html": qz_page, "nav": "study-tools.html"})
all_pages.append({"file": "exam-generator.html", "title": "Exam Generator", "html": eg_page, "nav": "study-tools.html"})
_ed = os.path.join(PUBLIC, "assets", "exam")
for _sub in ("b", "c"):
    os.makedirs(os.path.join(_ed, _sub), exist_ok=True)
    for _f in os.listdir(os.path.join(BUILD, "examgen", _sub)):
        copy_if_changed(os.path.join(BUILD, "examgen", _sub, _f), os.path.join(_ed, _sub, _f))
copy_if_changed(os.path.join(BUILD, "examgen", "web-template.docx"), os.path.join(_ed, "web-template.docx"))
print("TOOLS: flashcards=%d topics=%s glossary=%d" % (len(flashcards), {k: len(v) for k, v in topics_data.items()}, len(glossary)))

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
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;0,8..60,700;1,8..60,400&family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
<link rel="icon" type="image/png" href="assets/favicon.png">
<link rel="apple-touch-icon" href="assets/apple-touch-icon.png">
<meta property="og:site_name" content="VCE English Exam Preparation Guide">
<meta property="og:title" content="%s">
<meta property="og:description" content="South Oakleigh College Units 3/4 English exam preparation guide - texts, essays, practice exams and study tools.">
<meta property="og:image" content="https://nmo-soc.github.io/VCE-English-Guide/assets/img/soc-logo.png">
<script>try{if(localStorage.getItem('siteTheme')==='dark')document.documentElement.setAttribute('data-theme','dark');}catch(e){}</script>
<link rel="stylesheet" href="assets/style.css?v=10">
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
      <img class="brand-logo" src="assets/img/soc-logo.png" alt="South Oakleigh College">
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
<script src="assets/site.js?v=10"></script>
<script data-goatcounter="https://nmo.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
</body>
</html>""" % (html.escape(title), SITE_TITLE, html.escape(title), nav_html(active_nav, active_file), main_html, prevnext)

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
        _txt = re.sub(r"\s+", " ", BeautifulSoup(pg["html"], "html.parser").get_text(" "))[:1500]
        search.append({"t": pg["title"], "p": pg["title"], "u": pg["file"], "b": _txt.strip()})
        continue
    if "chapters" in pg and pg["chapters"]:
        search.append({"t": pg["title"], "p": pg["title"], "u": pg["file"]})
        continue
    for h in scope.find_all(["h1", "h2", "h3", "h4", "h5"]):
        anc = h.find_parent("section")
        hid = anc.get("id") if anc else None
        body = ""
        if anc:
            import copy as _copy
            _cl = _copy.copy(anc)
            for _sub in _cl.find_all("section"): _sub.decompose()
            body = re.sub(r"\s+", " ", _cl.get_text(" "))[:1500].strip()
        search.append({"t": h.get_text(" ", strip=True), "p": part_title,
                       "u": pg["file"] + ("#" + hid if hid else ""), "b": body})
search.append({"t": "Essay Marker", "p": "Study Tools", "u": "marker.html",
               "b": "ai essay marker score feedback section a b c criteria calibrated marking precision mode second opinion handwriting transcription"})
copy_if_changed(os.path.join(BUILD, "marker.html"), os.path.join(PUBLIC, "marker.html"))
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
        for c in pg["chapters"]:
            if "sec" in c: c["sec"].extract()
        rewrite_anchors(sec, pg["file"])
        h1 = sec.find("h1")
        if h1: h1.insert_before(BeautifulSoup('<div class="part-label">Part %02d</div>' % num, "html.parser"))
        cards = "".join('<a class="ch-card" href="%s"><span class="ch-num">%d</span><span>%s</span></a>'
                        % (c["file"], j+1, html.escape(c["title"])) for j, c in enumerate(pg["chapters"]))
        body = sec.decode() + '<h2 class="in-part-head">In this part</h2><div class="ch-list">%s</div>' % cards
    elif pg["file"] == "p08-english-exam-generator.html":
        crumb = ('<div class="part-label"><a href="%s">Part %02d &middot; %s</a>'
                 '<span class="ch-pos">Chapter %d of %d</span></div>'
                 % (pg["part"]["file"], num, html.escape(pg["part"]["title"]),
                    pg.get("chidx", 8), pg.get("chtotal", 8)))
        body = crumb + """<h1>English Exam Generator</h1>
<p>The exam generator now runs directly on this site &mdash; no download needed. It assembles a full three-section practice paper from the question banks: a random analytical topic for your text, a Creating Texts prompt with stimulus material, and an Analysing Argument source. Each generated paper downloads as a Word document identical in format to the real exam task book.</p>
<p><a class="btn" style="background:var(--accent);color:#fff" href="exam-generator.html">Open the Exam Generator &#8594;</a></p>
<p style="font-family:var(--sans);font-size:13.5px;color:var(--muted)">The original desktop version (Windows) is still available:
<a class="file-dl" href="assets/files/ExamGenerator.exe" download>ExamGenerator.exe</a></p>"""
    elif "chapter" in pg:
        sec = pg["chapter"]["sec"]
        if "quote-bank" in pg["file"]:
            sec["class"] = sec.get("class", []) + ["quotes-page"]
        if "exemplar" in pg["file"] or "sample-" in pg["file"]:
            sec["class"] = sec.get("class", []) + ["exemplar-page"]
        rewrite_anchors(sec, pg["file"])
        hh = sec.find(["h2", "h3", "h4"])
        if hh: hh.name = "h1"
        pos = ('<span class="ch-pos">Chapter %d of %d</span>' % (pg["chidx"], pg["chtotal"])) if pg.get("chidx") else ""
        crumb = ('<div class="part-label"><a href="%s">Part %02d &middot; %s</a>%s</div>'
                 % (pg["part"]["file"], num, html.escape(pg["part"]["title"]), pos))
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
ICONS = {
 "How to Use This Site": '<circle cx="12" cy="12" r="9"/><path d="M12 8l3 7-7-3z"/>',
 "Sunset Boulevard": '<rect x="3" y="8" width="18" height="12" rx="2"/><path d="M3 8l3-4 4 3 4-3 4 3 3-2v3"/>',
 "Rainbow\u2019s End": '<path d="M4 17a8 8 0 0 1 16 0"/><path d="M8 17a4 4 0 0 1 8 0"/>',
 "Analytical Text Response Essays": '<path d="M14 3l7 7-11 11H3v-7z"/><path d="M12 5l7 7"/>',
 "Creating Texts": '<path d="M4 20l1-5L16 4l4 4L9 19z"/><path d="M14 6l4 4"/>',
 "Analysing Argument": '<path d="M21 12a8 7 0 0 1-8 7 9 9 0 0 1-4-1l-5 2 2-4a7 7 0 0 1-1-4 8 7 0 0 1 8-7 8 7 0 0 1 8 7z"/>',
 "The Exam": '<circle cx="12" cy="13" r="8"/><path d="M12 9v4l3 2M9 2h6"/>',
 "Practice Exams": '<rect x="7" y="3" width="13" height="16" rx="2"/><path d="M4 7v12a2 2 0 0 0 2 2h10"/>',
 "Exam Assessment Criteria": '<rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 9l2 2 4-4M8 16h8"/>',
 "Exam Checklists": '<rect x="3" y="3" width="18" height="18" rx="3"/><path d="M8 12l3 3 5-6"/>',
 "Key Takeaways from the 2024 Assessment Report": '<path d="M4 20V10M10 20V4M16 20v-8M21 20H3"/>',
 "Key Takeaways from the 2025 Assessment Report": '<path d="M3 17l6-6 4 4 8-8"/><path d="M15 7h6v6"/>',
 "Effectively Studying For Exams": '<path d="M12 5c-2-2-6-2-8 0v13c2-2 6-2 8 0 2-2 6-2 8 0V5c-2-2-6-2-8 0z"/><path d="M12 5v13"/>',
 "Study Tools": '<path d="M13 2L4 14h6l-1 8 9-12h-6z"/>',
}
def icon_svg(title):
    body = ICONS.get(title, '<circle cx="12" cy="12" r="9"/>')
    return ('<span class="card-ico"><svg width="26" height="26" viewBox="0 0 24 24" fill="none" '
            'stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">%s</svg></span>' % body)

BLURB = {
 "How to Use This Site": "Quick orientation: search, sections, practice exams and suggested study routes.",
 "Sunset Boulevard": "Billy Wilder's film — context, themes, quote banks, scene analyses, techniques, symbols and exemplar essays.",
 "Rainbow’s End": "Jane Harrison's play — context, characters, themes, quotes and sample responses.",
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
cards = "".join('<a class="card" href="%s">%s<div class="card-num">%02d</div><div class="card-body"><h3>%s</h3><p>%s</p></div></a>'
                % (it["file"], icon_svg(it["title"]), it["num"], html.escape(it["title"]), html.escape(BLURB.get(it["title"], "")))
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

nf = """
<div class="nf-wrap">
  <div class="nf-code">404</div>
  <h1>Page not found</h1>
  <p>That page doesn&rsquo;t exist &mdash; it may have moved when the site was reorganised.</p>
  <p><a class="btn" style="background:var(--accent);color:#fff" href="index.html">Back to the guide</a></p>
  <p style="font-family:var(--sans);font-size:14px;color:var(--muted)">Or use the search box in the sidebar &mdash; it covers every page.</p>
</div>
"""
open(os.path.join(PUBLIC, "404.html"), "w", encoding="utf-8").write(shell("Page not found", "", "404.html", nf))

print("PAGES:", len(all_pages) + 1, "| PARTS:", len(nav_items), "| IMGS:", n_imgs, "| PDFS:", len(copied_pdfs),
      "| SEARCH:", len(search), "| EXEMPLARS:", len(exemplars))
for it in nav_items:
    print(" %02d %-46s %d chapters" % (it["num"], it["title"][:46], len(it["chapters"])))
