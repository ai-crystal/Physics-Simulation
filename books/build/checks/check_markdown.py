# -*- coding: utf-8 -*-
"""书稿自检：字数、标题、图号与文件、公式与代码块配对、禁用词、段落与短句。

用法: python books/build/checks/check_markdown.py --book basics
"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))   # 仓库根
BOOKS = os.path.join(ROOT, "books")

book = sys.argv[sys.argv.index("--book") + 1] if "--book" in sys.argv else None
if not book:
    raise SystemExit("用法: python books/build/checks/check_markdown.py --book <册名>")
BOOK = os.path.join(BOOKS, book)

BANNED = ["首先", "其次", "综上所述", "值得注意的是", "不难发现", "众所周知",
          "让我们", "深入探讨", "赋能", "本章将", "本节将", "显而易见", "总而言之"]


def body_paragraphs(text):
    """去掉标题、公式块、代码块、图表 HTML 之后的正文段落。"""
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"\$\$.*?\$\$", "", text, flags=re.S)
    text = re.sub(r"<figure.*?</figure>", "", text, flags=re.S)
    paras = []
    for block in text.split("\n\n"):
        b = block.strip()
        if (not b or b.startswith("#") or b.startswith("|") or b.startswith("- ")
                or b.startswith("* ") or b.startswith("**表") or b.startswith(">")):
            continue
        if re.match(r"^\d+\.\s", b):
            continue
        paras.append(b)
    return paras


def style_stats(text):
    paras = body_paragraphs(text)
    short_paras = 0
    short_runs = 0
    for p in paras:
        sents = [s for s in re.split(r"[。！？]", p) if s.strip()]
        if len(sents) <= 2 and len(p) < 80:
            short_paras += 1
        run = 0
        for s in sents:
            if len(s) < 15:
                run += 1
                short_runs = max(short_runs, run)
            else:
                run = 0
    return len(paras), short_paras, short_runs


def check(path):
    text = open(path, encoding="utf-8").read()
    name = os.path.basename(path)
    lines = text.splitlines()
    cn = len(re.findall(r"[\u4e00-\u9fff]", text))
    h1 = [l for l in lines if re.match(r"^#\s", l)]
    h2 = [l for l in lines if re.match(r"^##\s", l)]
    h3 = [l for l in lines if re.match(r"^###\s", l)]
    figs = re.findall(r'<img src="\.\./images/(\d+)/([^"]+)"', text)
    fig_nums = re.findall(r"<b>图\s*(\d+)-(\d+)</b>", text)
    ins = re.findall(r"图\s*(\d+)-(\d+)", text)
    tables = len(re.findall(r"^\*\*表\s*\d+-\d+\*\*", text, flags=re.M))
    fences = text.count("```")
    dollars = text.count("$") - 2 * text.count("$$")
    banned = [w for w in BANNED if w in text]
    dashes = text.count("——")
    colons = text.count("：")
    n_para, short_para, short_run = style_stats(text)
    problems = []

    if fences % 2:
        problems.append(f"代码围栏 {fences} 个（奇数）")
    if any(len(re.findall(r"^\s*```", l)) > 1 for l in lines):
        problems.append("怀疑嵌套代码块")
    if dollars % 2:
        problems.append(f"行内公式 $ 数 {dollars} 为奇数")
    for ch, fn in figs:
        p = os.path.join(BOOK, "images", ch.zfill(2), fn)
        if not os.path.exists(p):
            problems.append(f"缺图 {p}")
    for ch, num in set(ins):
        if (ch, num) not in set(fig_nums):
            problems.append(f"正文引用图 {ch}-{num} 无对应 figcaption")
    for ch, num in set(fig_nums):
        if (ch, num) not in set(ins):
            problems.append(f"图 {ch}-{num} 未被正文引用")
    if banned:
        problems.append("禁用词: " + "/".join(banned))
    if h1 and re.search(r"[`\"'（）()\[\]{}:：/\\]", h1[0][2:]):
        problems.append("章标题含特殊字符")
    # 附录是速查手册，按“公式 + 一句解释”排，不按段落篇幅要求
    if short_run >= 3 and "/appendix/" not in path.replace("\\", "/"):
        problems.append(f"连续 {short_run} 句短于 15 字")

    flag = "OK" if not problems else "!"
    tag = "（附录，不计短段）" if "/appendix/" in path.replace("\\", "/") else ""
    print(f"{name:12s} {cn:5d}字 h2={len(h2):2d} 图={len(figs)} 段={n_para:2d} "
          f"短段={short_para:2d} 破折号={dashes} 冒号={colons} {flag}{tag}")
    for p in problems:
        print("   -", p)
    return problems


def main():
    files = []
    for folder in ("front", "chapters", "appendix"):
        files += sorted(glob.glob(os.path.join(BOOK, folder, "*.md")))
    total = 0
    bad = 0
    for f in files:
        if os.path.basename(f) in ("titlepage.md", "copyright.md"):
            continue
        text = open(f, encoding="utf-8").read()
        total += len(re.findall(r"[\u4e00-\u9fff]", text))
        bad += len(check(f))
    print(f"\n{book} 全书汉字 {total}，问题 {bad} 处")


if __name__ == "__main__":
    main()
