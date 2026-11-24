import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *
from matplotlib.patches import Patch

import numpy as np

# ============================================================
# 图 1-1  一次时间步的数学分解（流程框图）
# ============================================================
fig, ax = canvas(6.6, 3.95)

rows = [
    ("① 算力", "几何 + 材料 → 单元力", "张量代数、链式法则"),
    ("② 组装", "单元力 → 全局系统", "稀疏矩阵、网格拓扑"),
    ("③ 求解", "解 $\\mathbf{K}\\Delta\\mathbf{v}=\\mathbf{b}$", "条件数、迭代收敛率"),
    ("④ 积分", "更新位置与速度", "常微分方程、截断误差"),
    ("⑤ 碰撞", "几何查询 + 非穿透", "凸优化、互补条件"),
]
ys = [0.865, 0.690, 0.515, 0.340, 0.165]
h = 0.125
xl, wl = 0.085, 0.395
xm, wm = 0.545, 0.435

for i, ((tag, body, math), y) in enumerate(zip(rows, ys)):
    fc = SOFT[i % len(SOFT)]
    box(ax, xl, y - h / 2, wl, h, "", fc=fc, ec=INK, lw=1.0, z=3)
    label(ax, xl + 0.016, y + 0.030, tag, fs=9.4, color=INK, ha="left", va="center", weight="bold")
    label(ax, xl + 0.016, y - 0.033, body, fs=8.4, color=SLATE, ha="left", va="center")
    box(ax, xm, y - h / 2, wm, h, math, fc="white", ec=FAINT, lw=0.9, z=3, fs=8.8)
    ax.plot([xl + wl + 0.008, xm - 0.008], [y, y], color=FAINT, lw=0.8,
            ls=(0, (2.5, 2.2)), zorder=2)

for i in range(len(ys) - 1):
    arrow(ax, (xl + 0.13, ys[i] - h / 2 - 0.004), (xl + 0.13, ys[i + 1] + h / 2 + 0.004),
          color=MUTED, lw=1.1, ms=8)

curve_arrow(ax, [(xl - 0.014, ys[-1]), (0.046, ys[-1]), (0.046, ys[0]), (xl - 0.014, ys[0])],
            color=ACCENT, lw=1.1, ms=8)
label(ax, 0.021, (ys[0] + ys[-1]) / 2, "下一帧", fs=8.2, color=ACCENT, rot=90)

label(ax, 0.085, 0.045, "一帧之内按顺序走一遍，Δt 固定或自适应", fs=8.2, color=MUTED, ha="left")
save(fig, "01", "fig01-01")

# ============================================================
# 图 1-2  分段线性插值的误差随区间数的变化
#   f1(x) = sin(2*pi*x)，光滑；f2(x) = sqrt(x)，在 0 处导数无穷
#   定义域 [0, 1]，节点均匀分布，n 段，h = 1/n
#   误差取每个小区间中点上的最大值
# ============================================================
def f_smooth(x):
    return np.sin(2 * np.pi * x)


def f_sing(x):
    return np.sqrt(x)


def pl_interp(f, n, xq):
    nodes = np.linspace(0.0, 1.0, n + 1)
    return np.interp(xq, nodes, f(nodes))


def max_err(f, n):
    xq = (np.arange(4001) + 0.5) / 4001
    return np.max(np.abs(pl_interp(f, n, xq) - f(xq)))


fig, (axA, axB) = plt.subplots(1, 2, figsize=(6.8, 3.2),
                               gridspec_kw=dict(width_ratios=[1.06, 1.0], wspace=0.30))
for a in (axA, axB):
    clean(a, grid=True, spines=("left", "bottom"))

n_show = 6
xd = np.linspace(0, 1, 1201)
xn = np.linspace(0, 1, n_show + 1)
axA.fill_between(xd, f_smooth(xd), pl_interp(f_smooth, n_show, xd),
                 color=PURPLE, alpha=0.16, lw=0, zorder=2)
axA.plot(xd, f_smooth(xd), color=BLUE, lw=1.5, zorder=4)
axA.plot(xn, f_smooth(xn), color=ACCENT, lw=1.2, marker="o", ms=3.4, mfc="white",
         mew=0.9, zorder=5)
axA.set_xlim(-0.03, 1.03)
axA.set_ylim(-1.45, 1.35)
axA.set_xticks([0, 0.5, 1])
axA.set_yticks([-1, 0, 1])
axA.set_xlabel("$x$")
axA.set_ylabel("$f(x)$")
axA.legend(handles=[Line2D([], [], color=BLUE, lw=1.5, label="光滑解 $f$"),
                    Line2D([], [], color=ACCENT, lw=1.2, marker="o", ms=3.4,
                           mfc="white", mew=0.9, label="分段线性插值 $f_h$"),
                    Patch(facecolor=PURPLE, alpha=0.22, label="两者之差 $e_h$")],
           loc="lower left", fontsize=8.4, handlelength=1.9, borderpad=0.1,
           labelspacing=0.5, handletextpad=0.6)

ns = 2 ** np.arange(2, 11)
e1 = np.array([max_err(f_smooth, n) for n in ns])
e2 = np.array([max_err(f_sing, n) for n in ns])
p1 = np.polyfit(np.log(ns), np.log(e1), 1)[0]
p2 = np.polyfit(np.log(ns), np.log(e2), 1)[0]
axB.loglog(ns, e1, color=BLUE, marker="o", ms=3.6, lw=1.3, mfc="white", mew=0.8,
           label="$\\sin(2\\pi x)$，斜率 %.1f" % p1)
axB.loglog(ns, e2, color=ACCENT, marker="s", ms=3.6, lw=1.3, mfc="white", mew=0.8,
           label="$\\sqrt{x}$，斜率 %.1f" % p2)
axB.set_xlim(2.6, 900)
axB.set_ylim(2e-7, 0.9)
axB.set_xlabel("区间数 $n$")
axB.set_ylabel("最大误差")
axB.legend(loc="lower left", fontsize=8.4, handlelength=1.9, borderpad=0.1,
           labelspacing=0.6)
save(fig, "01", "fig01-02")

# ============================================================
# 图 1-3  三类问题的关系（示意图）
# ============================================================
fig, ax = canvas(6.6, 3.45)
box(ax, 0.245, 0.775, 0.51, 0.155,
    "初值问题\n给定状态，沿时间往前推", fc=SOFT[1], ec=BLUE, fs=9.0, lw=1.1)
box(ax, 0.020, 0.300, 0.395, 0.145,
    "边值问题\n给定两端的条件，求中间的场", fc=SOFT[2], ec=GREEN, fs=9.0, lw=1.1)
box(ax, 0.585, 0.300, 0.395, 0.145,
    "反问题\n给定结果，反推参数", fc=SOFT[0], ec=ACCENT, fs=9.0, lw=1.1)

arrow(ax, (0.375, 0.770), (0.250, 0.455), color=GREEN, lw=1.1, rad=0.16)
label(ax, 0.262, 0.630, "每一步内部", fs=8.2, color=GREEN, ha="right")
label(ax, 0.262, 0.575, "先解一次平衡", fs=8.2, color=GREEN, ha="right")

arrow(ax, (0.428, 0.372), (0.572, 0.372), color=MUTED, lw=1.1, style="<|-|>")
label(ax, 0.500, 0.412, "同一套方程", fs=8.2, color=MUTED)

arrow(ax, (0.760, 0.455), (0.660, 0.770), color=ACCENT, lw=1.1, rad=-0.16)
label(ax, 0.768, 0.630, "参数代回模型", fs=8.2, color=ACCENT, ha="left")
label(ax, 0.768, 0.575, "再跑一次演化", fs=8.2, color=ACCENT, ha="left")

label(ax, 0.500, 0.748, "例：整段动画的逐帧演化", fs=8.2, color=SLATE, ha="center", va="top")
label(ax, 0.020, 0.258, "例：隐式步的牛顿迭代、\n压力泊松、静力平衡", fs=8.2, color=SLATE,
      ha="left", va="top")
label(ax, 0.585, 0.258, "例：从拍摄到的形变\n反推杨氏模量", fs=8.2, color=SLATE,
      ha="left", va="top")
label(ax, 0.500, 0.085, "时间向前  →", fs=8.6, color=BLUE, ha="center")
save(fig, "01", "fig01-03")
