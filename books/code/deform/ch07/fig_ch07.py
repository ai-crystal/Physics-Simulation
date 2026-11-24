import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

import numpy as np


# ---------------------------------------------------------------- 图 7-1
def fig01():
    fig = plt.figure(figsize=(6.9, 2.75))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.02, 1.10, 0.96], wspace=0.26)
    axa = fig.add_subplot(gs[0]); axa.set_xlim(0, 1); axa.set_ylim(0, 1); axa.axis("off")
    axb = fig.add_subplot(gs[1]); axb.set_xlim(0, 1); axb.set_ylim(0, 1); axb.axis("off")

    # ---- 左：二面角（垂直于共享边的剖面）
    P = np.array([0.30, 0.22])
    ang = np.deg2rad(56)
    L1, L2 = 0.66, 0.52
    e1 = P + L1 * np.array([1.0, 0.0])
    d2 = np.array([np.cos(ang), np.sin(ang)])
    e2 = P + L2 * d2
    axa.add_patch(Wedge(P, 0.46, 0, 56, facecolor="#FDF2E9", edgecolor="none",
                        alpha=0.55, zorder=1))
    axa.plot([P[0], e1[0]], [P[1], e1[1]], color=BLUE, lw=3.0, zorder=3,
             solid_capstyle="round")
    axa.plot([P[0], e2[0]], [P[1], e2[1]], color=ACCENT, lw=3.0, zorder=3,
             solid_capstyle="round")
    axa.scatter([P[0]], [P[1]], s=24, color=INK, zorder=5)
    axa.add_patch(Arc(P, 0.36, 0.36, theta1=0, theta2=56, color=MUTED, lw=0.9, zorder=4))
    label(axa, 0.505, 0.325, r"$\theta$", fs=10.5, color=INK, ha="left")
    # 法向
    arrow(axa, (0.79, 0.225), (0.79, 0.455), color=MUTED, lw=1.0, ms=7)
    label(axa, 0.79, 0.495, r"$\mathbf{n}_1$", fs=9.2, color=MUTED)
    m2 = P + 0.52 * L2 * d2
    nrm = np.array([-np.sin(ang), np.cos(ang)])
    arrow(axa, m2, m2 + 0.17 * nrm, color=MUTED, lw=1.0, ms=7)
    label(axa, m2[0] + 0.17 * nrm[0] - 0.03, m2[1] + 0.17 * nrm[1] + 0.02,
          r"$\mathbf{n}_2$", fs=9.2, color=MUTED, ha="right")
    label(axa, 0.84, 0.145, r"$T_1$", fs=9.0, color=BLUE)
    label(axa, 0.575, 0.545, r"$T_2$", fs=9.0, color=ACCENT, ha="left")
    label(axa, 0.30, 0.095, "共享边 $e$", fs=8.6, color=MUTED)

    # ---- 中：同一条弧的两种离散
    s = np.linspace(0, 1, 400)
    cx = 0.09 + 0.82 * s
    cy = 0.24 + 0.34 * np.sin(np.pi * s)
    axb.plot(cx, cy, color=GRID, lw=4.2, zorder=1, solid_capstyle="round")
    for n, col, ms in ((4, BLUE, 5.0), (14, ACCENT, 3.0)):
        sc = np.linspace(0, 1, n + 1)
        axb.plot(0.09 + 0.82 * sc, 0.24 + 0.34 * np.sin(np.pi * sc), color=col,
                 lw=1.4, marker="o", ms=ms, markerfacecolor="white",
                 markeredgewidth=0.9, zorder=3)
    label(axb, 0.50, 0.92, r"$k_b=B/l$", fs=10.2, color=INK)
    legend_row(axb, [(BLUE, r"粗网格，$l$ 大"), (ACCENT, r"细网格，$l$ 小")],
               x=0.06, y=0.115, dy=0.085, fs=8.6)

    # ---- 右：铰链能量
    axc = fig.add_subplot(gs[2])
    th = np.linspace(0, 1.15, 300)
    th0 = 0.48
    for k, col, lab in ((1.1, BLUE, r"$k_b$ 小"), (3.2, ACCENT, r"$k_b$ 大")):
        axc.plot(th, 0.5 * k * (th - th0) ** 2, color=col, lw=1.6, label=lab)
    axc.axvline(th0, color=FAINT, lw=0.8, ls=(0, (3, 2)))
    axc.set_xlim(0, 1.15)
    axc.set_ylim(-0.02, 0.72)
    axc.set_xlabel(r"二面角 $\theta$  (rad)", labelpad=2.0)
    axc.set_ylabel(r"弯曲能量 $E_b$", labelpad=2.0)
    axc.set_yticks([])
    axc.set_xticks([0, 0.5, 1.0])
    clean(axc)
    axc.legend(loc="upper center", fontsize=8.4, handlelength=1.6,
               borderaxespad=0.3)
    axc.annotate(r"$\bar\theta$", xy=(th0, -0.02), xytext=(th0 + 0.02, 0.055),
                 fontsize=9.6, color=MUTED)

    save(fig, "07", "fig07-01")


# ---------------------------------------------------------------- 图 7-2
def fig02():
    fig, ax = plt.subplots(figsize=(6.5, 3.55))
    B = np.logspace(-7, -2, 400)
    T = 1.2          # N/m，压缩线力
    K = 2.0e6        # N/m^3，支撑刚度
    lam_t = 2 * np.pi * np.sqrt(B / T)
    lam_k = 2 * np.pi * (B / K) ** 0.25

    ax.loglog(B, lam_t * 100, color=ACCENT, lw=1.9,
              label="压缩膜：" + r"$\lambda=2\pi\sqrt{B/T}$")
    ax.loglog(B, lam_k * 100, color=BLUE, lw=1.9, ls=(0, (5, 2)),
              label="软支撑：" + r"$\lambda=2\pi(B/K)^{1/4}$")

    # 薄棉布的工作点
    Bc = 1.2e-5
    yc1 = 2 * np.pi * np.sqrt(Bc / T) * 100
    yc2 = 2 * np.pi * (Bc / K) ** 0.25 * 100
    ax.scatter([Bc], [yc1], s=36, color=INK, zorder=6)
    ax.scatter([Bc], [yc2], s=30, color=INK, zorder=6, facecolor="white", linewidth=1.0)
    ax.plot([Bc, Bc], [yc2, yc1], color=FAINT, lw=0.8, ls=(0, (2, 2)), zorder=2)
    ax.annotate("薄棉布 $B=1.2\\times10^{-5}$ N·m\n实线 2.0 cm　虚线 1.0 cm",
                xy=(1.24e-5, 0.97), xytext=(1.25e-5, 0.40), fontsize=8.0, color=INK,
                linespacing=1.7, ha="left", va="bottom",
                arrowprops=dict(arrowstyle="-", color=FAINT, lw=0.7,
                                shrinkA=2, shrinkB=3,
                                connectionstyle="arc3,rad=0.0"))

    # 斜率标注（放在线上方，避开曲线）
    ax.annotate("斜率 1/2", xy=(2.1e-6, 1.95), fontsize=8.4,
                color=ACCENT, rotation=30, ha="center", va="center")
    ax.annotate("斜率 1/4", xy=(1.25e-3, 1.62), fontsize=8.4,
                color=BLUE, rotation=15, ha="center", va="center")

    ax.set_xlim(8e-8, 1.4e-2)
    ax.set_ylim(0.35, 90)
    ax.set_xlabel("弯曲刚度 $B$  (N·m)")
    ax.set_ylabel("褶皱波长 $\\lambda$  (cm)")
    clean(ax, grid=True)
    ax.legend(loc="upper left", fontsize=8.2, handlelength=2.4, borderaxespad=0.25)
    save(fig, "07", "fig07-02")


fig01()
fig02()
