import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

import numpy as np

# ============================================================
# 图 3-1  μ(I) 曲线与剪胀
#   mu(I) = mu_s + (mu_2 - mu_s) / (I_0/I + 1)
#   mu_s = 0.38 (21 deg), mu_2 = 0.64 (33 deg), I_0 = 0.3
#   phi(I) = phi_max - a I,  phi_max = 0.60, a = 0.15
# ============================================================
MU_S, MU_2, I_0 = 0.38, 0.64, 0.3
PHI_MAX, A_DIL = 0.60, 0.15

I = np.logspace(-4, 1, 600)
mu = MU_S + (MU_2 - MU_S) / (I_0 / I + 1.0)

fig, (axL, axR) = plt.subplots(1, 2, figsize=(6.8, 3.05),
                               gridspec_kw=dict(width_ratios=[1.32, 1.0], wspace=0.34))
for ax in (axL, axR):
    clean(ax, grid=False, spines=("left", "bottom"))

# ---------------- 左：mu(I) ----------------
axL.set_xscale("log")
axL.set_xlim(1e-4, 1e1)
axL.set_ylim(0.30, 0.79)

bands = [(1e-4, 1e-3, "#EFF4FF"), (1e-3, 1e-1, "#F5F3FF"), (1e-1, 1e1, "#FFFBEB")]
for x0, x1, c in bands:
    axL.axvspan(x0, x1, color=c, zorder=0)
axL.axvline(1e-3, color=GRID, lw=0.8, zorder=1)
axL.axvline(1e-1, color=GRID, lw=0.8, zorder=1)

axL.axhline(MU_S, color=FAINT, lw=0.8, ls=(0, (4, 3)), zorder=1)
axL.axhline(MU_2, color=FAINT, lw=0.8, ls=(0, (4, 3)), zorder=1)
axL.axvline(I_0, color=ACCENT, lw=0.7, ls=(0, (1.5, 2.5)), zorder=1, alpha=0.7)

axL.plot(I, mu, color=BLUE, lw=1.8, zorder=4, solid_capstyle="round")

axL.text(3e-4, 0.755, "准静态", fontsize=8.4, color=NAVY, ha="center", va="center", zorder=6)
axL.text(1e-2, 0.755, "稠密流动", fontsize=8.4, color=PURPLE, ha="center", va="center", zorder=6)
axL.text(1.0, 0.755, "惯性", fontsize=8.4, color=ACCENT, ha="center", va="center", zorder=6)

axL.text(1.55e-4, 0.392, r"$\mu_s=\tan 21^\circ$", fontsize=8.2, color=MUTED,
         ha="left", va="bottom", zorder=6)
axL.text(1.55e-4, 0.650, r"$\mu_2=\tan 33^\circ$", fontsize=8.2, color=MUTED,
         ha="left", va="bottom", zorder=6)
axL.text(I_0, 0.310, r"$I_0$", fontsize=8.4, color=ACCENT, ha="center", va="bottom", zorder=6)

axL.set_xlabel("惯性数 $I$")
axL.set_ylabel(r"$\mu=\tau/p$")
axL.set_xticks([1e-4, 1e-3, 1e-2, 1e-1, 1])
axL.set_xticklabels([r"$10^{-4}$", r"$10^{-3}$", r"$10^{-2}$", r"$10^{-1}$", r"$1$"])
axL.set_yticks([0.3, 0.4, 0.5, 0.6, 0.7])

# ---------------- 右：剪胀 ----------------
Ir = np.linspace(0.0, 0.20, 200)
phi = PHI_MAX - A_DIL * Ir
axR.plot(Ir, phi, color=GREEN, lw=1.8, zorder=4)
axR.set_xlim(0, 0.235)
axR.set_ylim(0.550, 0.615)
axR.set_xlabel("惯性数 $I$")
axR.set_ylabel(r"体积分数 $\varphi$")
axR.set_xticks([0, 0.05, 0.10, 0.15, 0.20])
axR.set_yticks([0.56, 0.57, 0.58, 0.59, 0.60])
axR.text(0.006, 0.6035, r"$\varphi_{\max}=0.60$", fontsize=8.2, color=MUTED,
         ha="left", va="center")
axR.text(0.150, 0.5600, "斜率 $-0.15$", fontsize=8.2, color=MUTED, ha="center",
         va="center")
axR.text(0.985, 0.025, "线性剪胀近似，稠密区有效", fontsize=7.6, color=FAINT,
         ha="right", va="bottom", transform=axR.transAxes)

save(fig, "03", "fig03-01")


# ============================================================
# 图 3-2  剪切带内的速度剖面（示意图）
#   指数形状 v/V 归一化到 z=0 处为 1、z=H 处为 0；xi = 6d
#   三种层厚 H = 40d / 12d / 4d
# ============================================================
XI = 6.0
zz = np.linspace(0, 44, 900)


def profile(H):
    raw = np.exp(-zz / XI)
    lo, hi = np.exp(-H / XI), 1.0
    v = (raw - lo) / (hi - lo)
    v[zz > H] = np.nan
    return v


fig, ax = plt.subplots(figsize=(6.6, 3.15))
clean(ax, spines=("left", "bottom"))

for H, col in ((40.0, BLUE), (12.0, ACCENT), (4.0, GREEN)):
    ax.plot(zz, profile(H), color=col, lw=1.7, zorder=4, solid_capstyle="round")

ax.set_xlim(-2.0, 47)
ax.set_ylim(-0.05, 1.14)
ax.set_xlabel(r"距剪切面的深度 $z/d$")
ax.set_ylabel(r"$v\,/\,V$")
ax.set_xticks([0, 4, 12, 20, 30, 40])
ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])

ax.annotate("", xy=(0, 1.045), xytext=(XI, 1.045),
            arrowprops=dict(arrowstyle="<|-|>", color=MUTED, lw=0.9, mutation_scale=7))
ax.text(XI / 2, 1.058, r"$\xi\approx 6d$", fontsize=8.4, color=MUTED,
        ha="center", va="bottom")

ax.text(29.0, 0.075, r"$H=40d$：下方静止", fontsize=8.4, color=BLUE,
        ha="left", va="bottom")
ax.text(12.8, 0.335, r"$H=12d$", fontsize=8.4, color=ACCENT, ha="left", va="bottom")
ax.text(2.6, 0.70, r"$H=4d$：近似线性", fontsize=8.4, color=GREEN,
        ha="left", va="bottom")

ax.axvline(12, color=GRID, lw=0.8, zorder=0)
ax.axvline(40, color=GRID, lw=0.8, zorder=0)
ax.text(0.985, 0.975, "示意图，曲线为指数形状，非实验数据", fontsize=7.6,
        color=FAINT, ha="right", va="top", transform=ax.transAxes)

save(fig, "03", "fig03-02")
