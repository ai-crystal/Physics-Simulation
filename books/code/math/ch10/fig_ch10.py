# -*- coding: utf-8 -*-
"""第 10 章插图：角亏曲率、余切权重、离散杆的转角与曲率。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Arc
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


# ---------------------------------------------------------------- 图 10-1
def heightfield(n=64, L=1.1, h=0.25, s=0.55):
    """高斯凸包曲面 z = h*exp(-r^2/s^2)，返回格点与三角形索引。"""
    x = np.linspace(-L, L, n + 1)
    X, Y = np.meshgrid(x, x)
    Z = h * np.exp(-(X ** 2 + Y ** 2) / s ** 2)
    pts = np.column_stack([X.ravel(), Y.ravel(), Z.ravel()])
    tris = []
    for j in range(n):
        for i in range(n):
            a = j * (n + 1) + i
            tris += [(a, a + 1, a + n + 2), (a, a + n + 2, a + n + 1)]
    return pts, np.array(tris)


def analytic_K(X, Y, h=0.25, s=0.55):
    """z = h exp(-r^2/s^2) 的高斯曲率 K = (rt - s^2)/(1+p^2+q^2)^2。"""
    e = np.exp(-(X ** 2 + Y ** 2) / s ** 2)
    p = h * e * (-2 * X / s ** 2)
    q = h * e * (-2 * Y / s ** 2)
    r = h * e * ((4 * X ** 2 / s ** 4) - 2 / s ** 2)
    t = h * e * ((4 * Y ** 2 / s ** 4) - 2 / s ** 2)
    sc = h * e * (4 * X * Y / s ** 4)
    return (r * t - sc ** 2) / (1 + p ** 2 + q ** 2) ** 2


def fig_10_1():
    pts, tris = heightfield()
    n = len(pts)
    A, B, C = pts[tris[:, 0]], pts[tris[:, 1]], pts[tris[:, 2]]

    def cosang(v1, v2):
        return np.sum(v1 * v2, 1) / (np.linalg.norm(v1, axis=1) * np.linalg.norm(v2, axis=1))

    ang = np.array([
        np.arccos(np.clip(cosang(B - A, C - A), -1, 1)),
        np.arccos(np.clip(cosang(C - B, A - B), -1, 1)),
        np.arccos(np.clip(cosang(A - C, B - C), -1, 1)),
    ]).T
    area = 0.5 * np.linalg.norm(np.cross(B - A, C - A), axis=1)

    angsum = np.zeros(n); are = np.zeros(n); cnt = np.zeros(n)
    for k in range(3):
        np.add.at(angsum, tris[:, k], ang[:, k])
        np.add.at(are, tris[:, k], area / 3.0)
        np.add.at(cnt, tris[:, k], 1)
    inner = cnt == 6                               # 内部顶点：周围 6 个三角形
    deficit = 2 * np.pi - angsum
    Kd = np.where(inner, deficit / np.maximum(are, 1e-12), np.nan)
    Kd_col = np.where(inner, deficit / np.maximum(are, 1e-12), 0.0)

    fig = plt.figure(figsize=(6.8, 3.05))
    ax = fig.add_subplot(1, 2, 1, projection="3d")
    kmax = 2.6
    fc = np.mean(np.stack([Kd_col[tris[:, 0]], Kd_col[tris[:, 1]], Kd_col[tris[:, 2]]]), axis=0)
    cmap = plt.get_cmap("RdBu_r")
    norm = plt.Normalize(-kmax, kmax)
    tri_verts = pts[tris].copy()
    tri_verts[:, :, 2] *= 3.6                      # 竖直方向放大，便于看出凸起
    pc = Poly3DCollection(tri_verts, facecolors=cmap(norm(fc)), linewidth=0.18,
                          edgecolor=(0.25, 0.25, 0.25, 0.28))
    ax.add_collection3d(pc)
    ax.set_xlim(-1.1, 1.1); ax.set_ylim(-1.1, 1.1); ax.set_zlim(0, 1.0)
    ax.set_box_aspect((1, 1, 0.55), zoom=1.32)
    ax.view_init(elev=34, azim=-62)
    ax.set_axis_off()
    ax.text2D(0.02, 0.95, "竖直方向放大 3.6 倍", transform=ax.transAxes,
              fontsize=8.2, color=MUTED)

    ax = fig.add_subplot(1, 2, 2)
    xs = pts[inner, 0]; ys = pts[inner, 1]
    sel = np.abs(ys) < 1e-9
    order = np.argsort(xs[sel])
    Kd_slice = Kd[inner][sel][order]
    xs_slice = xs[sel][order]
    xl = np.linspace(-0.95, 0.95, 400)
    ax.plot(xl, analytic_K(xl, 0.0), color=MUTED, lw=1.1, label="解析曲率 $K$")
    ax.scatter(xs_slice, Kd_slice, s=13, color=ACCENT, zorder=3, lw=0,
               label="角亏 / 面积")
    ax.axhline(0, color="#E5E7EB", lw=0.8, zorder=0)
    ax.set_xlim(-1.12, 1.12)
    ax.set_ylim(-1.6, 3.2)
    ax.set_xlabel("$x$", fontsize=9, labelpad=2)
    ax.set_ylabel("曲率", fontsize=9, labelpad=2)
    clean(ax, spines=("left", "bottom"))
    ax.legend(loc="lower center", fontsize=8.2, ncol=2, handletextpad=0.5,
              columnspacing=1.2, borderpad=0.2)
    ax.text(0.02, 0.97, "网格 64×64，$h=0.25$，$s=0.55$", transform=ax.transAxes,
            fontsize=8.2, color=MUTED, va="top")
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.05, wspace=0.06)
    save(fig, "10", "fig10-01")
    print("interior deficit sum", deficit[inner].sum())


# ---------------------------------------------------------------- 图 10-2
def angle_arc(ax, P, Q, R, r=0.09, color=INK, lw=0.9, fs=8.4, txt=None, tr=0.16):
    """在顶点 P 处，从 PQ 转到 PR 画内角弧并标注。"""
    a1 = np.degrees(np.arctan2(Q[1] - P[1], Q[0] - P[0]))
    a2 = np.degrees(np.arctan2(R[1] - P[1], R[0] - P[0]))
    d = (a2 - a1) % 360.0
    if d > 180.0:
        d -= 360.0
    t1, t2 = (a1, a1 + d) if d >= 0 else (a1 + d, a1)
    ax.add_patch(Arc(P, 2 * r, 2 * r, theta1=t1, theta2=t2, color=color, lw=lw, zorder=5))
    mid = np.radians(a1 + d / 2)
    if txt:
        ax.text(P[0] + tr * np.cos(mid), P[1] + tr * np.sin(mid), txt,
                fontsize=fs, color=color, ha="center", va="center", zorder=6)


def fig_10_2():
    fig, axs = plt.subplots(1, 2, figsize=(6.8, 3.0))

    # 左：共享边 ij 的两个三角形
    ax = axs[0]
    ax.set_aspect("equal")
    i = np.array([-0.30, 0.0]); j = np.array([0.54, 0.0])
    k = np.array([0.06, 0.60]); l = np.array([0.26, -0.58])
    ax.add_patch(Polygon([i, j, k], closed=True, facecolor="#EFF4FF", edgecolor=INK, lw=1.0))
    ax.add_patch(Polygon([i, j, l], closed=True, facecolor="#FDF6EC", edgecolor=INK, lw=1.0))
    ax.plot([i[0], j[0]], [i[1], j[1]], color=ACCENT, lw=2.4, zorder=4)
    for P, nm, off in ((i, "$i$", (-0.075, -0.02)), (j, "$j$", (0.075, -0.02)),
                       (k, "$k$", (0.0, 0.075)), (l, "$l$", (0.0, -0.088))):
        ax.plot([P[0]], [P[1]], "o", ms=3.6, color=INK, zorder=6)
        ax.text(P[0] + off[0], P[1] + off[1], nm, fontsize=9.2, color=INK,
                ha="center", va="center", zorder=6)
    angle_arc(ax, k, i, j, r=0.20, txt=r"$\alpha$", tr=0.30)
    angle_arc(ax, l, i, j, r=0.20, txt=r"$\beta$", tr=0.31)
    ax.text(-1.42, 0.74, "共享边 $ij$ 与它的两个对角", fontsize=9.0, color=INK, va="top")
    ax.text(-1.42, 0.55, r"$w_{ij}=\frac{1}{2}(\cot\alpha+\cot\beta)$", fontsize=9.4,
            color=INK, va="top")
    ax.text(-1.42, 0.22, "权重的正负取决于" + chr(10) + "两个对角是否为钝角",
            fontsize=8.2, color=MUTED, va="top", linespacing=1.7)
    ax.set_xlim(-1.46, 0.78); ax.set_ylim(-0.72, 0.78)
    ax.axis("off")

    # 右：钝角三角形
    ax = axs[1]
    ax.set_aspect("equal")
    A = np.array([-0.36, -0.28]); B = np.array([0.58, -0.28]); C = np.array([-0.66, 0.24])
    ax.add_patch(Polygon([A, B, C], closed=True, facecolor="#F5F3FF", edgecolor=INK, lw=1.1))
    ax.plot([B[0], C[0]], [B[1], C[1]], color=ACCENT, lw=2.2, zorder=4)
    for P, nm, off in ((A, "$i$", (0.07, -0.10)), (B, "$j$", (0.08, -0.07)),
                       (C, "$m$", (0.0, 0.09))):
        ax.plot([P[0]], [P[1]], "o", ms=3.6, color=INK, zorder=6)
        ax.text(P[0] + off[0], P[1] + off[1], nm, fontsize=9.2, color=INK,
                ha="center", va="center", zorder=6)
    angle_arc(ax, A, B, C, r=0.17, color=ACCENT, txt=r"$\alpha$", tr=0.30)
    ax.text(-1.42, 0.74, "钝角时 $\\cot\\alpha$ 取负值", fontsize=9.0, color=INK, va="top")
    ax.text(-1.42, 0.56, "对面那条边 $jm$ 的权重" + chr(10) + "可能变成负数",
            fontsize=8.4, color=MUTED, va="top", linespacing=1.7)
    ax.text(-1.42, -0.30, r"$\cot\alpha=\cos\alpha/\sin\alpha$", fontsize=9.2,
            color=MUTED, va="top")
    ax.set_xlim(-1.46, 0.78); ax.set_ylim(-0.72, 0.78)
    ax.axis("off")

    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01, wspace=0.04)
    save(fig, "10", "fig10-02")


# ---------------------------------------------------------------- 图 10-3
def fig_10_3():
    R = 1.0
    N = 6
    phi = np.linspace(0, np.pi, N + 1)
    P = np.column_stack([R * np.cos(phi), R * np.sin(phi)])
    dphi = phi[1] - phi[0]
    chord = 2 * R * np.sin(dphi / 2)
    kappa_d = dphi / chord

    fig, ax = plt.subplots(figsize=(6.4, 3.0))
    ax.set_aspect("equal")
    t = np.linspace(0, np.pi, 240)
    ax.plot(R * np.cos(t), R * np.sin(t), color="#E5E7EB", lw=3.6, zorder=1)
    ax.plot(P[:, 0], P[:, 1], color=INK, lw=1.4, zorder=3, marker="o", ms=4.6,
            markerfacecolor="white", markeredgecolor=INK, markeredgewidth=1.0)

    q = N // 2                                    # 顶点 (0,1)
    tg = np.array([-1.0, 0.0])
    nr = np.array([0.0, 1.0])
    ax.plot([P[q, 0] - 0.26 * tg[0], P[q, 0] + 0.26 * tg[0]],
            [P[q, 1] - 0.26 * tg[1], P[q, 1] + 0.26 * tg[1]], color=FAINT, lw=0.9, ls=":")
    ax.plot([P[q, 0], P[q, 0] - 0.44 * nr[0]], [P[q, 1], P[q, 1] - 0.44 * nr[1]],
            color=PURPLE, lw=1.0, zorder=4)
    ax.annotate("", xy=(P[q, 0] - 0.44 * nr[0], P[q, 1] - 0.44 * nr[1]),
                xytext=(P[q, 0] - 0.24 * nr[0], P[q, 1] - 0.24 * nr[1]),
                arrowprops=dict(arrowstyle="-|>", color=PURPLE, lw=1.0, shrinkA=0, shrinkB=0))
    ax.text(0.06, 0.66, "曲率方向", fontsize=8.4, color=PURPLE, va="center", ha="left")

    a1 = np.degrees(np.arctan2(P[q, 1] - P[q - 1, 1], P[q, 0] - P[q - 1, 0]))
    a2 = np.degrees(np.arctan2(P[q + 1, 1] - P[q, 1], P[q + 1, 0] - P[q, 0]))
    d = (a2 - a1) % 360.0
    if d > 180.0:
        d -= 360.0
    t1, t2 = (a1, a1 + d) if d >= 0 else (a1 + d, a1)
    ax.add_patch(Arc(P[q], 0.64, 0.64, theta1=t1, theta2=t2, color=ACCENT, lw=1.4, zorder=6))
    mid = np.radians(a1 + d / 2)
    ax.text(P[q, 0] + 0.44 * np.cos(mid), P[q, 1] + 0.44 * np.sin(mid),
            r"$\theta_i$", fontsize=9.4, color=ACCENT, ha="center", va="center")

    m0 = 0.5 * (P[q + 1] + P[q + 2])
    ax.annotate("", xy=P[q + 2], xytext=P[q + 1],
                arrowprops=dict(arrowstyle="<|-|>", color=BLUE, lw=0.9, shrinkA=3, shrinkB=3))
    ax.text(m0[0] + 0.07, m0[1] - 0.07, "$l$", fontsize=9.2, color=BLUE, ha="center")

    ax.text(0.62, 1.04, "$R=1$，六段等长弦", fontsize=8.8, color=MUTED, va="top")
    ax.text(0.0, -0.14, "弦长 $l$，转角 $\\theta_i$，离散曲率 $\\kappa_i=\\theta_i/l$",
            fontsize=9.2, color=INK, va="center", ha="center")
    ax.text(0.0, -0.28, "本图：$\\theta_i=%.4f$，$l=%.4f$，$\\kappa_i=%.4f$，解析值 $1/R=1$"
            % (dphi, chord, kappa_d), fontsize=8.6, color=MUTED, va="center", ha="center")
    ax.set_xlim(-1.45, 1.45); ax.set_ylim(-0.36, 1.06)
    ax.axis("off")
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    save(fig, "10", "fig10-03")
    print("theta", round(dphi, 4), "l", round(chord, 4), "kappa_d", round(kappa_d, 4))


if __name__ == "__main__":
    fig_10_1()
    fig_10_2()
    fig_10_3()
