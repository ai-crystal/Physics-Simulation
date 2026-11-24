import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

import numpy as np


# ---------------------------------------------------------------- 图 5-1
# 三类方程的一维解：全部来自解析解，参数写在图注里
def fig01():
    fig, axes = plt.subplots(1, 3, figsize=(6.9, 2.62),
                             gridspec_kw=dict(wspace=0.42))

    # (a) 热方程 u_t = alpha u_xx，两个模态，Dirichlet 边界
    ax = axes[0]
    x = np.linspace(0.0, 1.0, 700)
    alpha = 0.02

    def heat(t):
        return (np.exp(-alpha * np.pi**2 * t) * np.sin(np.pi * x)
                + 0.60 * np.exp(-9.0 * alpha * np.pi**2 * t) * np.sin(3.0 * np.pi * x))

    for t, c, ls, lab in [(0.0, MUTED, (0, (3, 2)), "$t=0$"),
                         (2.0, BLUE, "-", "$t=2$"),
                         (6.0, ACCENT, "-", "$t=6$")]:
        ax.plot(x, heat(t), color=c, lw=1.5, ls=ls, label=lab)
    ax.axhline(0.0, color=GRID, lw=0.8, zorder=0)
    clean(ax, grid=True)
    ax.set_xlim(0, 1.0)
    ax.set_ylim(-1.05, 2.05)
    ax.set_yticks([-1.0, -0.5, 0.0, 0.5, 1.0])
    ax.set_xticks([0.0, 0.5, 1.0])
    ax.set_xlabel("位置 $x$")
    ax.set_ylabel("温度 $u$")
    label(ax, 0.02, 1.94, "热方程", fs=8.6, color=INK, ha="left")
    ax.legend(loc="upper right", bbox_to_anchor=(1.02, 1.00), fontsize=8.0,
              handlelength=1.5, labelspacing=0.30)

    # (b) 波动方程 u_tt = c^2 u_xx，d'Alembert 解
    ax = axes[1]
    xx = np.linspace(0.0, 1.0, 900)

    def bump(xs, cx=0.5, s=0.042):
        return np.exp(-(xs - cx)**2 / (2.0 * s * s))

    cw = 0.35
    for t, c, ls, lab in [(0.0, MUTED, (0, (3, 2)), "$t=0$"),
                         (0.6, BLUE, "-", "$t=0.6$"),
                         (1.2, ACCENT, "-", "$t=1.2$")]:
        u = 0.5 * (bump(xx - cw * t) + bump(xx + cw * t))
        ax.plot(xx, u, color=c, lw=1.5, ls=ls, label=lab)
    ax.axhline(0.0, color=GRID, lw=0.8, zorder=0)
    clean(ax, grid=True)
    ax.set_xlim(0, 1.0)
    ax.set_ylim(-0.12, 2.05)
    ax.set_yticks([0.0, 0.5, 1.0])
    ax.set_xticks([0.0, 0.5, 1.0])
    ax.set_xlabel("位置 $x$")
    ax.set_ylabel("位移 $u$")
    label(ax, 0.02, 1.94, "波动方程", fs=8.6, color=INK, ha="left")
    ax.legend(loc="upper left", bbox_to_anchor=(-0.02, 0.80), fontsize=8.0,
              handlelength=1.5, labelspacing=0.30)
    label(ax, 0.98, 1.76, "鼓包一分为二，向两侧跑", fs=8.0, color=ACCENT, ha="right")

    # (c) 泊松方程 -u'' = 1，只换右端边界值
    ax = axes[2]
    xs = np.linspace(0.0, 1.0, 300)
    u0 = 0.5 * xs * (1.0 - xs)
    u1 = 0.5 * xs * (1.0 - xs) + 0.40 * xs
    ax.plot(xs, u0, color=BLUE, lw=1.5, label="右端 0")
    ax.plot(xs, u1, color=ACCENT, lw=1.5, ls="--", label="右端 0.4")
    clean(ax, grid=True)
    ax.set_xlim(0, 1.0)
    ax.set_ylim(-0.06, 1.05)
    ax.set_yticks([0.0, 0.2, 0.4])
    ax.set_xticks([0.0, 0.5, 1.0])
    ax.set_xlabel("位置 $x$")
    ax.set_ylabel("位移 $u$")
    label(ax, 0.02, 0.97, "泊松方程", fs=8.6, color=INK, ha="left")
    label(ax, 0.05, 0.72, "只改右端一个边界值", fs=8.0, color=ACCENT, ha="left")
    label(ax, 0.05, 0.61, "整条曲线都跟着变", fs=8.0, color=ACCENT, ha="left")
    ax.legend(loc="upper right", bbox_to_anchor=(1.03, 0.95), fontsize=8.0,
              handlelength=1.4, labelspacing=0.30)

    save(fig, "05", "fig05-01")


# ---------------------------------------------------------------- 图 5-2
# 三种对流格式的 von Neumann 放大因子与数值相速度，sigma = 0.6
def fig02():
    fig, axes = plt.subplots(1, 2, figsize=(6.6, 2.85),
                             gridspec_kw=dict(wspace=0.40, width_ratios=[1.0, 1.0]))

    s = 0.60
    th = np.linspace(1e-4, np.pi, 1400)
    sn = np.sin(th)
    cs = np.cos(th)

    g_c = 1.0 - 1j * s * sn
    g_u = 1.0 - s * (1.0 - cs) - 1j * s * sn
    g_l = 1.0 - s**2 * (1.0 - cs) - 1j * s * sn

    ax = axes[0]
    ax.plot(th / np.pi, np.abs(g_c), color=ACCENT, lw=1.7)
    ax.plot(th / np.pi, np.abs(g_u), color=BLUE, lw=1.7)
    ax.plot(th / np.pi, np.abs(g_l), color=GREEN, lw=1.7, ls=(0, (5, 2)))
    ax.axhline(1.0, color=MUTED, lw=0.9, ls=":")
    clean(ax, grid=True)
    ax.set_xlim(0, 1.0)
    ax.set_ylim(0.0, 1.30)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_xlabel(r"波长参数 $\theta=k\Delta x$ （以 $\pi$ 为单位）")
    ax.set_ylabel("每步放大因子 $|g|$")
    label(ax, 0.30, 1.20, "中心差分：大于 1，必炸", fs=8.0, color=ACCENT, ha="left")
    label(ax, 0.60, 0.84, "Lax-Wendroff", fs=8.0, color=GREEN, ha="left")
    label(ax, 0.44, 0.50, "迎风", fs=8.0, color=BLUE, ha="left")
    label(ax, 0.03, 1.03, "$|g|=1$", fs=8.0, color=MUTED, ha="left", va="bottom")

    ax = axes[1]
    nstep = 100
    ax.semilogy(th / np.pi, np.abs(g_c)**nstep, color=ACCENT, lw=1.7, label="中心差分")
    ax.semilogy(th / np.pi, np.abs(g_u)**nstep, color=BLUE, lw=1.7, label="迎风")
    ax.semilogy(th / np.pi, np.abs(g_l)**nstep, color=GREEN, lw=1.7, ls=(0, (5, 2)),
                label="Lax-Wendroff")
    ax.axhline(1.0, color=MUTED, lw=0.9, ls=":")
    clean(ax, grid=True)
    ax.set_xlim(0, 1.0)
    ax.set_ylim(1e-26, 1e10)
    ax.set_yticks([1e-20, 1e-10, 1.0])
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_xlabel(r"波长参数 $\theta=k\Delta x$ （以 $\pi$ 为单位）")
    ax.set_ylabel("100 步后的剩余振幅")
    ax.legend(loc="lower left", bbox_to_anchor=(0.01, 0.015), fontsize=8.0,
              handlelength=1.5, labelspacing=0.28)

    save(fig, "05", "fig05-02")


# ---------------------------------------------------------------- 图 5-3
# MAC 网格（示意）+ 共位网格的棋盘压力（恒等式，非实验数据）
def fig03():
    fig = plt.figure(figsize=(6.8, 3.40))
    ax = fig.add_axes([0.02, 0.02, 0.55, 0.92])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    dx, dy = 0.125, 0.145
    x0, y0 = 0.245, 0.305
    nx, ny = 4, 3
    grid(ax, x0, y0, nx * dx, ny * dy, nx, ny, color="#C9CDD4", lw=0.9)

    ci, cj = 1, 1
    ax.add_patch(Rectangle((x0 + ci * dx, y0 + cj * dy), dx, dy,
                           facecolor="#FDF2E9", edgecolor=ACCENT, lw=1.2, zorder=1))

    for i in range(nx):
        for j in range(ny):
            cx = x0 + (i + 0.5) * dx
            cy = y0 + (j + 0.5) * dy
            ax.plot([cx], [cy], "o", ms=3.8, mfc=INK, mec="white", mew=0.7, zorder=4)

    for i in range(nx + 1):
        for j in range(ny):
            fx = x0 + i * dx
            fy = y0 + (j + 0.5) * dy
            arrow(ax, (fx - 0.030, fy), (fx + 0.030, fy), color=BLUE, lw=1.1, ms=7, z=5,
                  shrinkA=0, shrinkB=0)

    for i in range(nx):
        for j in range(ny + 1):
            fx = x0 + (i + 0.5) * dx
            fy = y0 + j * dy
            arrow(ax, (fx, fy - 0.034), (fx, fy + 0.034), color=GREEN, lw=1.1, ms=7, z=5,
                  shrinkA=0, shrinkB=0)

    cols = ["$i-1$", "$i$", "$i+1$", "$i+2$"]
    rows = ["$j-1$", "$j$", "$j+1$"]
    for i in range(nx):
        label(ax, x0 + (i + 0.5) * dx, y0 - 0.070, cols[i], fs=8.0, color=MUTED)
    for j in range(ny):
        label(ax, x0 - 0.048, y0 + (j + 0.5) * dy, rows[j], fs=8.0, color=MUTED, ha="right")

    yy = 0.945
    ax.plot([0.02], [yy], "o", ms=3.8, mfc=INK, mec="white", mew=0.7)
    label(ax, 0.063, yy, "压力、温度等标量在格心", fs=8.2, ha="left")
    arrow(ax, (0.02, yy - 0.072), (0.052, yy - 0.072), color=BLUE, lw=1.1, ms=7,
          shrinkA=0, shrinkB=0)
    label(ax, 0.063, yy - 0.072, "水平速度在竖直面", fs=8.2, ha="left")
    arrow(ax, (0.036, yy - 0.148), (0.036, yy - 0.096), color=GREEN, lw=1.1, ms=7,
          shrinkA=0, shrinkB=0)
    label(ax, 0.063, yy - 0.122, "竖直速度在水平面", fs=8.2, ha="left")

    label(ax, 0.02, 0.180, "散度取左右两个水平速度之差，", fs=8.2, color=MUTED, ha="left")
    label(ax, 0.02, 0.113, "梯度取相邻两个格心压力之差，", fs=8.2, color=MUTED, ha="left")
    label(ax, 0.02, 0.046, "两者都只跨半格，不会互相错过。", fs=8.2, color=MUTED, ha="left")

    # 右：共位网格上的棋盘压力与它的中心差分梯度
    ax2 = fig.add_axes([0.665, 0.10, 0.315, 0.80])
    n = 8
    idx = np.arange(n)
    p = (-1.0) ** idx
    ax2.bar(idx, p, width=0.60, color=[ACCENT if v > 0 else BLUE for v in p],
            alpha=0.85, edgecolor="white", lw=0.6)
    ax2.axhline(0, color=MUTED, lw=0.8)
    yg = -1.62
    ax2.axhline(yg, color=GRID, lw=0.8)
    ax2.plot(idx[1:-1], np.full(n - 2, yg), "o", ms=4.2, mfc="white", mec=MUTED, mew=0.9,
             zorder=4)
    ax2.set_xlim(-0.65, n - 0.35)
    ax2.set_ylim(-2.05, 1.45)
    ax2.set_yticks([-1, 0, 1])
    ax2.set_xticks(idx)
    ax2.set_xticklabels([str(i) for i in idx], fontsize=8.0)
    clean(ax2, grid=False)
    ax2.tick_params(length=2.5)
    ax2.set_xlabel("格心编号 $i$", fontsize=8.6, labelpad=2)
    ax2.set_ylabel("$p_i$", fontsize=8.6, labelpad=2)
    ax2.text(-0.55, 1.26, "棋盘压力场", fontsize=8.4, color=INK)
    ax2.text(-0.55, yg + 0.18, "中心差分的梯度：处处为 0", fontsize=8.2, color=ACCENT)

    save(fig, "05", "fig05-03")


fig01()
fig02()
fig03()
