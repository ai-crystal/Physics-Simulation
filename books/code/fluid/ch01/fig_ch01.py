import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

import numpy as np

# ============================================================
# 图 1-1  拉格朗日与欧拉：两种记录方式（示意）
# ============================================================
fig, (axL, axR) = plt.subplots(1, 2, figsize=(6.86, 3.10),
                               gridspec_kw=dict(wspace=0.06))

for ax in (axL, axR):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

# ---------- 左：拉格朗日 ----------
OFFS = [0.052, 0.017, -0.017, -0.052]
COLS = [INK, BLUE, GREEN, PURPLE]
xs = np.linspace(0.05, 0.95, 240)


def traj(d):
    """沿 x 向右下弯的中心线，加一个随流动收窄的横向偏移 d。"""
    return 0.72 - 0.30 * (xs - 0.05) ** 1.15 + d * (1.0 - 0.35 * (xs - 0.05))


# 通道壁（两条浅灰线，示意流动区域）
for d in (0.108, -0.108):
    axL.plot(xs, traj(d), color=GRID, lw=1.0, zorder=1)

station = [0.10, 0.37, 0.64, 0.89]
for k, d in enumerate(OFFS):
    yy = traj(d)
    axL.plot(xs, yy, color=COLS[k], lw=1.25, zorder=3)
    for i, sx in enumerate(station):
        j = int(np.argmin(np.abs(xs - sx)))
        axL.add_patch(Circle((xs[j], yy[j]), 0.0128, facecolor="white",
                             edgecolor=COLS[k], lw=1.1, zorder=5))
        axL.add_patch(Circle((xs[j], yy[j]), 0.0052, facecolor=COLS[k],
                             edgecolor="none", alpha=0.85 - 0.17 * i, zorder=6))

axL.annotate("", xy=(0.70, 0.822), xytext=(0.40, 0.822),
             arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.0,
                             connectionstyle="arc3,rad=-0.10"))
label(axL, 0.31, 0.860, "时间", fs=8.2, color=MUTED, ha="left")

txt = ["每个微团带一个永久标签 $\\mathbf{X}$",
       "位置写成 $\\mathbf{x}(\\mathbf{X},t)$，速度是它对时间的偏导",
       "存的是每个微团的传记，身份不丢"]
for i, s in enumerate(txt):
    label(axL, 0.045, 0.205 - 0.058 * i, s, fs=8.0, color=INK, ha="left")

label(axL, 0.5, 0.985, "拉格朗日", fs=9.6, color=INK, weight="bold", va="top")

# ---------- 右：欧拉 ----------
nx, ny = 9, 6
x0, x1, y0, y1 = 0.11, 0.93, 0.30, 0.86
gx = np.linspace(x0, x1, nx)
gy = np.linspace(y0, y1, ny)
grid(axR, x0, y0, x1 - x0, y1 - y0, nx - 1, ny - 1, color=GRID, lw=0.7)
axR.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False,
                        edgecolor=FAINT, lw=1.0, zorder=2))

for yy in gy:
    for xx in gx:
        vx, vy = 1.0, -0.42 * (xx - 0.5) * 2.4
        s, nrm = 0.030, np.hypot(1.0, vy)
        axR.annotate("", xy=(xx + s * vx / nrm, yy + s * vy / nrm), xytext=(xx, yy),
                     arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=0.85,
                                     mutation_scale=6.5, alpha=0.75), zorder=3)
        axR.add_patch(Circle((xx, yy), 0.0045, facecolor=INK, edgecolor="none", zorder=4))

tt = np.linspace(x0, x1, 120)
for c, col in ((0.115, TEAL), (0.0, ACCENT), (-0.115, PINK)):
    axR.plot(tt, 0.56 + c - 0.34 * (tt - 0.40) ** 2, color=col, lw=1.0,
             ls=(0, (5, 2)), alpha=0.9, zorder=2)

px, py = gx[7], gy[1]
axR.annotate("", xy=(px, py), xytext=(0.66, 0.175),
             arrowprops=dict(arrowstyle="-", color=FAINT, lw=0.8,
                             connectionstyle="arc3,rad=-0.22"))
label(axR, 0.50, 0.155, "格点不动，记 $\\mathbf{u}_{ij}$、$p_{ij}$", fs=8.0, color=MUTED,
      ha="center")
label(axR, 0.50, 0.075, "物质从格子之间穿过（虚线）", fs=8.0, color=MUTED, ha="center")

label(axR, 0.5, 0.985, "欧拉", fs=9.6, color=INK, weight="bold", va="top")

save(fig, "01", "fig01-01")


# ============================================================
# 图 1-2  刚体旋转场中的局部导数与随体导数（真实计算）
#   u = (-Omega*y, Omega*x), Omega = 1 rad/s, phi = x
#   局部导数 dphi/dt = 0；随体导数 Dphi/Dt = -Omega*y
# ============================================================
OM = 1.0
fig, axs = plt.subplots(1, 3, figsize=(6.9, 2.72),
                        gridspec_kw=dict(wspace=0.62, width_ratios=[1, 1.12, 1.10]))

# ---- (a) 场与流线 ----
ax = axs[0]
clean(ax, spines=("left", "bottom"))
ax.set_xlim(-1.05, 1.05)
ax.set_ylim(-1.05, 1.16)
ax.set_aspect("equal", adjustable="box")
xx = np.linspace(-1, 1, 9)
yy = np.linspace(-1, 1, 9)
X, Y = np.meshgrid(xx, yy)
ax.quiver(X, Y, -OM * Y, OM * X, color=BLUE, width=0.0055, scale=17,
          headwidth=3.2, headlength=3.8, alpha=0.85, zorder=3)
for lev in (-0.8, -0.4, 0.0, 0.4, 0.8):
    if lev == 0.0:
        ax.plot([0, 0], [-1.02, 1.02], color=ACCENT, lw=1.2, zorder=2)
    else:
        ax.plot([lev, lev], [-1.02, 1.02], color=FAINT, lw=0.8,
                ls=(0, (4, 3)), zorder=2)
for r in (0.35, 0.95):
    th = np.linspace(0, 2 * np.pi, 200)
    ax.plot(r * np.cos(th), r * np.sin(th), color=GRID, lw=0.8, zorder=1)
th = np.linspace(0, 2 * np.pi, 200)
ax.plot(0.6 * np.cos(th), 0.6 * np.sin(th), color=PINK, lw=0.9,
        ls=(0, (3, 2)), alpha=0.85, zorder=4)
ax.plot([0.6], [0.0], marker="o", ms=5.2, mfc="white", mec=PINK, mew=1.4, zorder=6)
ax.set_xlabel("$x$")
ax.set_ylabel("$y$")
label(ax, 0.03, 1.07, "$\\phi=0$", fs=7.8, color=ACCENT, ha="left")

# ---- (b) 随体导数分布 ----
ax = axs[1]
clean(ax, spines=("left", "bottom"))
ax.set_xlim(-1.05, 1.05)
ax.set_ylim(-1.05, 1.05)
ax.set_aspect("equal", adjustable="box")
n = 240
gx2 = np.linspace(-1, 1, n)
gy2 = np.linspace(-1, 1, n)
GX, GY = np.meshgrid(gx2, gy2)
D = -OM * GY
im = ax.imshow(D, extent=[-1, 1, -1, 1], origin="lower", cmap="RdBu_r",
               vmin=-1, vmax=1, aspect="equal", zorder=1, interpolation="bilinear")
ax.contour(GX, GY, D, levels=[0.0], colors=[INK], linewidths=0.9, zorder=3)
ax.set_xlabel("$x$")
ax.set_ylabel("$y$")
cb = fig.colorbar(im, ax=ax, fraction=0.043, pad=0.03, ticks=[-1, 0, 1])
cb.ax.tick_params(labelsize=8)

# ---- (c) 一个微团走一圈 ----
ax = axs[2]
clean(ax, grid=True, spines=("left", "bottom"))
ax.grid(axis="y", color=GRID, lw=0.7)
t = np.linspace(0, 2 * np.pi / OM, 400)
r0 = 0.6
ax.plot(t, r0 * np.cos(OM * t), color=PINK, lw=1.5, zorder=4,
        label="微团携带的 $\\phi$")
ax.plot(t, np.full_like(t, r0), color=BLUE, lw=1.3, ls=(0, (5, 3)), zorder=3,
        label="固定点的读数")
ax.axhline(0, color=FAINT, lw=0.8, zorder=1)
ax.set_xlim(0, t[-1])
ax.set_ylim(-0.92, 0.92)
ax.set_yticks([-0.6, -0.3, 0, 0.3, 0.6])
ax.set_xticks([0, np.pi / 2, np.pi, 3 * np.pi / 2, 2 * np.pi])
ax.set_xticklabels(["0", "$\\pi/2$", "$\\pi$", "$3\\pi/2$", "$2\\pi$"])
ax.set_xlabel("$\\Omega t$")
ax.legend(loc="lower left", fontsize=7.4, handlelength=1.7, borderaxespad=0.25,
          labelspacing=0.35)

TITLES = ["(a) 场 $\\phi=x$ 不随时间变", "(b) 随体导数 $-\\Omega y$", "(c) 微团走一圈"]
for a, t in zip(axs, TITLES):
    pos = a.get_position()
    fig.text(pos.x0, 0.975, t, ha="left", va="top", fontsize=8.4, color=INK)

save(fig, "01", "fig01-02")
