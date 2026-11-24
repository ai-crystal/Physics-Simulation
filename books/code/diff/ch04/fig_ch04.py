import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

# ============================================================
# 图 4-1  法向力与间隙：硬接触、软接触、softplus、障碍（真实计算）
#   k = 2000 N/m, eps = 2 mm, 障碍激活距离 ghat = 5 mm, kappa = 838
# ============================================================
k = 2000.0
eps = 2.0e-3
ghat = 5.0e-3
kappa = 838.0
m = 0.5
g_acc = 9.8

gmm = np.linspace(-8.0, 8.0, 1200)          # 间隙，单位 mm
g = gmm * 1e-3

pen = k * np.maximum(0.0, -g)
soft = k * eps * np.log1p(np.exp(-g / eps))
gb = np.clip(g, 1e-6, ghat - 1e-9)
bar = kappa * (2.0 * (gb - ghat) * np.log(gb / ghat) + (gb - ghat) ** 2 / gb)
bar[g <= 0] = np.nan
bar[g >= ghat] = 0.0

fig, (axA, axB) = plt.subplots(1, 2, figsize=(6.9, 3.35),
                               gridspec_kw=dict(width_ratios=[1.0, 1.0], wspace=0.30))

for a in (axA, axB):
    clean(a, grid=False, spines=("left", "bottom"))
    a.set_xlim(-8.0, 8.0)
    a.set_xlabel("间隙 $g$ (mm)")
    a.axvline(0.0, color=FAINT, lw=0.8, zorder=1)

# ---------- (a) 力 ----------
axA.axvspan(-8.0, 0.0, facecolor="#EFEFEF", edgecolor="none", zorder=0)
axA.fill_between([-8.0, 0.0], 0, 18.5, facecolor="none", hatch="////",
                 edgecolor="#D9D9D9", lw=0.0, zorder=1)
axA.plot(gmm[gmm >= 0], np.zeros_like(gmm[gmm >= 0]), color=INK, lw=1.9, zorder=4)
axA.plot([0, 0], [0, 10.5], color=INK, lw=1.2, ls=(0, (4, 3)), zorder=4)

axA.plot(gmm, pen, color=ACCENT, lw=1.7, zorder=5)
axA.plot(gmm, soft, color=BLUE, lw=1.7, zorder=5)
axA.plot(gmm, bar, color=PURPLE, lw=1.7, zorder=5)

axA.axhline(m * g_acc, color=MUTED, lw=0.9, ls=(0, (2, 2)), zorder=3)
label(axA, 7.6, m * g_acc + 0.5, "重力 $mg = 4.9$ N", fs=7.8, color=MUTED, ha="right")

label(axA, 0.55, 11.4, "任意值", fs=8.0, color=INK, ha="left")
label(axA, -7.5, 0.9, "不允许的区域", fs=8.0, color=MUTED, ha="left")

axA.set_ylim(0, 18.5)
axA.set_ylabel("法向力 $\\lambda$ (N)")

handles = [
    Line2D([], [], color=INK, lw=1.9, label="硬接触"),
    Line2D([], [], color=ACCENT, lw=1.7, label="软接触 $k\\max(0,-g)$"),
    Line2D([], [], color=BLUE, lw=1.7, label="softplus 平滑"),
    Line2D([], [], color=PURPLE, lw=1.7, label="障碍函数"),
]
fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, -0.115), ncol=4,
           fontsize=7.9, frameon=False, handlelength=1.9, columnspacing=1.3,
           handletextpad=0.55)

# ---------- (b) 接触刚度 ----------
axB.plot(gmm[gmm >= 0], np.zeros_like(gmm[gmm >= 0]), color=INK, lw=1.9, zorder=4)
axB.plot([0, 0], [0, k], color=ACCENT, lw=1.9, zorder=5)
axB.plot(gmm[gmm <= 0], np.full(gmm[gmm <= 0].shape, k), color=ACCENT, lw=1.9, zorder=5)

d_soft = k / (1.0 + np.exp(g / eps))
axB.plot(gmm, d_soft, color=BLUE, lw=1.7, zorder=5)

dbar = -kappa * (2.0 * np.log(gb / ghat) + 4.0 * (gb - ghat) / gb - ((gb - ghat) / gb) ** 2)
dbar[g <= 0] = np.nan
dbar[g >= ghat] = 0.0
axB.plot(gmm, dbar, color=PURPLE, lw=1.7, zorder=5)

label(axB, 0.40, 1690, "一步到 $k$", fs=7.8, color=ACCENT, ha="left", va="bottom")
label(axB, 3.9, 2300, "贴上去时冲高", fs=7.8, color=PURPLE, ha="left", va="center")

axB.set_xlim(-8.0, 8.0)
axB.set_ylim(0, 3400)
axB.set_xlabel("间隙 $g$ (mm)")
axB.set_ylabel("$-\\partial \\lambda / \\partial g$ (N/m)")
label(axB, -7.6, 3230, "硬接触：$g\\neq 0$ 处为零，$g = 0$ 处不存在",
      fs=7.6, color=MUTED, ha="left", va="top")

save(fig, "04", "fig04-01")

# ============================================================
# 图 4-2  接触梯度偏差（一维真实计算）
#   自由落体，g = 9.8，dt = 1/240，检测首次穿透时刻
# ============================================================
gc = 9.8
dt = 1.0 / 240.0
h = np.linspace(0.10, 0.60, 1200)

T_exact = np.sqrt(2.0 * h / gc)
T_disc = np.ceil(T_exact / dt) * dt

delta = 2.0e-3
hh = np.linspace(0.10, 0.60, 201)
T_h = np.ceil(np.sqrt(2.0 * hh / gc) / dt) * dt
T_hp = np.ceil(np.sqrt(2.0 * (hh + delta) / gc) / dt) * dt
d_num = (T_hp - T_h) / delta
spike = d_num > 0.5 * dt / delta

d_exact = 1.0 / np.sqrt(2.0 * gc * h)

fig, (axA, axB) = plt.subplots(1, 2, figsize=(6.9, 3.35),
                               gridspec_kw=dict(width_ratios=[1.0, 1.0], wspace=0.26))

mz = h <= 0.19
axA.plot(h[mz], (T_disc - T_exact)[mz] * 1000.0, color=ACCENT, lw=1.0, drawstyle="steps-post", zorder=4)
axA.axhline(dt * 1000.0, color=BLUE, lw=0.9, ls=(0, (4, 3)), zorder=3)
axA.set_xlim(0.10, 0.19)
axA.set_ylim(0.0, 5.0)
axA.set_xlabel("初始高度 $h$ (m)")
axA.set_ylabel("离散时刻减解析时刻 (ms)")
clean(axA, grid=True, spines=("left", "bottom"))
label(axA, 0.104, 4.62, "齿高 = 步长 Δt = 4.17 ms（局部放大）", fs=7.9, color=BLUE, ha="left", va="center")
axB.plot(h, d_exact, color=BLUE, lw=1.9, zorder=5)
axB.axhline(dt / delta, color=ACCENT, lw=0.9, ls=(0, (4, 3)), alpha=0.75, zorder=2)
axB.plot(hh[spike], np.full(spike.sum(), dt / delta), marker="|", ls="none",
         ms=5.5, mew=1.1, color=ACCENT, zorder=4)
axB.set_xlim(0.10, 0.60)
axB.set_ylim(-0.08, 2.55)
axB.set_yticks([0.0, 0.5, 1.0, 1.5, 2.0])
axB.set_xlabel("初始高度 $h$ (m)")
axB.set_ylabel("$\\mathrm{d}T/\\mathrm{d}h$ (s/m)")
clean(axB, grid=True, spines=("left", "bottom"))
label(axB, 0.118, 2.24, "$\\Delta t/\\delta \\approx 2.08$：差分只给出这个值", fs=7.9,
      color=ACCENT, ha="left", va="center")
label(axB, 0.30, 0.09, "解析导数 1/√(2gh)", fs=7.9, color=BLUE, ha="left", va="center")

save(fig, "04", "fig04-02")
