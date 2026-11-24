# -*- coding: utf-8 -*-
"""全书统一绘图风格与常用图元。所有插图脚本都 import 本文件。

约定：
    books/code/<册>/chNN/fig_xxx.py   绘图脚本
    books/<册>/images/NN/figNN-0X.png 输出（由 save() 自动落到对应册与章）

用法（推荐）：
    from figstyle import *
    fig, ax = canvas(6.6, 3.6)
    box(ax, .1, .4, .25, .2, "编码器")
    save(fig, "03", "fig03-01")          # 第 3 章第 1 图

也支持两参形式 save(fig, "fig03-01")：章节号从脚本所在路径推断。
"""
import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import (FancyBboxPatch, FancyArrowPatch, Circle, Ellipse,
                                Polygon, Rectangle, Arc, Wedge, PathPatch)
from matplotlib.path import Path
from matplotlib.lines import Line2D

# ---------- 配色 ----------
INK    = "#1F2937"
MUTED  = "#6B7280"
FAINT  = "#9CA3AF"
ACCENT = "#B45309"
BLUE   = "#1D4ED8"
GREEN  = "#047857"
PURPLE = "#6D28D9"
GOLD   = "#B45309"
PINK   = "#BE185D"
TEAL   = "#0F766E"
NAVY   = "#1E3A5F"
LIGHT  = "#F3F4F6"
PAPER  = "#FBF7F0"
GRID   = "#E5E7EB"
SLATE  = "#64748B"

PALETTE = [ACCENT, BLUE, GREEN, PURPLE, GOLD, PINK, TEAL]
SOFT = ["#FDF2E9", "#EFF4FF", "#ECFDF5", "#F5F3FF", "#FFFBEB", "#FDF2F8", "#F0FDFA"]

# ---------- 路径：从本文件推出仓库根 ----------
HERE = os.path.dirname(os.path.abspath(__file__))          # books/code
BOOKS = os.path.dirname(HERE)                              # books
ROOT = os.path.dirname(BOOKS)                              # 仓库根

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Microsoft YaHei", "Noto Sans SC", "SimHei", "DejaVu Sans"],
    "axes.unicode_minus": False,
    "font.size": 10.2,
    "axes.titlesize": 11.2,
    "axes.labelsize": 10.2,
    "axes.edgecolor": "#9CA3AF",
    "axes.linewidth": 0.8,
    "axes.labelcolor": INK,
    "text.color": INK,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "axes.grid": False,
    "grid.color": GRID,
    "grid.linewidth": 0.7,
    "legend.frameon": False,
    "legend.fontsize": 9,
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.14,
    "svg.fonttype": "none",
})


def _caller_book_chapter():
    """从调用脚本路径 books/code/<book>/chNN/ 推出册名与章号。"""
    f = sys._getframe(2).f_globals.get("__file__", "")
    f = f.replace("\\", "/")
    m = None
    for mm in __import__("re").finditer(r"/books/code/([^/]+)/ch(\d+)", f):
        m = mm
    if m:
        return m.group(1), m.group(2)
    return None, None


def save(fig, a, b=None, dpi=230, facecolor="white"):
    """save(fig, "03", "fig03-01") 或 save(fig, "fig03-01")。"""
    if b is None:
        chapter, name = None, a
        book, ch = _caller_book_chapter()
        chapter = ch
    else:
        chapter, name = a, b
        book, _ = _caller_book_chapter()
    if book is None:
        book = os.environ.get("WM_BOOK", "intro")
    chap = str(chapter).replace("ch", "").zfill(2) if chapter else "00"
    d = os.path.join(BOOKS, book, "images", chap)
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, name + ".png")
    fig.savefig(p, dpi=dpi, facecolor=facecolor)
    plt.close(fig)
    print("saved", os.path.relpath(p, ROOT))
    return p


# ---------- 画布 ----------
def canvas(w=6.6, h=3.5, xlim=(0, 1), ylim=(0, 1)):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.axis("off")
    return fig, ax


def new(w=6.6, h=3.5, ncols=1, nrows=1, **kw):
    return plt.subplots(nrows, ncols, figsize=(w, h), **kw)


def clean(ax, grid=False, spines=("left", "bottom")):
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(s in spines)
    if grid:
        ax.grid(True, zorder=0)
        ax.set_axisbelow(True)
    return ax


# ---------- 图元 ----------
def box(ax, x, y, w, h, text, fc="white", ec=INK, tc=INK, fs=9.2, lw=1.0,
        rounded=0.018, weight="normal", ha="center", va="center", alpha=1.0, z=3,
        ls="-"):
    p = FancyBboxPatch((x, y), w, h,
                       boxstyle=f"round,pad=0.008,rounding_size={rounded}",
                       linewidth=lw, edgecolor=ec, facecolor=fc, alpha=alpha,
                       zorder=z, linestyle=ls)
    ax.add_patch(p)
    if text:
        tx = x + w / 2 if ha == "center" else x + 0.014
        ax.text(tx, y + h / 2, text, ha=ha, va=va, fontsize=fs, color=tc,
                weight=weight, zorder=z + 1, linespacing=1.55)
    return p


def arrow(ax, p0, p1, color=MUTED, lw=1.2, style="-|>", ls="-", rad=0.0, z=2, ms=8,
          shrinkA=3, shrinkB=3, alpha=1.0):
    a = FancyArrowPatch(p0, p1, arrowstyle=style, mutation_scale=ms, color=color,
                        lw=lw, linestyle=ls, alpha=alpha,
                        connectionstyle=f"arc3,rad={rad}", zorder=z,
                        shrinkA=shrinkA, shrinkB=shrinkB)
    ax.add_patch(a)
    return a


def curve_arrow(ax, pts, color=MUTED, lw=1.2, z=2, ms=8, ls="-"):
    """折线/曲线箭头：pts 为若干控制点，最后一段画箭头。"""
    pts = [np.asarray(p, float) for p in pts]
    for i in range(len(pts) - 2):
        ax.plot([pts[i][0], pts[i + 1][0]], [pts[i][1], pts[i + 1][1]],
                color=color, lw=lw, ls=ls, zorder=z, solid_capstyle="round")
    arrow(ax, pts[-2], pts[-1], color=color, lw=lw, z=z, ms=ms, ls=ls)


def label(ax, x, y, text, fs=9, color=INK, ha="center", va="center",
          weight="normal", z=10, rot=0, **kw):
    ax.text(x, y, text, fontsize=fs, color=color, ha=ha, va=va, weight=weight,
            zorder=z, linespacing=1.55, rotation=rot, **kw)


def flow(ax, labels, y=0.5, w=None, h=0.2, gap=None, colors=None, fs=9,
         x0=0.04, x1=0.96, fc="white", lw=1.1):
    """横向流程：若干圆角框 + 箭头。"""
    n = len(labels)
    gap = gap if gap is not None else 0.03
    if w is None:
        w = (x1 - x0 - gap * (n - 1)) / n
    xs = []
    for i, lab in enumerate(labels):
        x = x0 + i * (w + gap)
        c = colors[i] if colors else INK
        box(ax, x, y - h / 2, w, h, lab, fc=fc, ec=c, fs=fs, lw=lw)
        xs.append((x, x + w))
        if i:
            arrow(ax, (xs[i - 1][1] + 0.002, y), (x - 0.002, y), color=FAINT, lw=1.0)
    return xs


def vflow(ax, labels, x=0.5, w=0.34, h=0.13, gap=0.075, y0=0.84, colors=None,
          fs=9, fc="white"):
    """纵向流程，从下往上或从上往下排。返回每个框的中心。"""
    cents = []
    for i, lab in enumerate(labels):
        y = y0 - i * (h + gap)
        c = colors[i] if colors else INK
        box(ax, x - w / 2, y - h / 2, w, h, lab, fc=fc, ec=c, fs=fs)
        cents.append((x, y))
        if i:
            arrow(ax, (x, cents[i - 1][1] - h / 2 - 0.006), (x, y + h / 2 + 0.006),
                  color=FAINT, lw=1.0)
    return cents


def timeline(ax, items, y=0.5, color=INK, accent=ACCENT, fs=8.4, span=None,
             alt=0.20):
    """时间轴。items: [(year, label, sub)]，交替上下标注。"""
    years = [it[0] for it in items]
    lo, hi = (span or (min(years), max(years)))
    ax.plot([0.03, 0.97], [y, y], color=color, lw=1.2, zorder=2)
    for i, it in enumerate(items):
        yr, lab = it[0], it[1]
        sub = it[2] if len(it) > 2 else ""
        x = 0.06 + 0.88 * (yr - lo) / max(1e-9, (hi - lo))
        above = (i % 2 == 0)
        yy = y + alt if above else y - alt
        ax.plot([x, x], [y, yy], color=FAINT, lw=0.7, zorder=1)
        ax.scatter([x], [y], s=20, color=accent, zorder=3, edgecolor="white", linewidth=0.7)
        va = "bottom" if above else "top"
        label(ax, x, yy + (0.035 if above else -0.035), f"{yr}", fs=fs + 0.4,
              color=accent, weight="bold", va=va)
        label(ax, x, yy + (0.095 if above else -0.095), lab, fs=fs, color=INK, va=va)
        if sub:
            label(ax, x, yy + (0.155 if above else -0.155), sub, fs=fs - 1.3,
                  color=MUTED, va=va)


def bracket(ax, x0, x1, y, text, color=MUTED, fs=8.4, dy=0.022, lw=0.9):
    ax.annotate("", xy=(x0, y), xytext=(x1, y),
                arrowprops=dict(arrowstyle="<->", color=color, lw=lw))
    label(ax, (x0 + x1) / 2, y + dy, text, fs=fs, color=color)


def brace_v(ax, x, y0, y1, text, color=MUTED, fs=8.4, dx=-0.02):
    """左侧竖括号 + 说明文字。"""
    ax.plot([x, x - 0.012, x - 0.012, x], [y0, y0, y1, y1], color=color, lw=0.9, zorder=4)
    label(ax, x + dx, (y0 + y1) / 2, text, fs=fs, color=color, ha="right", rot=90)


def grid(ax, x0, y0, w, h, nx, ny, color=GRID, lw=0.6, alpha=1.0):
    for i in range(nx + 1):
        x = x0 + w * i / nx
        ax.plot([x, x], [y0, y0 + h], color=color, lw=lw, alpha=alpha, zorder=1)
    for j in range(ny + 1):
        y = y0 + h * j / ny
        ax.plot([x0, x0 + w], [y, y], color=color, lw=lw, alpha=alpha, zorder=1)


def patch_cells(ax, x0, y0, w, h, nx, ny, cells, color=ACCENT, alpha=0.28, z=2):
    """按 (i, j) 列表给网格上的格子填色。cells: [(i,j), ...]，i 列 j 行（从下往上）。"""
    cw, ch = w / nx, h / ny
    for i, j in cells:
        ax.add_patch(Rectangle((x0 + i * cw, y0 + j * ch), cw, ch,
                               facecolor=color, edgecolor="none", alpha=alpha, zorder=z))


def heat(ax, x0, y0, w, h, M, cmap="YlOrBr", vmin=None, vmax=None, z=2, alpha=1.0):
    ax.imshow(np.asarray(M), extent=[x0, x0 + w, y0, y0 + h], origin="lower",
              cmap=cmap, vmin=vmin, vmax=vmax, aspect="auto", zorder=z, alpha=alpha)


def dim_arrow(ax, p0, p1, text, color=MUTED, fs=8.4, off=0.03):
    arrow(ax, p0, p1, color=color, lw=0.9, style="<|-|>", ms=7)
    mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
    label(ax, mx, my + off, text, fs=fs, color=color)


def legend_row(ax, items, x=0.04, y=0.06, dy=0.055, fs=8.4, sw=0.022, sh=0.018):
    """左下角小图例。items: [(color, text)]"""
    for i, (c, t) in enumerate(items):
        yy = y + (len(items) - 1 - i) * dy
        ax.add_patch(Rectangle((x, yy), sw, sh, facecolor=c, edgecolor="none", alpha=0.85, zorder=5))
        label(ax, x + sw + 0.012, yy + sh / 2, t, fs=fs, color=INK, ha="left")


def band(ax, x0, y0, w, h, text, fc="#F9FAFB", ec="#E5E7EB", tc=MUTED, fs=8.4, z=1):
    ax.add_patch(Rectangle((x0, y0), w, h, facecolor=fc, edgecolor=ec, lw=0.8, zorder=z))
    if text:
        label(ax, x0 + 0.012, y0 + h - 0.022, text, fs=fs, color=tc, ha="left", va="top")


def frame_note(ax, text, x=0.985, y=0.02, fs=7.8, color=FAINT):
    """右下角出处/说明。"""
    label(ax, x, y, text, fs=fs, color=color, ha="right", va="bottom")


# ---------- 常用示意 ----------
def neural_net(ax, layers, x0=0.1, x1=0.9, y=0.5, r=0.012, color=INK, accent=ACCENT,
               spread=0.32):
    """画一个前馈网络：layers 为每层节点数。"""
    xs = np.linspace(x0, x1, len(layers))
    pos = []
    for x, n in zip(xs, layers):
        ys = np.linspace(y - spread, y + spread, n) if n > 1 else [y]
        pos.append([(x, yy) for yy in ys])
    for a, b in zip(pos[:-1], pos[1:]):
        for p in a:
            for q in b:
                ax.plot([p[0], q[0]], [p[1], q[1]], color="#D1D5DB", lw=0.5, zorder=1)
    for i, ps in enumerate(pos):
        for p in ps:
            ax.add_patch(Circle(p, r, facecolor="white", edgecolor=color, lw=0.9, zorder=3))
    return pos, xs


def axes3d_sketch(ax, x=0.5, y=0.35, s=1.0, labels=("x", "y", "z")):
    ax.annotate("", xy=(x + 0.16 * s, y), xytext=(x, y),
                arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.0))
    ax.annotate("", xy=(x, y + 0.2 * s), xytext=(x, y),
                arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.0))
    ax.annotate("", xy=(x - 0.11 * s, y + 0.11 * s), xytext=(x, y),
                arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.0))
    label(ax, x + 0.175 * s, y, labels[0], fs=8, color=MUTED)
    label(ax, x, y + 0.215 * s, labels[1], fs=8, color=MUTED)
    label(ax, x - 0.125 * s, y + 0.125 * s, labels[2], fs=8, color=MUTED)


def point_cloud(ax, x0, y0, w, h, n=140, color=SLATE, seed=3, size=3.2, alpha=0.8):
    rng = np.random.default_rng(seed)
    xs = x0 + w * rng.random(n)
    ys = y0 + h * rng.random(n)
    ax.scatter(xs, ys, s=size, color=color, alpha=alpha, zorder=3, linewidths=0)


def latent_blob(ax, x=0.5, y=0.5, rx=0.20, ry=0.14, n=90, color=PURPLE, seed=1):
    rng = np.random.default_rng(seed)
    pts = rng.normal(0, 1, (n, 2))
    pts = pts / (np.abs(pts).max(0) + 1e-6)
    ax.scatter(x + rx * pts[:, 0], y + ry * pts[:, 1], s=6, color=color, alpha=0.55,
               zorder=3, linewidths=0)
    ax.add_patch(Ellipse((x, y), 2 * rx, 2 * ry, fill=False, edgecolor=color, lw=1.0,
                         linestyle="--", alpha=0.7, zorder=2))
