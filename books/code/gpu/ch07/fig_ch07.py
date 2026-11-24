# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *
import numpy as np


# ---------------------------------------------------------------- 冲突图与着色
def conflict_graph(W, H, r):
    """格子 (i,j) 的写入集合是 (i..i+k-1)x(j..j+k-1)，k = r+1。
    两个格子冲突 <=> 写入集合有交集 <=> 两个方向上的距离都不超过 r。"""
    cells = [(i, j) for j in range(H) for i in range(W)]
    idx = {c: n for n, c in enumerate(cells)}
    adj = [set() for _ in cells]
    for n, (i, j) in enumerate(cells):
        for di in range(-r, r + 1):
            for dj in range(-r, r + 1):
                if di == 0 and dj == 0:
                    continue
                q = (i + di, j + dj)
                if q in idx:
                    adj[n].add(idx[q])
    return cells, adj


def greedy_color(cells, adj):
    """行优先顺序的贪心着色。"""
    order = sorted(range(len(cells)), key=lambda n: (cells[n][1], cells[n][0]))
    color = [-1] * len(cells)
    for n in order:
        used = {color[m] for m in adj[n] if color[m] >= 0}
        c = 0
        while c in used:
            c += 1
        color[n] = c
    return color


def verify(cells, adj, color):
    bad = 0
    for n in range(len(cells)):
        for m in adj[n]:
            if color[m] == color[n]:
                bad += 1
    return bad


# ---------------------------------------------------------------- 图 7-1
W1, H1, R1 = 8, 8, 1      # 双线性（2x2 支撑）
W2, H2, R2 = 6, 6, 2      # 三次 B 样条（3x3 支撑）

c1, a1 = conflict_graph(W1, H1, R1)
col1 = greedy_color(c1, a1)
n1 = max(col1) + 1
bad1 = verify(c1, a1, col1)

c2, a2 = conflict_graph(W2, H2, R2)
col2 = greedy_color(c2, a2)
n2 = max(col2) + 1
bad2 = verify(c2, a2, col2)

print("2x2 支撑: 色数 =", n1, " 同色冲突对数 =", bad1, " 顶点数 =", len(c1))
print("3x3 支撑: 色数 =", n2, " 同色冲突对数 =", bad2, " 顶点数 =", len(c2))
assert n1 == 4 and bad1 == 0
assert n2 == 9 and bad2 == 0

fig, axs = plt.subplots(1, 2, figsize=(6.8, 3.35),
                        gridspec_kw=dict(width_ratios=[1.16, 1.0], wspace=0.30))

FOUR = [ACCENT, BLUE, GREEN, PURPLE]

# (a) 四色
ax = axs[0]
for n, (i, j) in enumerate(c1):
    ax.add_patch(Rectangle((i, H1 - 1 - j), 1, 1, facecolor=FOUR[col1[n] % 4],
                           edgecolor="white", lw=1.1, alpha=0.88, zorder=2))
ax.set_xlim(-0.12, W1 + 0.12)
ax.set_ylim(-1.55, H1 + 0.12)
ax.set_aspect("equal")
ax.axis("off")
# 图例（网格下方）
for k in range(4):
    ax.add_patch(Rectangle((1.55 + k * 0.72, -1.32), 0.52, 0.52, facecolor=FOUR[k],
                           edgecolor="white", lw=1.0, zorder=3))
    ax.text(1.81 + k * 0.72, -1.52, str(k), ha="center", va="top", fontsize=8.4, color=MUTED)
ax.text(1.35, -1.06, "轮次", ha="right", va="center", fontsize=8.4, color=MUTED)
ax.text(-0.05, H1 + 0.04, "(a)  $2\\times2$ 支撑，4 色", ha="left", va="bottom",
        fontsize=9.0, color=INK)

# (b) 九色（数字标号，同底色）
ax = axs[1]
for n, (i, j) in enumerate(c2):
    ax.add_patch(Rectangle((i, H2 - 1 - j), 1, 1, facecolor="#F3F4F6",
                           edgecolor="#D1D5DB", lw=0.9, zorder=2))
    ax.text(i + 0.5, H2 - 1 - j + 0.5, str(col2[n]), ha="center", va="center",
            fontsize=9.2, color=INK, zorder=4)
ax.set_xlim(-0.12, W2 + 0.12)
ax.set_ylim(-0.55, H2 + 0.12)
ax.set_aspect("equal")
ax.axis("off")
ax.text(-0.05, H2 + 0.04, "(b)  $3\\times3$ 支撑，9 色", ha="left", va="bottom",
        fontsize=9.0, color=INK)
ax.text(W2 / 2, -0.30, "同色格子相距 3 格", ha="center", va="center",
        fontsize=8.2, color=MUTED)

save(fig, "07", "fig07-01")


# ---------------------------------------------------------------- 图 7-2（示意）
fig, ax = canvas(6.7, 3.55)

X0, X1 = 0.150, 0.940

W_WORK, W_HOT, W_TAIL = 0.200, 0.048, 0.200
W_WAIT = 0.048
H_BAR = 0.052


def bar(x, y, w, fc, ec, lw=0.8, z=2, alpha=1.0, hatch=None):
    ax.add_patch(Rectangle((x, y), w, H_BAR, facecolor=fc, edgecolor=ec, lw=lw,
                           zorder=z, alpha=alpha, hatch=hatch))


# ---- 上组
ax.text(0.012, 0.958, "不加保护", fontsize=9.0, color=INK, ha="left", va="center", weight="bold")
ax.text(0.012, 0.912, "同一地址的请求被硬件排队重放，等待沿时间轴累积",
        fontsize=8.2, color=MUTED, ha="left", va="center")

top_ys = [0.820, 0.740, 0.660, 0.580]
for k, y in enumerate(top_ys):
    x = X0
    bar(x, y, W_WORK, "#E8EDF5", "#C7D2E3")
    x += W_WORK
    if k:
        bar(x, y, W_WAIT * k, "#F3F4F6", "#D1D5DB", lw=0.7, hatch="////")
        ax.text(x + W_WAIT * k / 2, y + H_BAR / 2, "等", ha="center", va="center",
                fontsize=8.0, color=MUTED, zorder=5)
        x += W_WAIT * k
    bar(x, y, W_HOT, ACCENT, "white", lw=0.9, z=3, alpha=0.92)
    x += W_HOT
    bar(x, y, W_TAIL, "#E8EDF5", "#C7D2E3")
    ax.text(0.086, y + H_BAR / 2, "T%d" % (k + 1), ha="center", va="center",
            fontsize=8.2, color=MUTED)

top_end = X0 + W_WORK + W_WAIT * 3 + W_HOT + W_TAIL

# ---- 图例
ax.text(0.012, 0.528, "橙色：排队重放　　斜纹：线程空等　　绿色：块内合并",
        fontsize=8.0, color=FAINT, ha="left", va="center")

# ---- 下组
ax.text(0.012, 0.462, "块内合并后分轮：每轮写集合互不相交", fontsize=9.0, color=INK,
        ha="left", va="center", weight="bold")

bot_ys = [0.360, 0.280, 0.200, 0.120]
for k, y in enumerate(bot_ys):
    x = X0
    bar(x, y, W_WORK, "#E8EDF5", "#C7D2E3")
    x += W_WORK
    bar(x, y, W_HOT * 0.45, GREEN, "white", lw=0.9, z=3, alpha=0.85)
    x += W_HOT * 0.45
    bar(x, y, W_TAIL, "#E8EDF5", "#C7D2E3")
    ax.text(0.086, y + H_BAR / 2, "T%d" % (k + 1), ha="center", va="center",
            fontsize=8.2, color=MUTED)

bot_end = X0 + W_WORK + W_HOT * 0.45 + W_TAIL

# ---- 结束时刻的虚线
ax.plot([top_end, top_end], [0.545, 0.872], color=ACCENT, lw=0.9, ls=(0, (4, 3)), zorder=1)
ax.plot([bot_end, bot_end], [0.095, 0.412], color=GREEN, lw=0.9, ls=(0, (4, 3)), zorder=1)

# ---- 省下的时间
ax.annotate("", xy=(top_end - 0.004, 0.068), xytext=(bot_end + 0.004, 0.068),
            arrowprops=dict(arrowstyle="<|-|>", color=MUTED, lw=0.9))
ax.text((top_end + bot_end) / 2, 0.089, "省下的时间", ha="center", va="center",
        fontsize=8.0, color=MUTED)

# ---- 时间轴
ax.annotate("", xy=(X1, 0.026), xytext=(X0, 0.026),
            arrowprops=dict(arrowstyle="-|>", color=FAINT, lw=0.9))
ax.text(X1 + 0.010, 0.026, "时间", ha="left", va="center", fontsize=8.2, color=MUTED)

save(fig, "07", "fig07-02")
