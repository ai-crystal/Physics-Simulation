import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *
import numpy as np


# ---------------------------------------------------------------- 核函数
# 三次样条核（M4）的轮廓函数，W = alpha_d * f(q)，q = r/h，支撑 0 <= q < 2。
def f_kernel(q):
    q = np.asarray(q, float)
    out = np.zeros_like(q)
    m1 = q < 1.0
    m2 = (q >= 1.0) & (q < 2.0)
    out[m1] = 1.0 - 1.5 * q[m1] ** 2 + 0.75 * q[m1] ** 3
    out[m2] = 0.25 * (2.0 - q[m2]) ** 3
    return out


def df_kernel(q):
    q = np.asarray(q, float)
    out = np.zeros_like(q)
    m1 = q < 1.0
    m2 = (q >= 1.0) & (q < 2.0)
    out[m1] = -3.0 * q[m1] + 2.25 * q[m1] ** 2
    out[m2] = -0.75 * (2.0 - q[m2]) ** 2
    return out


# ---------------------------------------------------------------- 图 7-1
fig, axs = plt.subplots(1, 3, figsize=(6.9, 2.85),
                        gridspec_kw=dict(width_ratios=[1.05, 1.0, 1.1], wspace=0.42))

# (a) 轮廓函数
ax = axs[0]
q = np.linspace(0, 2.6, 700)
ax.fill_between([1.0, 2.0], 0, 1.12, color=GRID, alpha=0.55, zorder=1)
ax.plot(q, f_kernel(q), color=ACCENT, lw=2.0, zorder=4)
ax.axvline(1.0, color=FAINT, lw=0.8, ls=":", zorder=2)
ax.axvline(2.0, color=FAINT, lw=0.8, ls=":", zorder=2)
clean(ax, grid=False)
ax.set_xlim(0, 2.6)
ax.set_ylim(0, 1.12)
ax.set_xlabel(r"$q=r/h$")
ax.set_ylabel(r"$W/\alpha_d$")
ax.set_xticks([0, 0.5, 1, 1.5, 2, 2.5])
ax.text(1.50, 0.13, "支撑域", color=MUTED, fontsize=8.2, ha="center")
ax.text(0.06, 0.94, "(a)", transform=ax.transAxes, fontsize=9, color=INK, va="top")

# (b) 一阶导数
ax = axs[1]
ax.plot(q, df_kernel(q), color=BLUE, lw=2.0, zorder=4)
ax.axhline(0, color=FAINT, lw=0.7, zorder=1)
ax.axvline(1.0, color=FAINT, lw=0.8, ls=":", zorder=2)
ax.axvline(2.0, color=FAINT, lw=0.8, ls=":", zorder=2)
ax.axvline(2.0 / 3.0, color=GREEN, lw=1.0, ls="--", zorder=2)
clean(ax, grid=False)
ax.set_xlim(0, 2.6)
ax.set_ylim(-1.65, 0.32)
ax.set_xlabel(r"$q=r/h$")
ax.set_ylabel(r"$dW/dq\ /\ \alpha_d$")
ax.set_xticks([0, 0.5, 1, 1.5, 2, 2.5])
ax.set_yticks([-1.5, -1.0, -0.5, 0.0])
ax.text(2.10, -0.34, "$q=2$ 处\n斜率归零", color=MUTED, fontsize=7.8, ha="left", va="top")
ax.text(2.0 / 3.0 + 0.08, -1.45, r"$q=2/3$", color=GREEN, fontsize=8.0, ha="left")
ax.text(0.06, 0.90, "(b)", transform=ax.transAxes, fontsize=9, color=INK, va="top")

# (c) 二维邻域，h = 1.2 dx，支撑圆半径 2h，共 20 个邻居
ax = axs[2]
h = 1.2
pts = []
for i in range(-3, 4):
    for j in range(-3, 4):
        if i == 0 and j == 0:
            continue
        r = np.hypot(i, j)
        if r < 2 * h:
            pts.append((i, j, r))
pts = np.array(pts)
w = (10.0 / (7 * np.pi * h ** 2)) * f_kernel(pts[:, 2] / h)
wn = w / w.max()

th = np.linspace(0, 2 * np.pi, 400)
ax.plot(2 * h * np.cos(th), 2 * h * np.sin(th), color=INK, lw=1.0, zorder=2)
ax.plot(h * np.cos(th), h * np.sin(th), color=FAINT, lw=0.8, ls="--", zorder=2)
ax.scatter(pts[:, 0], pts[:, 1], s=26 + 95 * wn, c=wn, cmap="YlOrBr",
           vmin=-0.05, vmax=1.05, edgecolor=INK, linewidth=0.5, zorder=4)
ax.scatter([0], [0], s=52, color=INK, zorder=5)
ax.set_aspect("equal")
ax.set_xlim(-2.75, 2.75)
ax.set_ylim(-2.75, 2.75)
ax.axis("off")
ax.text(0.30, 2.62, "20 个邻居，$h=1.2\\,dx$", color=INK, fontsize=8.0,
        ha="center", va="center")
ax.plot([-1.75, -1.35], [-2.55, -2.55], color=INK, lw=1.0, solid_capstyle="round")
ax.text(-1.28, -2.55, "$r=2h$", color=INK, fontsize=7.6, ha="left", va="center")
ax.plot([0.15, 0.55], [-2.55, -2.55], color=FAINT, lw=0.9, ls="--")
ax.text(0.62, -2.55, "$r=h$", color=MUTED, fontsize=7.6, ha="left", va="center")
ax.text(0.02, 0.88, "(c)", transform=ax.transAxes, fontsize=9, color=INK, va="top")

save(fig, "07", "fig07-01")


# ---------------------------------------------------------------- 图 7-2
# 一维密度估计：50 个粒子排在 [0,1]，dx=0.02，m = rho0*dx，h = 3dx。
# rho(x) = sum_j m * W(x - x_j),  W = (2/(3h)) * f(|x-xj|/h)
rho0 = 1000.0
dx = 0.02
n = 50
m = rho0 * dx
h = 3 * dx
alpha1 = 2.0 / (3.0 * h)


def rho_1d(xq, xp, mm=m, hh=h):
    xq = np.atleast_1d(np.asarray(xq, float))
    out = np.zeros_like(xq)
    for p in xp:
        out += mm * alpha1 * f_kernel(np.abs(xq - p) / hh)
    return out


rng = np.random.default_rng(7)
x_reg = (np.arange(n) + 0.5) * dx
x_jit = x_reg + 0.3 * dx * rng.uniform(-1, 1, n)

xg = np.linspace(0, 1, 600)
r_reg = rho_1d(xg, x_reg) / rho0
r_jit = rho_1d(xg, x_jit) / rho0

fig, ax = plt.subplots(figsize=(6.7, 3.25))
clean(ax, grid=True)
ax.set_xlim(-0.01, 1.01)
ax.set_ylim(0.30, 1.12)

ax.axhline(1.0, color=FAINT, lw=0.9, ls=":", zorder=1)
ax.plot(xg, r_reg, color=ACCENT, lw=1.9, zorder=4, label="均匀分布")
ax.plot(xg, r_jit, color=BLUE, lw=1.3, zorder=3, label="位置抖动 $0.3\\,dx$")

# 粒子位置
ax.plot(x_reg, np.full(n, 0.345), "|", color=ACCENT, ms=6, mew=0.9, zorder=3)
ax.plot(x_jit, np.full(n, 0.383), "|", color=BLUE, ms=6, mew=0.9, zorder=3)

ax.annotate("表面粒子邻居缺失，\n密度被系统性低估", xy=(0.035, 0.63), xytext=(0.15, 0.74),
            color=MUTED, fontsize=8.2,
            arrowprops=dict(arrowstyle="-|>", color=FAINT, lw=0.8,
                            connectionstyle="arc3,rad=0.2"))

ax.set_xlabel("位置 $x$ / m")
ax.set_ylabel(r"$\rho/\rho_0$")
ax.set_yticks([0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
ax.legend(loc="lower right", frameon=False, fontsize=8.8,
          handlelength=2.2, bbox_to_anchor=(0.94, 0.10))
ax.text(0.5, -0.255, "$\\rho_0=1000\\,\\mathrm{kg/m^3}$，$dx=0.02\\,\\mathrm{m}$，"
        "$h=3\\,dx$，$m=\\rho_0\\,dx$", color=FAINT, fontsize=7.8,
        transform=ax.transAxes, ha="center", va="top")

save(fig, "07", "fig07-02")
