import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

import numpy as np
from math import fsum

# ============================================================
# 图 9-1  固定步长、累加器与回滚的时间线（示意图，无数值含义）
# ============================================================
fig, (axA, axB) = plt.subplots(
    2, 1, figsize=(6.7, 4.2),
    gridspec_kw=dict(height_ratios=[1.0, 0.92], hspace=0.22))
for ax in (axA, axB):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

X0, X1 = 0.178, 0.975
TICK = (X1 - X0) / 12.0

# ---- 上半：渲染帧 / 物理步 / 累加器余量 ----
YR = 0.800         # 渲染帧基线
YP = 0.600         # 物理步柱带中心
label(axA, 0.012, YR + 0.010, "渲染帧\n144 Hz", fs=7.8, color=MUTED, ha="left")
label(axA, 0.012, YP, "物理步\n固定 $\\Delta t$", fs=7.8, color=MUTED, ha="left")

xs = np.linspace(X0, X1, 13)
axA.plot([X0, X1], [YR, YR], color=FAINT, lw=0.9, zorder=1)
for x in xs:
    axA.plot([x, x], [YR, YR - 0.038], color=FAINT, lw=0.9, zorder=2)

STEP = 3
bars = xs[::STEP]
for x in bars:
    axA.plot([x, x], [YP - 0.050, YP + 0.050], color=BLUE, lw=1.6, zorder=3)
    axA.scatter([x], [YR], s=15, color=BLUE, zorder=4, edgecolor="white", linewidth=0.6)

for i, x in enumerate(bars[:-1]):
    label(axA, x + 1.5 * TICK, YP - 0.125, f"$n+{i}$" if i else "$n$",
          fs=8.4, color=INK)

# 累加器余量 alpha：最后一步内已积累的一段
x_a0, x_a1 = bars[-2], bars[-2] + TICK
axA.add_patch(Rectangle((x_a0, YP - 0.046), x_a1 - x_a0, 0.092,
                        facecolor=ACCENT, edgecolor="none", alpha=0.26, zorder=5))
axA.plot([x_a1, x_a1], [YP - 0.046, YP + 0.046], color=ACCENT, lw=0.9, zorder=6)
label(axA, (x_a0 + x_a1) / 2, YP + 0.098, "$\\alpha$", fs=9.4, color=ACCENT)

# 此刻的渲染时刻
xi = x_a1
axA.scatter([xi], [YR], s=32, color=ACCENT, zorder=6, edgecolor="white", linewidth=0.8)
axA.plot([xi, xi], [YR, YP + 0.046], color=ACCENT, lw=0.8, ls=(0, (2, 2)), zorder=2)
label(axA, xi, YR + 0.088, "渲染取此刻插值", fs=7.6, color=ACCENT, ha="center")

bracket(axA, bars[0], bars[1], 0.300, "$\\Delta t$", color=MUTED, fs=8.8, dy=0.055)
label(axA, X0, 0.135,
      "余量 $\\alpha\\,\\Delta t$ 是已积累的时间，渲染值取相邻两个物理状态按 $\\alpha$ 混合",
      fs=7.8, color=MUTED, ha="left")
label(axA, 0.012, 0.960, "(a) 一个渲染帧落在两个物理状态之间", fs=8.6,
      color=INK, ha="left")

# ---- 下半：回滚 ----
Y1, Y2 = 0.700, 0.220
pts = np.linspace(X0 + 0.02, 0.800, 5)
axB.plot([pts[0], pts[-1]], [Y1, Y1], color=MUTED, lw=1.4, zorder=3)
for i, x in enumerate(pts):
    axB.scatter([x], [Y1], s=26, color=MUTED, zorder=4, edgecolor="white", linewidth=0.7)
    if i == len(pts) - 1:
        label(axB, x - 0.014, Y1 - 0.100, f"$t_{{n+{i}}}$", fs=7.8, color=MUTED, ha="right")
    else:
        label(axB, x, Y1 - 0.100, f"$t_{{n+{i}}}$" if i else "$t_n$", fs=7.8, color=MUTED)
label(axB, pts[0], Y1 + 0.125, "首次运行：用当时的本地输入", fs=8.4, color=MUTED, ha="left")

axB.plot([pts[0], pts[-1]], [Y2, Y2], color=ACCENT, lw=1.4, zorder=3)
for x in pts:
    axB.scatter([x], [Y2], s=26, color=ACCENT, zorder=4, edgecolor="white", linewidth=0.7)
label(axB, pts[0], Y2 - 0.150, "恢复快照后重放：用修正过的输入", fs=8.4,
      color=ACCENT, ha="left")

# 快照位置：两条线上的小方块 + 左侧文字
for yy in (Y1, Y2):
    axB.add_patch(Rectangle((pts[0] - 0.008, yy - 0.022), 0.016, 0.044,
                            facecolor=PAPER, edgecolor=ACCENT, lw=0.9, zorder=6))
label(axB, pts[0] - 0.020, (Y1 + Y2) / 2, "快照", fs=7.8, color=ACCENT, ha="right")

# 收到权威状态 -> 回滚
axB.plot([pts[-1], pts[-1]], [Y1, 0.435], color=ACCENT, lw=1.0, ls=(0, (2, 2)), zorder=2)
label(axB, pts[-1] + 0.016, 0.462, "收到权威状态", fs=7.8, color=ACCENT, ha="left")
arrow(axB, (pts[-1] - 0.006, 0.435), (pts[0] + 0.016, 0.435), color=ACCENT, lw=1.1, ms=9)
label(axB, (pts[0] + pts[-1]) / 2 + 0.02, 0.500, "回滚窗口 $W$ 帧", fs=8.0, color=ACCENT)
label(axB, 0.012, 0.960, "(b) 回滚的代价是重算窗口内的每一步", fs=8.6,
      color=INK, ha="left")

save(fig, "09", "fig09-01")


# ============================================================
# 图 9-2  不同求和顺序的舍入误差（真实计算）
#   x ~ U[0,1)，单精度累加，双精度 fsum 为参考；每点 32 组样本取中位数
# ============================================================
def pairwise_sum(a):
    a = a.astype(np.float32)
    while a.size > 1:
        if a.size % 2:
            a = np.append(a, np.float32(0.0))
        a = (a[0::2] + a[1::2]).astype(np.float32)
    return a[0]


def kahan_sum(X):
    """X: (n, trials) float32，沿第 0 维补偿求和，对 trials 向量化。"""
    s = np.zeros(X.shape[1], dtype=np.float32)
    c = np.zeros(X.shape[1], dtype=np.float32)
    for i in range(X.shape[0]):
        y = (X[i] - c).astype(np.float32)
        t = (s + y).astype(np.float32)
        c = ((t - s) - y).astype(np.float32)
        s = t
    return s


rng = np.random.default_rng(20261124)
N_LIST = np.array([100, 300, 1000, 3000, 10000, 30000, 100000])
TRIALS = 32

res = {"asc": [], "desc": [], "pair": [], "kahan": []}
for n in N_LIST:
    X = rng.random((TRIALS, n), dtype=np.float32)
    exact = np.array([fsum(row.astype(np.float64)) for row in X])
    asc = np.array([np.cumsum(row, dtype=np.float32)[-1] for row in X], dtype=np.float64)
    des = np.array([np.cumsum(row[::-1], dtype=np.float32)[-1] for row in X],
                   dtype=np.float64)
    par = np.array([pairwise_sum(row) for row in X], dtype=np.float64)
    kah = np.array(kahan_sum(np.ascontiguousarray(X.T)), dtype=np.float64)
    for k, v in (("asc", asc), ("desc", des), ("pair", par), ("kahan", kah)):
        res[k].append(np.median(np.abs(v - exact) / exact))

fig, ax = plt.subplots(figsize=(6.5, 3.5))
clean(ax, grid=True)

styles = [
    ("asc",   "顺序累加（从小到大）",     ACCENT, "-",  "o"),
    ("desc",  "逆序累加",                 PURPLE, "--", "s"),
    ("pair",  "两两配对（固定归约树）",   BLUE,   "-",  "^"),
    ("kahan", "Kahan 补偿求和",           GREEN,  "-",  "D"),
]
for key, name, color, ls, mk in styles:
    ax.loglog(N_LIST, res[key], color=color, ls=ls, marker=mk, ms=4.2, lw=1.4,
              mfc="white", mew=1.1, label=name, zorder=4)

ax.set_xlabel("参与求和的元素个数 $n$")
ax.set_ylabel("相对误差（中位数）")
ax.set_xlim(80, 1.35e5)
ax.grid(True, which="major", color=GRID, lw=0.7)
ax.grid(True, which="minor", color=GRID, lw=0.4, alpha=0.6)
ax.set_axisbelow(True)
leg = ax.legend(loc="upper left", fontsize=8.2, handlelength=2.4, borderaxespad=0.7)
for t in leg.get_texts():
    t.set_color(INK)

save(fig, "09", "fig09-02")

print("相对误差中位数")
for key in res:
    print(f"  {key:6s}", " ".join(f"{v:.2e}" for v in res[key]))
