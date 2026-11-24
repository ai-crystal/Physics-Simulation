# -*- coding: utf-8 -*-
"""成书自检：PDF 里每个标题都能被正确读出来，且没有 Type3 字体。

用法: python books/build/checks/verify_pdf_text.py output/jepa-basics.pdf --book basics
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BOOKS = ROOT / "books"

args = [a for a in sys.argv[1:] if not a.startswith("--")]
pdf = Path(args[0]) if args else None
book = sys.argv[sys.argv.index("--book") + 1] if "--book" in sys.argv else None
if pdf is None:
    book = book or "basics"
    pdf = ROOT / "output" / f"jepa-{book}.pdf"
if book is None:
    m = re.match(r"jepa-(\w+)\.pdf", pdf.name)
    book = m.group(1) if m else "basics"
BOOK = BOOKS / book

KEEP = re.compile(r"[^\u4e00-\u9fffA-Za-z0-9]+")


def norm(s: str) -> str:
    return KEEP.sub("", s)


def content_files():
    files = []
    for folder in ("front", "chapters", "appendix"):
        files.extend(sorted((BOOK / folder).glob("*.md")))
    return files


def headings():
    out = []
    for path in content_files():
        for line in path.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^(#{1,4})\s+(.*\S)\s*$", line)
            if m:
                text = re.sub(r"\s*\{:[^}]*\}\s*$", "", m.group(2)).strip()
                out.append((len(m.group(1)), text, path.name))
    return out


def main():
    import pymupdf

    if not pdf.exists():
        raise SystemExit(f"找不到 {pdf}")
    doc = pymupdf.open(pdf)
    blob = "".join(norm(p.get_text()) for p in doc)

    type3 = 0
    for page in doc:
        for f in page.get_fonts():
            if f[2] == "Type3":
                type3 += 1

    missing = []
    for level, text, src in headings():
        if level > 3:
            continue
        key = norm(text)
        if key and key not in blob:
            missing.append((src, level, text))

    print(f"PDF: {pdf.name}  册: {book}  页数 {doc.page_count}  "
          f"体积 {pdf.stat().st_size / 1024 / 1024:.2f} MiB")
    print(f"Type3 字体引用数: {type3}")
    if missing:
        print(f"[FAIL] {len(missing)} 个标题无法在文本层读出：")
        for src, level, text in missing[:40]:
            print(f"  {src}  h{level}  {text}")
    else:
        print("[PASS] 全部标题均可从文本层读出")
    doc.close()
    return 1 if (missing or type3) else 0


if __name__ == "__main__":
    sys.exit(main())
