# -*- coding: utf-8 -*-
"""为每一册生成正封与封底（A4，约 290 DPI）。

视觉：_private/art/logos 下的星际与山川图；同一套版式，靠分册名与强调色区分。

用法: python books/build/make_covers.py            # 全部册
      python books/build/make_covers.py --book intro
输出: books/<册>/images/cover_front.jpg, cover_back.jpg
"""
import base64
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent      # books/build
BOOKS = HERE.parent                         # books
ROOT = BOOKS.parent                         # 仓库根
LOGO_DIR = ROOT / "_private" / "art" / "logos"

W, H = 794, 1123   # A4 @96dpi 的 CSS 像素
INK = "#F4F7FB"
ICE = "#A8CBE4"
GOLD = "#E7B473"


def art(name):
    """把插图转成 data URI：set_content 的页面是 about:blank，file:// 子资源会被拦。"""
    p = LOGO_DIR / name
    mime = "image/png" if p.suffix.lower() == ".png" else "image/jpeg"
    return "data:%s;base64,%s" % (mime, base64.b64encode(p.read_bytes()).decode())


BASE_CSS = """
*{margin:0;padding:0;box-sizing:border-box;}
html,body{width:%(W)dpx;height:%(H)dpx;background:#060A14;}
.page{width:%(W)dpx;height:%(H)dpx;position:relative;overflow:hidden;color:%(INK)s;
  font-family:"Noto Serif SC","Source Han Serif SC","SimSun",serif;background:#060A14;}
.bg{position:absolute;inset:0;background-repeat:no-repeat;background-size:cover;}
.scrim{position:absolute;inset:0;}
.frame{position:absolute;inset:30px;border:1px solid rgba(200,225,245,.20);}
.frame:before{content:"";position:absolute;left:-1px;top:-1px;width:26px;height:26px;
  border-left:2px solid %(GOLD)s;border-top:2px solid %(GOLD)s;opacity:.85;}
.frame:after{content:"";position:absolute;right:-1px;bottom:-1px;width:26px;height:26px;
  border-right:2px solid %(ICE)s;border-bottom:2px solid %(ICE)s;opacity:.65;}
.inner{position:absolute;left:78px;right:78px;top:96px;}
.kicker{font-family:"Noto Sans SC","Microsoft YaHei",sans-serif;font-size:10.5px;
  letter-spacing:6px;color:%(ICE)s;font-weight:400;}
.rule{width:36px;height:1.5px;background:%(GOLD)s;margin-top:20px;}
h1{font-size:74px;line-height:1.26;font-weight:600;letter-spacing:5px;color:#FCFEFF;
  margin-top:118px;
  text-shadow:0 3px 30px rgba(2,7,16,.92),0 1px 2px rgba(2,7,16,.85),0 0 46px rgba(4,12,26,.7);}
.vol{font-size:30px;line-height:1.5;letter-spacing:8px;color:%(ACC)s;margin-top:24px;
  text-shadow:0 2px 20px rgba(2,7,16,.9);}
.sub{font-size:28px;line-height:1.5;letter-spacing:6px;color:#EFF7FE;margin-top:22px;
  text-shadow:0 2px 18px rgba(2,7,16,.85);}
.sub2{font-family:"Noto Sans SC",sans-serif;font-size:14px;letter-spacing:5px;
  color:rgba(226,242,255,.86);margin-top:15px;text-shadow:0 1px 12px rgba(2,7,16,.8);}
.barwrap{margin-top:58px;}
.bar{height:3px;width:100%%;background:linear-gradient(90deg,%(ICE)s 0%%,#C6B4FF 46%%,%(GOLD)s 100%%);opacity:.9;}
.ticks{display:flex;justify-content:space-between;margin-top:10px;
  font-family:"Noto Sans SC",sans-serif;font-size:9px;letter-spacing:1.2px;
  color:rgba(232,244,255,.8);text-shadow:0 1px 10px rgba(2,7,16,.9);}
.tag{font-size:17px;line-height:1.95;letter-spacing:2.4px;color:#F3F9FF;margin-top:48px;
  text-shadow:0 2px 16px rgba(2,7,16,.9);padding-left:16px;border-left:2px solid %(GOLD)s;}
.tag i{font-style:normal;color:%(GOLD)s;}
.bottom{position:absolute;left:78px;right:78px;bottom:84px;}
.author{font-size:16px;letter-spacing:4px;color:#FBFDFF;}
.edition{font-family:"Noto Sans SC",sans-serif;font-size:10.2px;letter-spacing:2.2px;
  color:rgba(214,235,252,.52);margin-top:9px;}
.orbits{position:absolute;left:0;top:0;width:100%%;height:100%%;opacity:.30;}
h2{font-size:42px;line-height:1.44;letter-spacing:3px;font-weight:600;color:#FBFDFF;
  margin-top:22px;text-shadow:0 2px 22px rgba(4,10,22,.6);}
.panel{margin-top:24px;padding:28px 28px 26px;border:1px solid rgba(207,232,255,.15);
  background:linear-gradient(180deg,rgba(8,18,34,.60),rgba(5,12,24,.72));}
.lead{font-size:12.6px;line-height:2.0;letter-spacing:.4px;color:rgba(232,244,255,.90);}
.lead em{font-style:normal;color:%(GOLD)s;}
.toc{margin-top:22px;list-style:none;}
.toc li{display:flex;gap:12px;align-items:baseline;padding:8px 0;
  border-top:1px solid rgba(207,232,255,.10);}
.toc li b{font-family:"Noto Sans SC",sans-serif;font-size:11px;letter-spacing:2.4px;
  color:%(ICE)s;font-weight:500;white-space:nowrap;}
.toc li span{font-family:"Noto Sans SC",sans-serif;font-size:10.4px;line-height:1.7;
  letter-spacing:.6px;color:rgba(226,240,252,.72);}
.quote{margin-top:26px;font-size:16px;line-height:1.95;letter-spacing:2px;color:#F4F9FF;
  border-left:2px solid %(GOLD)s;padding-left:16px;}
.who{font-size:15px;letter-spacing:3.4px;color:#FBFDFF;line-height:1.8;}
.who span{font-family:"Noto Sans SC",sans-serif;font-size:10.2px;letter-spacing:2px;
  color:rgba(214,235,252,.52);}
"""

FRONT_TPL = """<!doctype html><html><head><meta charset="utf-8"><style>{css}
.bg{{background-image:url("{art}");background-position:{pos};}}
.scrim{{background:
  linear-gradient(102deg,rgba(3,8,19,.94) 0%,rgba(3,8,19,.80) 38%,rgba(3,8,19,.42) 66%,rgba(3,8,19,.16) 100%),
  linear-gradient(180deg,rgba(3,8,19,.62) 0%,rgba(3,8,19,.10) 34%,rgba(3,8,19,.28) 62%,rgba(2,6,14,.90) 100%);}}
</style></head><body><div class="page">
  <div class="bg"></div><div class="scrim"></div>
  <svg class="orbits" viewBox="0 0 794 1123" fill="none">
    <ellipse cx="640" cy="700" rx="420" ry="150" stroke="{ice}" stroke-width=".8" stroke-opacity=".5" transform="rotate(-18 640 700)"/>
    <ellipse cx="640" cy="700" rx="330" ry="112" stroke="{gold}" stroke-width=".7" stroke-opacity=".4" transform="rotate(-18 640 700)"/>
    <ellipse cx="640" cy="700" rx="520" ry="196" stroke="#C6B4FF" stroke-width=".6" stroke-opacity=".28" transform="rotate(-18 640 700)"/>
  </svg>
  <div class="frame"></div>
  <div class="inner">
    <div class="kicker">{series_en}　·　{volno}</div>
    <div class="rule"></div>
    <h1>{title}</h1>
    <div class="vol">{volume}</div>
    <div class="sub">{subtitle}</div>
    <div class="sub2">{tagline}</div>
    <div class="barwrap"><div class="bar"></div>
      <div class="ticks">{ticks}</div>
    </div>
    <div class="tag">{tag}</div>
  </div>
  <div class="bottom">
    <div class="author">{author}</div>
    <div class="edition">{edition}　·　{volume}</div>
  </div>
</div></body></html>"""

BACK_TPL = """<!doctype html><html><head><meta charset="utf-8"><style>{css}
.bg{{background-image:url("{art}");background-position:{pos};}}
.scrim{{background:
  radial-gradient(700px 520px at 80% 18%,rgba(8,20,40,.28),transparent 72%),
  linear-gradient(180deg,rgba(3,8,18,.84) 0%,rgba(3,8,18,.64) 30%,rgba(3,8,18,.80) 72%,rgba(2,6,14,.94) 100%);}}
</style></head><body><div class="page">
  <div class="bg"></div><div class="scrim"></div><div class="frame"></div>
  <div class="inner">
    <div class="kicker">ABOUT THIS VOLUME</div>
    <div class="rule"></div>
    <h2>{back_title}</h2>
    <div class="panel">
      <div class="lead">{back_lead}</div>
      <ul class="toc">{items}</ul>
    </div>
    <div class="quote">{quote}</div>
  </div>
  <div class="bottom">
    <div class="who">{author}<br><span>{edition}　·　{volume}</span></div>
  </div>
</div></body></html>"""


def load_books(only=None):
    out = []
    for p in sorted(BOOKS.glob("*/book.json")):
        cfg = json.load(open(p, encoding="utf-8"))
        if only and p.parent.name != only:
            continue
        out.append((p.parent, cfg))
    out.sort(key=lambda x: x[1].get("order", 999))
    return out


def fill(tpl, cfg):
    css = BASE_CSS % dict(W=W, H=H, INK=INK, ICE=cfg.get("ice", ICE), GOLD=GOLD,
                          ACC=cfg.get("cover_accent", cfg["accent"]))
    items = "".join("<li><b>%s</b><span>%s</span></li>" % (a, b)
                    for a, b in cfg.get("back_items", []))
    ticks = "".join("<span>%s</span>" % t for t in cfg.get("ticks", []))
    html = tpl.format(css=css, art="{ART}", pos="{POS}", ice=cfg["ice"], gold=GOLD,
                      series_en=cfg.get("series_en", "PHYSICS SIMULATION"), ticks=ticks,
                      volno=cfg.get("volume", ""), title=cfg.get("cover_title", ""),
                      volume=cfg.get("volume_name", ""), subtitle=cfg.get("subtitle", ""),
                      tagline=cfg.get("tag_line", ""), tag=cfg.get("cover_tag", ""),
                      author=cfg.get("author", ""), edition=cfg.get("edition", ""),
                      back_title=cfg.get("back_title", ""), back_lead=cfg.get("back_lead", ""),
                      items=items, quote=cfg.get("back_quote", ""))
    return html


def render(b, html, out):
    pg = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=3)
    pg.set_content(html, wait_until="load")
    pg.evaluate("document.fonts.ready")
    pg.wait_for_timeout(600)
    pg.screenshot(path=str(out), type="jpeg", quality=90)
    print("saved", out, round(out.stat().st_size / 1e6, 2), "MB")
    pg.close()


def main():
    import sys
    only = None
    if "--book" in sys.argv:
        only = sys.argv[sys.argv.index("--book") + 1].rstrip("/\\")
    with sync_playwright() as p:
        args = ["--font-render-hinting=none", "--force-color-profile=srgb"]
        b = None
        for kw in ({"channel": "chrome"}, {"channel": "msedge"}, {}):
            try:
                b = p.chromium.launch(headless=True, args=args, **kw)
                print("browser:", kw.get("channel", "bundled"))
                break
            except Exception:
                continue
        if b is None:
            raise SystemExit("没有可用的 Chromium/Chrome/Edge")
        for bd, cfg in load_books(only):
            cfg = dict(cfg)
            cfg["ice"] = cfg.get("ice", ICE)
            front = fill(FRONT_TPL, cfg)
            front = front.replace("{ART}", art(cfg["art"]))
            front = front.replace("{POS}", cfg.get("art_pos", "50% 50%"))
            back = fill(BACK_TPL, cfg)
            back = back.replace("{ART}", art(cfg.get("art_back", cfg["art"])))
            back = back.replace("{POS}", cfg.get("art_back_pos", "50% 50%"))
            render(b, front, bd / "images" / "cover_front.jpg")
            render(b, back, bd / "images" / "cover_back.jpg")
        b.close()


if __name__ == "__main__":
    main()
