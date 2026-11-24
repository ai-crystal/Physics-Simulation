import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

import numpy as np

# ============================================================
# 图 2-1  圆管泊肃叶流（真实解析解）
#   u(r) = dP/(4 mu L) * (R^2 - r^2),  Q = pi R^4 dP / (8 mu L)
#   水：R = 10 mm, mu = 1e-3 Pa s, dP/L = 1 Pa/m
#   蜂蜜：R = 20 mm, mu = 10 Pa s, dP/L = 400 Pa/m
# ============================================================
R_W, MU_W, G_W = 10e-3, 1e-3, 1.0        # 水
R_H, MU_H, G_H = 20e-3, 10.0, 400.0      # 蜂蜜

fig, (axL, axR) = plt.subplots(1, 2, figsize=(6.8, 2.92),
                               gridspec_kw=dict(width_ratios=[1.0, 1.22], wspace=0.34))

# ---------- 左：无量纲剖面 ----------
clean(axL, grid=True, spines=("left", "bottom"))
axL.grid(axis="y", color=GRID, lw=0.7)
rr = np.linspace(-1, 1, 400)
axL.plot(rr, 1 - rr ** 2, color=BLUE, lw=1.6, zorder=4)
axL.axhline(0.5, color=ACCENT, lw=1.0, ls=(0, (5, 3)), zorder=3)
axL.fill_between(rr, 0, 1 - rr ** 2, color=BLUE, alpha=0.07, zorder=1)
axL.set_xlim(-1.12, 1.12)
axL.set_ylim(0, 1.16)
axL.set_xticks([-1, -0.5, 0, 0.5, 1])
axL.set_xlabel("$r/R$")
axL.set_ylabel("$u\\,/\\,u_{\\max}$")
label(axL, 0.80, 0.527, "0.5", fs=7.4, color=ACCENT, ha="left", va="bottom")
label(axL, 0.02, 1.055, "$u_{\\max}=\\Delta p\\,R^{2}/(4\\mu L)$", fs=8.2, color=BLUE,
      ha="left")
label(axL, 0.055, 0.235, "$u=u_{\\max}\\left(1-(r/R)^{2}\\right)$", fs=8.4, color=INK,
      ha="left")

# ---------- 右：流量与半径 ----------
clean(axR, grid=True, spines=("left", "bottom"))
axR.grid(True, color=GRID, lw=0.7, which="major")
axR.set_xscale("log")
axR.set_yscale("log")
Rs = np.logspace(np.log10(1e-3), np.log10(4e-2), 200)
Qw = np.pi * Rs ** 4 * G_W / (8 * MU_W * 1.0)
Qh = np.pi * Rs ** 4 * G_H / (8 * MU_H * 1.0)
axR.plot(Rs * 1e3, Qw * 1e6, color=BLUE, lw=1.5, zorder=4, label="水（$\\mu=10^{-3}$ Pa·s）")
axR.plot(Rs * 1e3, Qh * 1e6, color=ACCENT, lw=1.5, zorder=4, label="蜂蜜（$\\mu=10$ Pa·s）")
for R0, Q0, c in ((R_W, np.pi * R_W ** 4 * G_W / (8 * MU_W), BLUE),
                  (R_H, np.pi * R_H ** 4 * G_H / (8 * MU_H), ACCENT)):
    axR.plot([R0 * 1e3], [Q0 * 1e6], marker="o", ms=5.2, mfc="white", mec=c, mew=1.4,
             zorder=5)
axR.set_xlim(1, 45)
axR.set_ylim(1e-4, 1e2)
axR.set_xlabel("管半径 $R$ (mm)")
axR.set_ylabel("流量 $Q$ (mL/s)")
axR.legend(loc="lower right", fontsize=7.6, handlelength=1.6, borderaxespad=0.4)
label(axR, 1.35, 30, "斜率 4", fs=8.2, color=MUTED, ha="left")
label(axR, 1.35, 12, "$Q\\propto R^{4}$", fs=8.6, color=INK, ha="left")

save(fig, "02", "fig02-01")


# ============================================================
# 图 2-2  雷诺数与流态（示意；Re 由标注的 U、L、nu 算出）
# ============================================================
fig, ax = plt.subplots(figsize=(6.86, 2.86))
clean(ax, spines=("bottom",))
ax.set_xscale("log")
ax.set_xlim(1e-6, 2e8)
ax.set_ylim(0, 1)
ax.set_yticks([])

# 流态底色
ax.axvspan(1e-6, 1.0, color="#F3F4F6", zorder=0)
ax.axvspan(1.0, 2300, color="#EFF4FF", zorder=0)
ax.axvspan(2300, 4000, color="#FDF2E9", zorder=0)
ax.axvspan(4000, 2e8, color="#FDF2F8", zorder=0)
ax.axvline(2300, color=FAINT, lw=0.9, ls=(0, (4, 3)), zorder=1)
ax.axvline(4000, color=FAINT, lw=0.9, ls=(0, (4, 3)), zorder=1)
ax.axhline(0.50, color="#D1D5DB", lw=0.9, zorder=1)

label(ax, 6e-4, 0.955, "蠕流", fs=8.4, color=MUTED)
label(ax, 6e1, 0.955, "层流", fs=8.4, color=BLUE)
label(ax, 2e6, 0.955, "湍流", fs=8.4, color=PINK)

# 过渡区标注（两条虚线之间，靠下，避免与圆点文字相撞）
label(ax, 3050, 0.070, "过渡", fs=7.2, color=GOLD, rot=90, va="bottom")

# 实例：(Re, 名称, 上方/下方, 横向偏移倍数)
NU_AIR, NU_W, NU_BL, NU_H = 1.5e-5, 1e-6, 3e-6, 7e-3
cases = [
    (30e-6 * 1e-6 / NU_W, "细菌游泳", -1, 1.0),
    (0.5e-3 * 8e-6 / NU_BL, "毛细血管血液", +1, 1.0),
    (0.01 * 0.05 / NU_H, "蜂蜜", -1, 1.0),
    (2.0 * 2e-3 / NU_AIR, "雨滴", +1, 1.0),
    (0.3 * 8e-3 / NU_W, "水龙头", -1, 1.0),
    (2.0 * 15e-3 / NU_W, "花园水管", +1, 1.0),
    (1.0 * 1.0 / NU_W, "河流", -1, 1.0),
]
for Re, name, side, s in cases:
    y = 0.50 + side * 0.115
    ax.plot([Re, Re], [0.50, y], color=FAINT, lw=0.8, zorder=2)
    ax.plot([Re], [0.50], marker="o", ms=5.0, mfc="white", mec=INK, mew=1.1, zorder=6)
    label(ax, Re, y + side * 0.055, name, fs=7.8, color=INK,
          va="bottom" if side > 0 else "top")

ax.set_xlabel("雷诺数 $Re=UL/\\nu$（对数刻度，圆管流动）")
fig.subplots_adjust(bottom=0.24, top=0.97)

save(fig, "02", "fig02-02")
