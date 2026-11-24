import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

# ============================================================
# 图 9-1  Laplace 压差与曲率半径（按 dp = sigma(1/R1 + 1/R2) 计算）
# ============================================================
SIGMA = 0.0728          # 水 20 摄氏度，N/m
fig, axes = plt.subplots(1, 2, figsize=(6.9, 3.15))
fig.subplots_adjust(wspace=0.32)

# ---- 左：三种曲率配置的压差-半径曲线 ----
ax = axes[0]
R_mm = np.logspace(-2, 1, 400)
R = R_mm * 1e-3
ax.loglog(R_mm, 2 * SIGMA / R, color=BLUE, lw=1.7, label="球形液滴 $2\\sigma/R$，$R=1$ mm 时 146 Pa")
ax.loglog(R_mm, SIGMA / R, color=GREEN, lw=1.7, label="圆柱液柱 $\\sigma/R$，73 Pa")
ax.loglog(R_mm, 4 * SIGMA / R, color=ACCENT, lw=1.7, label="肥皂泡 $4\\sigma/R$，291 Pa")

for k, col in ((2, BLUE), (1, GREEN), (4, ACCENT)):
    ax.plot([1.0], [k * SIGMA / 1e-3], "o", ms=4.8, color=col, zorder=5,
            markeredgecolor="white", markeredgewidth=0.8)

ax.set_xlim(1e-2, 1e1)
ax.set_ylim(1, 3e4)
ax.set_xlabel("曲率半径 $R$ / mm")
ax.set_ylabel("Laplace 压差 $\\Delta p$ / Pa")
ax.grid(True, which="major", color=GRID, lw=0.7)
ax.set_axisbelow(True)
clean(ax, grid=False)
ax.grid(True, which="major", color=GRID, lw=0.7)
ax.set_axisbelow(True)
ax.legend(loc="lower left", fontsize=7.5, handlelength=1.6, borderaxespad=0.6)

# ---- 右：固定第二个半径，看第一个半径的作用 ----
ax = axes[1]
ax.axhspan(-100, 0, color="#FDF2F8", zorder=0)
ax.axhline(0, color=FAINT, lw=0.9, zorder=1)
for R2_mm, col, lab, ls in ((2.0, GREEN, "$R_2=+2$ mm", "-"),
                            (np.inf, MUTED, "$R_2=\\infty$", (0, (4, 2))),
                            (-2.0, PINK, "$R_2=-2$ mm", "-")):
    k2 = 0.0 if not np.isfinite(R2_mm) else 1.0 / (R2_mm * 1e-3)
    ax.semilogx(R_mm, SIGMA * (1.0 / R + k2), color=col, lw=1.6, ls=ls, label=lab)

ax.plot([2.0], [0.0], "o", ms=5.0, color=PINK, zorder=5,
        markeredgecolor="white", markeredgewidth=0.8)
label(ax, 3.9, -70, "$R_1=R_2$，两项抵消\n马鞍面", fs=8.0, color=PINK, ha="center", va="center")

ax.set_xlim(0.1, 10)
ax.set_ylim(-100, 800)
ax.set_xlabel("曲率半径 $R_1$ / mm")
ax.set_ylabel("Laplace 压差 $\\Delta p$ / Pa")
clean(ax)
ax.grid(True, which="major", color=GRID, lw=0.7)
ax.set_axisbelow(True)
ax.legend(loc="upper right", fontsize=8.0, handlelength=1.7, borderaxespad=0.6)

save(fig, "09", "fig09-01")

# ============================================================
# 图 9-2  粘性扩散时间尺度与显式稳定性上限（直接按公式计算）
# ============================================================
NU = [("水", 1.0e-6, BLUE), ("橄榄油", 9.0e-5, GREEN),
      ("甘油", 1.1e-3, PURPLE), ("蜂蜜", 7.0e-3, ACCENT)]

fig, axes = plt.subplots(1, 2, figsize=(6.9, 3.15))
fig.subplots_adjust(wspace=0.34)

# ---- 左：tau = L^2 / nu ----
ax = axes[0]
L_mm = np.logspace(-1, 3, 400)
L = L_mm * 1e-3
for name, nu, col in NU:
    ax.loglog(L_mm, L ** 2 / nu, color=col, lw=1.6, label="%s  $\\nu=%.0e$" % (name, nu))

ax.plot([1.0], [1e-6 / 1.0e-6], "o", ms=4.6, color=BLUE, zorder=5,
        markeredgecolor="white", markeredgewidth=0.8)
ax.plot([1.0], [1e-6 / 7.0e-3], "o", ms=4.6, color=ACCENT, zorder=5,
        markeredgecolor="white", markeredgewidth=0.8)
label(ax, 1.55, 9.0, "1 s", fs=8.0, color=BLUE, ha="left", va="bottom")
label(ax, 1.55, 2.2e-5, "$1.4\\times10^{-4}$ s", fs=8.0, color=ACCENT, ha="left", va="top")

ax.set_xlim(0.1, 1e3)
ax.set_ylim(1e-7, 1e8)
ax.set_xlabel("长度尺度 $L$ / mm")
ax.set_ylabel("扩散时间 $\\tau=L^{2}/\\nu$ / s")
clean(ax)
ax.grid(True, which="major", color=GRID, lw=0.7)
ax.set_axisbelow(True)
ax.legend(loc="upper left", fontsize=7.8, handlelength=1.5, borderaxespad=0.6)

# ---- 右：显式格式稳定上限 dt = h^2 / (6 nu) ----
ax = axes[1]
h_mm = np.logspace(-1, 2, 400)
h = h_mm * 1e-3
for name, nu, col in NU:
    ax.loglog(h_mm, h ** 2 / (6 * nu), color=col, lw=1.6, label=name)

for yv in (1.0 / 60.0, 1e-3):
    ax.axhline(yv, color=FAINT, lw=0.9, ls=(0, (4, 2)), zorder=1)
label(ax, 92, 0.0125, "1/60 s", fs=7.4, color=MUTED, ha="right", va="top")
label(ax, 92, 7.5e-4, "1 ms", fs=7.4, color=MUTED, ha="right", va="top")

ax.plot([1.0], [1e-6 / (6 * 7.0e-3)], "o", ms=4.6, color=ACCENT, zorder=5,
        markeredgecolor="white", markeredgewidth=0.8)
label(ax, 1.35, 3.0e-6, "$2.4\\times10^{-5}$ s\n约 700 子步/帧", fs=7.8, color=ACCENT,
      ha="left", va="center")

ax.set_xlim(0.1, 1e2)
ax.set_ylim(1e-8, 1e4)
ax.set_xlabel("格子边长 $h$ / mm")
ax.set_ylabel("显式稳定上限 $\\Delta t=h^{2}/(6\\nu)$ / s")
clean(ax)
ax.grid(True, which="major", color=GRID, lw=0.7)
ax.set_axisbelow(True)
ax.legend(loc="upper left", fontsize=7.8, handlelength=1.5, borderaxespad=0.6)

save(fig, "09", "fig09-02")
