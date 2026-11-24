# -*- coding: utf-8 -*-
"""把 books/<册>/ 下的 Markdown 编译为 PDF（输出到 output/）。

用法:
    python books/build/build.py --book intro        # 构建一册（完整流程）
    python books/build/build.py --all               # 依次构建全部册
    python books/build/build.py --list              # 列出全部册
    python books/build/build.py --book intro --html # 只生成 HTML 预览
    python books/build/build.py --book intro --q 74 # 指定插图 JPEG 质量

目录约定（每册一套）:
    books/<册>/book.json          书名、副标题、作者、输出文件名、强调色
    books/<册>/structure.json     前后辅文、篇、章、附录（顺序的唯一来源）
    books/<册>/front/             扉页、版权页、前言、篇首、后记
    books/<册>/chapters/          正文（ch01.md …）
    books/<册>/appendix/          附录
    books/<册>/images/NN/         插图（正文里写作 ../images/NN/xxx.png）
    books/build/                  本脚本、gen_appendix.py、refs.json、assets/
    books/code/<册>/chNN/         绘图代码
    output/                       各册 PDF
"""
import os, re, sys, json, glob, time, hashlib, argparse
from collections import OrderedDict

import markdown
from markdown.extensions.toc import TocExtension

HERE = os.path.dirname(os.path.abspath(__file__))          # books/build
BOOKS = os.path.dirname(HERE)                              # books
ROOT = os.path.dirname(BOOKS)                              # 仓库根
OUT = os.path.join(ROOT, "output")
REFS = os.path.join(HERE, "refs.json")
KATEX_DIR = os.path.join(HERE, "assets", "katex")


def katex_uri(name):
    return "file:///" + os.path.join(KATEX_DIR, name).replace(os.sep, "/")


# KaTeX 宏表（HTML 里必须是双反斜杠，JS 运行时才是单反斜杠）
KATEX_MACROS_JS = r'{"\\RR": "\\mathbb{R}", "\\bm": "\\boldsymbol{#1}", "\\T": "^{\\top}"}'


def all_books():
    """books/ 下每个含 book.json 的目录，按 book.json 里的 order 排序。"""
    out = []
    for d in sorted(glob.glob(os.path.join(BOOKS, "*", "book.json"))):
        p = os.path.dirname(d)
        try:
            cfg = json.load(open(d, encoding="utf-8"))
        except Exception as e:
            print("! 读取失败", d, e)
            continue
        out.append((cfg.get("order", 999), os.path.basename(p), p, cfg))
    out.sort(key=lambda x: (x[0], x[1]))
    return out


def resolve_book(arg):
    if not arg:
        raise SystemExit("请用 --book 指定册，例如 --book intro；或 --all 构建全部。")
    p = arg if os.path.isdir(arg) else os.path.join(BOOKS, arg)
    p = os.path.abspath(p)
    if not os.path.isdir(p):
        raise SystemExit("找不到册目录：%s" % arg)
    return p


def load_book(bookdir):
    global BOOK, CH, FRONT, APP, IMG, OUTDIR, WORK, CFG, PDF_NAME, PDF_PATH, \
        COVER_FRONT, COVER_BACK, STRUCT, CHAPTERS, PARTS, ACCENT, ACCENT2
    BOOK = bookdir
    CH = os.path.join(BOOK, "chapters")
    FRONT = os.path.join(BOOK, "front")
    APP = os.path.join(BOOK, "appendix")
    IMG = os.path.join(BOOK, "images")
    CFG = json.load(open(os.path.join(BOOK, "book.json"), encoding="utf-8"))
    STRUCT = json.load(open(os.path.join(BOOK, "structure.json"), encoding="utf-8"))
    PARTS = STRUCT.get("parts") or [{"no": "", "title": "", "page": None,
                                     "chapters": STRUCT.get("chapters", [])}]
    CHAPTERS = [f for p in PARTS for f in p["chapters"]]
    OUTDIR = OUT
    os.makedirs(OUTDIR, exist_ok=True)
    PDF_NAME = CFG.get("pdf") or (os.path.basename(BOOK) + ".pdf")
    PDF_PATH = os.environ.get("PDF_OUT") or os.path.join(OUTDIR, PDF_NAME)
    COVER_FRONT = os.path.join(IMG, "cover_front.jpg")
    COVER_BACK = os.path.join(IMG, "cover_back.jpg")
    ACCENT = CFG.get("accent", "#8A4B12")
    ACCENT2 = CFG.get("accent2", "#A65B1E")
    base = os.path.join(ROOT, "_private", "build") if os.path.isdir(os.path.join(ROOT, "_private")) \
        else os.path.join(BOOKS, ".build")
    WORK = os.path.join(base, os.path.basename(BOOK))
    os.makedirs(WORK, exist_ok=True)


CITED = OrderedDict()      # key -> 编号（按正文首次出现）
HEADINGS = []              # (id, level, text)
_IMAP = {}


# ------------------------------------------------------------------ 参考文献
def load_refs():
    if not os.path.exists(REFS):
        return {}
    items = json.load(open(REFS, encoding="utf-8"))
    return {it["key"]: it for it in items}


PAPERMETA = load_refs()


def cite_html(keys):
    out = []
    for k in keys:
        k = k.strip()
        if not k:
            continue
        if k not in PAPERMETA:
            print("  ! 未在 refs.json 中的引用:", k)
        if k not in CITED:
            CITED[k] = len(CITED) + 1
        out.append(f'<a class="cite" href="#ref-{CITED[k]}">[{CITED[k]}]</a>')
    return "".join(out)


def repl_cite(m):
    return cite_html(re.split(r"[,;]\s*", m.group(1)))


def author_str(r):
    au = r.get("authors") or []
    if not au:
        return ""
    if len(au) > 3:
        return ", ".join(au[:3]) + ", et al."
    return ", ".join(au)


def ref_entry(k, n):
    r = PAPERMETA.get(k, {})
    title = r.get("title") or k
    au = author_str(r)
    venue = r.get("venue") or ""
    year = r.get("year") or ""
    extra = ""
    if r.get("arxiv"):
        extra = f' arXiv:{r["arxiv"]}'
    elif r.get("doi"):
        extra = f' DOI:{r["doi"]}'
    s = (f'{au}. ' if au else '') + f'<i>{esc(title)}</i>. '
    if venue:
        s += f'<span class="venue">{esc(venue)}, {year}.</span>'
    elif year:
        s += f'<span class="venue">{year}.</span>'
    s += extra
    return f'<div class="ref" id="ref-{n}"><span class="num">[{n}]</span>{s}</div>'


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


# ------------------------------------------------------------------ 图片压缩
def prepare_images(quality=82, max_w=1500):
    """把 PNG 插图转成压缩 JPEG（缓存到 WORK/img），返回 {相对 book/images 的路径: file URI}。"""
    from PIL import Image
    cache = os.path.join(WORK, "img")
    os.makedirs(cache, exist_ok=True)
    mapping = {}
    files = []
    for pat in ("*/*.png", "*/*.jpg", "*.png", "*.jpg"):
        files += glob.glob(os.path.join(IMG, pat))
    for src in sorted(set(files)):
        rel = os.path.relpath(src, IMG).replace("\\", "/")
        stem = re.sub(r"[^0-9A-Za-z]+", "-", rel)[:60]
        try:
            st = os.stat(src)
            stamp = f"{st.st_size}|{int(st.st_mtime)}"
        except OSError:
            stamp = "0|0"
        tag = hashlib.md5(f"{rel}|{quality}|{max_w}|{stamp}".encode()).hexdigest()[:8]
        dst = os.path.join(cache, f"{stem}-q{quality}-{tag}.jpg")
        if not os.path.exists(dst):
            try:
                im = Image.open(src).convert("RGB")
                if im.width > max_w:
                    im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
                im.save(dst, "JPEG", quality=quality, optimize=True, progressive=True)
            except Exception as e:
                print("  ! 图片压缩失败", rel, e)
                dst = src
        mapping[rel] = "file:///" + dst.replace("\\", "/")
    print(f"图片压缩：{len(mapping)} 张（q={quality}, max_w={max_w}）")
    return mapping


def img_uri(rel):
    return _IMAP.get(rel, "file:///" + os.path.join(IMG, rel).replace("\\", "/"))


# ------------------------------------------------------------------ Markdown
def protect_math(text):
    box = []

    def keep(m):
        box.append(m.group(0))
        return f"@@MATH{len(box)-1}@@"

    codes = []

    def keep_code(m):
        codes.append(m.group(0))
        return f"@@CODE{len(codes)-1}@@"

    text = re.sub(r"```.*?```", keep_code, text, flags=re.S)
    text = re.sub(r"\$\$.*?\$\$", keep, text, flags=re.S)
    text = re.sub(r"(?<!\\)\$[^$\n]+?\$", keep, text)
    for i, c in enumerate(codes):
        text = text.replace(f"@@CODE{i}@@", c)
    return text, box


def restore_math(html_text, box):
    def esc_math(s):
        # 公式里的 & < > 会被浏览器当成实体/标签，先转义；KaTeX 取 textContent 时仍是原字符
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    for i, m in enumerate(box):
        html_text = html_text.replace(f"@@MATH{i}@@", esc_math(m))
    return html_text


def md2html(text):
    text, box = protect_math(text)
    md = markdown.Markdown(extensions=[
        "extra", "sane_lists", "md_in_html", "attr_list", "tables", "footnotes",
        "admonition", TocExtension(baselevel=1, permalink=False),
    ], extension_configs={"toc": {"toc_depth": "1-3"}})
    out = md.convert(text)
    out = restore_math(out, box)
    out = re.sub(r"\[@([A-Za-z0-9_,;\s]+)\]", repl_cite, out)
    return out


def add_heading_ids(html_text, chap_id, part=False):
    counters = [0]

    def sub(m):
        level, attrs, inner = int(m.group(1)), m.group(2), m.group(3)
        attrs = re.sub(r'\s*id="[^"]*"', "", attrs)
        plain = re.sub(r"<[^>]+>", "", re.sub(r"⟦[^⟧]+⟧", "", inner)).strip()
        if level == 1:
            hid = chap_id
        else:
            counters[0] += 1
            hid = f"{chap_id}-s{counters[0]}"
        HEADINGS.append((hid, level, plain))
        mark = f'<span class="pgmark">⟦{hid}⟧</span>'
        return f'<h{level} id="{hid}"{attrs}>{mark}{inner}</h{level}>'

    return re.sub(r"<h([123])([^>]*)>(.*?)</h\1>", sub, html_text, flags=re.S)


def rewrite_images(raw):
    """../images/NN/x.png -> 本机构建好的压缩 JPEG 的 file URI。"""
    return re.sub(r"\.\./images/([^\"')\s]+)",
                  lambda m: img_uri(m.group(1)), raw)


def render_page(rel, kind="chapter"):
    """rel 相对 book/，例如 chapters/ch07.md。"""
    path = os.path.join(BOOK, rel)
    if not os.path.exists(path):
        print("  ! 缺少文件", rel)
        return None
    raw = open(path, encoding="utf-8").read()
    title_m = re.search(r"^#\s+(.+)$", raw, flags=re.M)
    title = title_m.group(1).strip() if title_m else os.path.basename(rel)
    raw = rewrite_images(raw)
    body = md2html(raw)
    pid = os.path.splitext(os.path.basename(rel))[0]
    body = add_heading_ids(body, pid)
    if kind == "chapter":
        body = re.sub(r'<h1 id="%s">(.*?)</h1>' % pid,
                      lambda m: f'<div class="chap-open"><h1 id="{pid}">{m.group(1)}</h1></div>',
                      body, count=1, flags=re.S)
    elif kind == "part":
        body = f'<section class="part">{body}</section>'
    elif kind == "front":
        # 扉页/版权页/后记的容器已经写在 md 里（便于 GitHub 网页端也有同样版式），
        # 这里不再包一层，否则会嵌套两个同高容器、撑出空白页。
        pass
    elif kind == "appendix":
        body = re.sub(r'<h1 id="%s">(.*?)</h1>' % pid,
                      lambda m: f'<div class="chap-open appendix-open"><h1 id="{pid}">{m.group(1)}</h1></div>',
                      body, count=1, flags=re.S)
    return dict(id=pid, title=title, html=body, kind=kind)


def roman(n):
    if n <= 0:
        return ""
    vals = [(1000, "m"), (900, "cm"), (500, "d"), (400, "cd"), (100, "c"), (90, "xc"),
            (50, "l"), (40, "xl"), (10, "x"), (9, "ix"), (5, "v"), (4, "iv"), (1, "i")]
    out = ""
    for v, sym in vals:
        while n >= v:
            out += sym
            n -= v
    return out


# CSS 单独放 books/build/style.css，便于换版式；强调色按册替换
CSS_RAW = open(os.path.join(HERE, "style.css"), encoding="utf-8").read()


def css_text():
    return CSS_RAW.replace("--accent:#14507A", "--accent:" + ACCENT)                   .replace("--accent2:#A65B1E", "--accent2:" + ACCENT2)


# ------------------------------------------------------------------ 组装
def build_html(pagemap=None):
    """pagemap 非空时用于目录页码（第二遍）。"""
    HEADINGS.clear()
    CITED.clear()
    front = []
    for rel in STRUCT.get("front", []):
        p = render_page(rel, kind="front")
        if p:
            front.append(p)

    parts = []
    for part in PARTS:
        pg = render_page(part["page"], kind="part") if part.get("page") else None
        chs = [render_page("chapters/" + fn) for fn in part["chapters"]]
        parts.append((part, pg, [c for c in chs if c]))

    apps = [render_page("appendix/" + fn, kind="appendix") for fn in STRUCT.get("appendices", [])]
    apps = [a for a in apps if a]
    back = [render_page(rel, kind="front") for rel in STRUCT.get("back", [])]
    back = [b for b in back if b]

    if pagemap:
        ids = [c["id"] for _, _, chs in parts for c in chs]
        firsts = [pagemap[i] for i in ids if i in pagemap]
        off = (min(firsts) - 1) if firsts else 0
        pagemap = {k: v - off for k, v in pagemap.items()}

    # ---- 目录 ----
    toc = ['<section class="toc"><h1>目　录</h1>']
    for p in front:
        if p["id"] in ("preface",):
            _fp = (pagemap or {}).get(p["id"], "")
            if isinstance(_fp, int) and _fp < 1:
                _fp = ""
            toc.append(f'<div class="row l1"><span class="pg">{_fp}</span>'
                       f'<span class="tt">{esc(re.sub(r"\s+", " ", p["title"]))}</span></div>')
    for part, pg, chs in parts:
        if part.get("title"):
            toc.append('<div class="tocpart">%s</div>'
                       % esc(part["title"].replace(part.get("no") or "", "").strip()))
        for c in chs:
            num = re.match(r"第\s*(\d+)\s*章", c["title"])
            short = re.sub(r"^第\s*\d+\s*章\s*", "", c["title"])
            p = (pagemap or {}).get(c["id"], "")
            if isinstance(p, int) and p < 1:
                p = ""
            toc.append(f'<div class="row l1"><span class="pg">{p}</span>'
                       f'<span class="tt">{esc(num.group(1)) if num else ""}　{esc(short)}</span></div>')
            for m in re.finditer(r'<h2 id="([^"]+)"[^>]*>.*?⟦[^⟧]+⟧(.*?)</h2>', c["html"], flags=re.S):
                hid, t = m.group(1), re.sub(r"<[^>]+>", "", m.group(2)).strip()
                t = re.sub(r"^\d+(\.\d+)*\s*", "", t)
                p2 = (pagemap or {}).get(hid, "")
                if isinstance(p2, int) and p2 < 1:
                    p2 = ""
                toc.append(f'<div class="row l2"><span class="pg">{p2}</span>'
                           f'<span class="tt">{esc(t)}</span></div>')
    if apps:
        toc.append('<div class="tocpart">附　录</div>')
        for c in apps:
            p = (pagemap or {}).get(c["id"], "")
            if isinstance(p, int) and p < 1:
                p = ""
            toc.append(f'<div class="row l1"><span class="pg">{p}</span>'
                       f'<span class="tt">{esc(c["title"])}</span></div>')
    for b in back:
        pgno = (pagemap or {}).get(b["id"], "")
        if isinstance(pgno, int) and pgno < 1:
            pgno = ""
        toc.append(f'<div class="row l1" style="margin-top:4mm"><span class="pg">{pgno}</span>'
                   f'<span class="tt">{esc(re.sub(r"\s+", " ", b["title"]))}</span></div>')
    toc.append("</section>")

    # ---- 正文 ----
    # 扉页与版权页在目录之前，前言在目录之后（符合中文书的一般排法）
    pre = [p["html"] for p in front if p["id"] in ("titlepage", "copyright")]
    post = [p["html"] for p in front if p["id"] not in ("titlepage", "copyright")]
    body = pre
    body += toc
    body += post
    for part, pg, chs in parts:
        if pg:
            body.append(pg["html"])
        body += [c["html"] for c in chs]
    body += [c["html"] for c in apps]
    body += [b["html"] for b in back]

    body_html = "\n".join(body)

    html_doc = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<title>{esc(CFG['title'])}</title>
<link rel="stylesheet" href="{katex_uri('katex.min.css')}">
<script src="{katex_uri('katex.min.js')}"></script>
<script src="{katex_uri('auto-render.min.js')}"></script>
<script>
window.addEventListener('load', function () {{
  try {{
    renderMathInElement(document.body, {{
      delimiters: [
        {{ left: '$$', right: '$$', display: true }},
        {{ left: '$',  right: '$',  display: false }}
      ],
      ignoredTags: ['script','noscript','style','textarea','pre','code','option'],
      throwOnError: false,
      errorColor: '#cc0000',
      strict: 'ignore',
      macros: {KATEX_MACROS_JS}
    }});
  }} catch (e) {{
    console.error('katex render failed', e);
  }}
  var errs = Array.prototype.map.call(document.querySelectorAll('.katex-error'),
                                     function (el) {{ return el.getAttribute('title') || el.textContent; }});
  window.__katexerrs = errs;
  document.fonts.ready.then(function () {{ window.__katexd = true; }});
}});
</script>
<style>{css_text()}</style>
</head><body>
{body_html}
</body></html>"""
    out = os.path.join(WORK, "_build.html")
    open(out, "w", encoding="utf-8").write(html_doc)
    print("HTML ->", out, len(html_doc) // 1024, "KB")
    return out, parts, apps


# ------------------------------------------------------------------ PDF
def render_pdf(html_path, pdf_path):
    from playwright.sync_api import sync_playwright
    url = "file:///" + html_path.replace("\\", "/")
    args = ["--allow-file-access-from-files", "--font-render-hinting=none"]
    with sync_playwright() as p:
        b = None
        for kw in ({"channel": "chrome"}, {"channel": "msedge"}, {}):
            try:
                b = p.chromium.launch(headless=True, args=args, **kw)
                break
            except Exception:
                continue
        if b is None:
            raise RuntimeError("找不到可用浏览器：请安装 Chrome 或 Edge。")
        pg = b.new_page()
        pg.goto(url, wait_until="load", timeout=240000)
        pg.wait_for_function("window.__katexd === true", timeout=240000)
        errs = pg.evaluate("window.__katexerrs || []")
        if errs:
            print("  ! KaTeX 渲染失败 %d 处：" % len(errs))
            for e in errs[:10]:
                print("    ", str(e)[:120])
        pg.wait_for_function(
            "Promise.all(Array.from(document.images).map(i => i.complete ? 1 : new Promise(r => {i.onload=r;i.onerror=r;}))).then(()=>true)",
            timeout=180000)
        pg.evaluate("document.fonts.ready.then(()=>true)")
        time.sleep(1.0)
        pg.pdf(path=pdf_path, format="A4", print_background=True,
               prefer_css_page_size=True, display_header_footer=False)
        b.close()
    print("PDF ->", pdf_path)


def read_pagemap(pdf_path):
    import pymupdf
    doc = pymupdf.open(pdf_path)
    pm = {}
    pat = re.compile(r"⟦([A-Za-z0-9_\-]+)⟧")
    for i, page in enumerate(doc):
        for m in pat.finditer(page.get_text()):
            pm.setdefault(m.group(1), i + 1)
    doc.close()
    return pm


def decorate(pdf_path, pagemap, parts, apps, headings):
    import pymupdf
    doc = pymupdf.open(pdf_path)
    anchors = []
    for part, pg, chs in parts:
        if pg and pg["id"] in pagemap and part.get("title"):
            no = part.get("no") or ""
            anchors.append((pagemap[pg["id"]], pg["id"],
                            (no + "　" + part["title"].replace(no, "").strip()).strip()))
        for c in chs:
            if c["id"] in pagemap:
                anchors.append((pagemap[c["id"]], c["id"], c["title"]))
    for c in apps:
        if c["id"] in pagemap:
            anchors.append((pagemap[c["id"]], c["id"], c["title"]))
    anchors.sort()
    if not anchors:
        doc.close()
        return
    start = anchors[0][0]
    offset = start - 1

    for i, page in enumerate(doc):
        if i == 0 or i + 1 < start or i == len(doc) - 1:
            continue
        cur = None
        for pno, pid, title in anchors:
            if pno <= i + 1:
                cur = title
            else:
                break
        if cur:
            m = re.match(r"第\s*(\d+)\s*章", cur)
            t = (f"第 {m.group(1)} 章　{re.sub(r'^第\s*\d+\s*章\s*', '', cur)}") if m else cur
            page.insert_text((19 * 72 / 25.4, 12.5 * 72 / 25.4), t,
                             fontname="china-s", fontsize=7.6, color=(0.55, 0.55, 0.58))
        n = i + 1 - offset
        s = f"— {n} —"
        w = pymupdf.get_text_length(s, fontname="china-s", fontsize=8.5)
        page.insert_text(((210 * 72 / 25.4 - w) / 2, 288 * 72 / 25.4), s,
                         fontname="china-s", fontsize=8.5, color=(0.45, 0.45, 0.5))

    toc = [[1, "封面", 1], [1, "扉页", 2]]
    for pno, pid, title in anchors:
        toc.append([1, re.sub(r"\s+", " ", title), pno])
    for hid, level, text in headings:
        if level == 2 and hid in pagemap:
            toc.append([2, text, pagemap[hid]])
    toc.sort(key=lambda x: (x[2], x[0]))
    doc.set_toc(toc)
    doc.set_metadata({"title": CFG.get("title", ""), "author": CFG.get("author", ""),
                      "subject": CFG.get("subtitle", ""), "creator": "Markdown + Chromium"})
    tmp = pdf_path + ".tmp"
    doc.save(tmp, garbage=4, deflate=True, clean=True)
    doc.close()
    atomic_replace(tmp, pdf_path)
    chk = pymupdf.open(pdf_path); npages = chk.page_count; chk.close()
    print("decorated ->", pdf_path, "pages:", npages)


def add_covers(body_pdf, out_pdf):
    import pymupdf
    body = pymupdf.open(body_pdf)
    rect = body[0].rect
    doc = pymupdf.open()
    for img in (COVER_FRONT, None, COVER_BACK):
        if img is None:
            doc.insert_pdf(body)
            continue
        page = doc.new_page(width=rect.width, height=rect.height)
        if os.path.exists(img):
            page.insert_image(page.rect, filename=img)
        else:
            print("  ! 缺少封面图", img)
    doc.set_metadata({"title": CFG.get("title", ""), "author": CFG.get("author", ""),
                      "subject": CFG.get("subtitle", "")})
    tmp = out_pdf + ".new"
    doc.save(tmp, garbage=3, deflate=True)
    doc.close(); body.close()
    try:
        atomic_replace(tmp, out_pdf)
    except PermissionError:
        try:
            os.remove(tmp)
        except OSError:
            pass
        raise
    print("covers merged ->", out_pdf)


def finalize(pdf_path):
    """字体子集化 + 清理，尽量压小体积。"""
    import pymupdf
    doc = pymupdf.open(pdf_path)
    try:
        doc.subset_fonts(verbose=False)
    except Exception as e:
        print("  ! 字体子集化跳过:", e)
    tmp = pdf_path + ".tmp"
    doc.save(tmp, garbage=3, deflate=True)
    doc.close()
    atomic_replace(tmp, pdf_path)
    chk = pymupdf.open(pdf_path); npages = chk.page_count; chk.close()
    print("font subset done:", npages, "pages,", round(os.path.getsize(pdf_path) / 1e6, 2), "MB")


def build_once(quality, max_w=1500):
    global _IMAP, HEADINGS
    _IMAP = prepare_images(quality, max_w)
    body_pdf = os.path.join(WORK, "_body.pdf")
    tmp_pdf = os.path.join(WORK, "_pass.pdf")
    pm = None
    for it in range(4):
        html_path, parts, apps = build_html(pm)
        render_pdf(html_path, tmp_pdf)
        pm_new = read_pagemap(tmp_pdf)
        same = (pm is not None and pm_new == pm)
        print("  第 %d 轮页码：%d 条%s" % (it + 1, len(pm_new), "（已稳定）" if same else ""))
        pm = pm_new
        if same:
            break
    html_path, parts, apps = build_html(pm)
    heads = list(HEADINGS)
    render_pdf(html_path, body_pdf)
    pm2 = read_pagemap(body_pdf)
    if pm2 != pm:
        print("  ! 页码仍未收敛（差 %d 条），以最终渲染为准"
              % len(set(pm2.items()) ^ set(pm.items())))

    def emit(path):
        add_covers(body_pdf, path)
        decorate(path, {k: v + 1 for k, v in pm2.items()}, parts, apps, heads)
        finalize(path)

    target = PDF_PATH
    try:
        emit(target)
    except PermissionError:
        alt = os.path.splitext(target)[0] + "-new.pdf"
        for stray in (target + ".new", target + ".tmp"):
            try:
                if os.path.exists(stray):
                    os.remove(stray)
            except OSError:
                pass
        print("  ! 目标 PDF 被占用，改写为:", alt)
        emit(alt)
        target = alt
    for f in (tmp_pdf, body_pdf):
        try:
            os.remove(f)
        except OSError:
            pass
    return target


def atomic_replace(src, dst, tries=12, delay=0.5):
    last = None
    for _ in range(tries):
        try:
            os.replace(src, dst)
            return True
        except PermissionError as e:
            last = e
            try:
                if os.path.exists(dst):
                    os.chmod(dst, 0o666)
                    os.remove(dst)
                    os.replace(src, dst)
                    return True
            except Exception:
                pass
            time.sleep(delay)
    raise last


def build_one(bookdir, quality=82, html_only=False):
    load_book(bookdir)
    print("=" * 60)
    print("册:", os.path.basename(bookdir), "|", CFG.get("title", ""),
          "|", CFG.get("subtitle", ""))
    if html_only:
        prepare_images(quality, 1500)
        build_html(None)
        return None
    target = build_once(quality)
    size_mb = os.path.getsize(target) / 1e6
    print("成书:", target, round(size_mb, 2), "MB")
    if size_mb > 20:
        for q in (74, 66, 58):
            print(f"超过 20 MB，降质量重建：q={q}")
            target = build_once(q)
            size_mb = os.path.getsize(target) / 1e6
            print("成书:", round(size_mb, 2), "MB")
            if size_mb <= 20:
                break
    return target


def main():
    ap = argparse.ArgumentParser(description="构建《物理模拟技术》系列中的一册或全部")
    ap.add_argument("--book", help="册目录，如 books/intro 或 intro")
    ap.add_argument("--all", action="store_true", help="依次构建全部册")
    ap.add_argument("--list", action="store_true", help="列出全部册")
    ap.add_argument("--html", action="store_true", help="只生成 HTML 预览")
    ap.add_argument("--q", type=int, default=82, help="插图 JPEG 质量（默认 82）")
    a = ap.parse_args()

    if a.list:
        for order, name, path, cfg in all_books():
            print("%-14s %-4s %s" % (name, cfg.get("order", ""), cfg.get("title", "")))
        return
    if a.all:
        failed = []
        for order, name, path, cfg in all_books():
            try:
                build_one(path, a.q, a.html)
            except Exception as e:
                print("! 构建失败", name, type(e).__name__, e)
                failed.append(name)
        if failed:
            raise SystemExit("失败：" + ", ".join(failed))
        return
    build_one(resolve_book(a.book), a.q, a.html)


if __name__ == "__main__":
    main()
