# -*- coding: utf-8 -*-
"""第 9 章插图：线性形函数、高斯积分点、组装后的稀疏结构。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from figstyle import *

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon


# ---------------------------------------------------------------- 图 9-1
def ref_tri_lattice(n=20):
    """参考三角形上的均匀格点：返回 (u, v) 坐标与三角形连接。"""
    uv, idx = [], {}
    for j in range(n + 1):
        for i in range(n + 1 - j):
            idx[(i, j)] = len(uv)
            uv.append((i / n, j / n))
    tris = []
    for j in range(n + 1):
        for i in range(n + 1 - j):
            if i + j < n:
                tris.append((idx[(i, j)], idx[(i + 1, j)], idx[(i, j + 1)]))
            if i + j < n - 1:
                tris.append((idx[(i + 1, j)], idx[(i + 1, j + 1)], idx[(i, j + 1)]))
    return np.array(uv), np.array(tris)


def fig_9_1():
    uv, T = ref_tri_lattice(20)
    u, v = uv[:, 0], uv[:, 1]
    lam = [1.0 - u - v, u, v]
    X, Y = u, v                                   # 参考三角形 V1=(0,0) V2=(1,0) V3=(0,1)
    base = np.array([(0, 0), (1, 0), (0, 1), (0, 0)])
    tex = [r"$N_1 = 1-x-y$", r"$N_2 = x$", r"$N_3 = y$"]
    cols = [ACCENT, BLUE, GREEN]
    cmaps = ["OrRd", "Blues", "Greens"]
    AZ = [225, 180, 270]                          # 每张图都顺着该曲面自身的法向看

    fig = plt.figure(figsize=(6.8, 2.62))
    for k in range(3):
        ax = fig.add_subplot(1, 3, k + 1, projection="3d")
        ax.plot_trisurf(X, Y, lam[k], triangles=T, cmap=cmaps[k],
                        vmin=0.0, vmax=1.0, linewidth=0.3, antialiased=True,
                        shade=False, edgecolor=(1, 1, 1, 0.45))
        ax.plot(base[:, 0], base[:, 1], np.zeros(len(base)), color=INK, lw=0.9,
                ls=(0, (3, 2)))
        for bx, by in base[:3]:
            ax.plot([bx], [by], [0], marker="o", ms=3.4, color=INK)
        for (vx, vy), nm, (ox, oy) in zip(base[:3], ("$V_1$", "$V_2$", "$V_3$"),
                                         ((-0.10, -0.13), (0.13, -0.12), (-0.12, 0.10))):
            ax.text(vx + ox, vy + oy, 0.0, nm, fontsize=8.6, color=MUTED,
                    ha="center", va="center")
        ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.set_zlim(0, 1)
        ax.set_box_aspect((1, 1, 1.55))
        ax.view_init(elev=22, azim=AZ[k])
        ax.set_axis_off()
        ax.text2D(0.03, 0.95, tex[k], transform=ax.transAxes, fontsize=9.2,
                  color=cols[k], va="top", ha="left")
    fig.subplots_adjust(left=0.0, right=1.0, top=1.0, bottom=0.0, wspace=0.0)
    save(fig, "09", "fig09-01")


# ---------------------------------------------------------------- 图 9-2
def fig_9_2():
    fig, axs = plt.subplots(1, 2, figsize=(6.8, 3.0))

    # 左：三角形
    ax = axs[0]
    ax.set_aspect("equal")
    tri = np.array([(0, 0), (1, 0), (0, 1)])
    ax.add_patch(Polygon(tri, closed=True, facecolor="#FDF6EC", edgecolor=INK, lw=1.1, zorder=1))
    p1, p2, p3 = (1 / 6, 1 / 6), (2 / 3, 1 / 6), (1 / 6, 2 / 3)
    ax.scatter([p1[0], p2[0], p3[0]], [p1[1], p2[1], p3[1]], s=42, color=BLUE,
               zorder=4, edgecolor="white", lw=0.8)
    ax.scatter([1 / 3], [1 / 3], s=60, marker="D", color=ACCENT, zorder=4,
               edgecolor="white", lw=0.8)

    def call(p, t, tx, ty, col=INK, ha="left"):
        ax.annotate(t, xy=p, xytext=(tx, ty), fontsize=8.3, color=col, ha=ha,
                    va="center", arrowprops=dict(arrowstyle="-", color=FAINT, lw=0.7,
                                                 shrinkA=1, shrinkB=6))

    call(p3, "(1/6, 2/3)", -0.09, 0.74, ha="right")
    ax.text(p1[0], -0.11, "(1/6, 1/6)", fontsize=8.3, color=INK, ha="center", va="center")
    ax.text(p2[0], -0.11, "(2/3, 1/6)", fontsize=8.3, color=INK, ha="center", va="center")
    call((1 / 3, 1 / 3), "重心 (1/3, 1/3)", 1.04, 0.44, col=ACCENT)
    ax.text(0.0, 1.58, "三角形", fontsize=9.2, color=INK, va="top")
    ax.text(0.0, 1.47, "3 点：权重均为 1/6" + chr(10) + "1 点：重心，权重 1/2",
            fontsize=8.2, color=MUTED, va="top", linespacing=1.7)
    ax.set_xlim(-0.62, 1.72); ax.set_ylim(-0.24, 1.62)
    ax.axis("off")

    # 右：四边形
    ax = axs[1]
    ax.set_aspect("equal")
    g = 1 / np.sqrt(3)
    sq = np.array([(-1, -1), (1, -1), (1, 1), (-1, 1), (-1, -1)])
    ax.plot(sq[:, 0], sq[:, 1], color=INK, lw=1.1, zorder=2)
    for gx in (-g, g):
        for gy in (-g, g):
            ax.scatter([gx], [gy], s=42, color=BLUE, zorder=4, edgecolor="white", lw=0.8)
    ax.plot([g, g], [-1.0, g], color=FAINT, lw=0.7, ls=":", zorder=1)
    ax.plot([-1.0, g], [g, g], color=FAINT, lw=0.7, ls=":", zorder=1)
    ax.text(g, -1.13, "0.5774", fontsize=8.3, color=MUTED, ha="center", va="top")
    ax.text(-1.16, g, "0.5774", fontsize=8.3, color=MUTED, ha="right", va="center")
    ax.text(-g, -1.13, "−0.5774", fontsize=8.3, color=MUTED, ha="center", va="top")
    ax.text(0.0, -0.02, "四点坐标 (±0.5774, ±0.5774)" + chr(10) + "权重均为 1",
            fontsize=8.2, color=INK, ha="center", va="center", linespacing=1.7)
    ax.text(-1.0, 1.58, "四边形", fontsize=9.2, color=INK, va="top")
    ax.text(-1.0, 1.34, "2×2 点：两轴各取 ±0.5774", fontsize=8.2, color=MUTED, va="top")
    ax.text(-1.0, -1.62, r"$g = 1/\sqrt{3} \approx 0.57735$", fontsize=8.8,
            color=MUTED, va="center", ha="left")
    ax.set_xlim(-1.78, 1.30); ax.set_ylim(-1.95, 1.62)
    ax.axis("off")

    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01, wspace=0.05)
    save(fig, "09", "fig09-02")


# ---------------------------------------------------------------- 图 9-3
def fig_9_3():
    nx, ny = 11, 5
    nodes = {(i, j): j * (nx + 1) + i for j in range(ny + 1) for i in range(nx + 1)}
    tris = []
    for j in range(ny):
        for i in range(nx):
            a, b = nodes[(i, j)], nodes[(i + 1, j)]
            c, d = nodes[(i + 1, j + 1)], nodes[(i, j + 1)]
            tris += [(a, b, c), (a, c, d)]
    n = len(nodes)
    nnz = np.zeros((n, n), dtype=float)
    for t in tris:
        for p in t:
            for q in t:
                nnz[p, q] = 1.0
    pos = lambda k: (k % (nx + 1), k // (nx + 1))

    fig = plt.figure(figsize=(6.8, 2.55))
    ax = fig.add_subplot(1, 2, 1)
    ax.set_aspect("equal")
    for j in range(ny + 1):
        ax.plot([0, nx], [j, j], color="#E5E7EB", lw=0.7, zorder=1)
    for i in range(nx + 1):
        ax.plot([i, i], [0, ny], color="#E5E7EB", lw=0.7, zorder=1)
    for t in tris:
        ax.add_patch(Polygon([pos(k) for k in t], closed=True, facecolor="none",
                             edgecolor=INK, lw=0.55, zorder=2))
    P = np.array([pos(k) for k in range(n)], float)
    ax.scatter(P[:, 0], P[:, 1], s=7, color=ACCENT, zorder=3, lw=0)
    ax.text(0.0, 1.22, "%d 个顶点，%d 个三角形" % (n, len(tris)), fontsize=8.6,
            color=INK, transform=ax.transAxes, va="top")
    ax.text(0.0, 1.09, "自由度按行优先编号", fontsize=8.4, color=MUTED,
            transform=ax.transAxes, va="top")
    ax.set_xlim(-0.5, nx + 0.5); ax.set_ylim(-0.5, ny + 0.5)
    ax.axis("off")

    ax = fig.add_subplot(1, 2, 2)
    ax.imshow(nnz, cmap="Greys", vmin=0, vmax=1, interpolation="nearest", origin="upper")
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_color("#D1D5DB")
    bw = nx + 2
    ax.plot([-0.5, n - 0.5], [bw - 0.5, bw - 0.5], color=ACCENT, lw=0.9, ls="--")
    ax.plot([bw - 0.5, bw - 0.5], [-0.5, n - 0.5], color=ACCENT, lw=0.9, ls="--")
    ax.text(0.0, 1.22, "阶数 %d，非零元 %d 个，占 %.1f%%"
            % (n, int(nnz.sum()), 100.0 * nnz.sum() / n ** 2), fontsize=8.6, color=INK,
            transform=ax.transAxes, va="top")
    ax.text(0.0, 1.09, "橙色虚线标出半带宽 %d" % bw, fontsize=8.4, color=MUTED,
            transform=ax.transAxes, va="top")
    fig.subplots_adjust(left=0.02, right=0.98, top=0.86, bottom=0.02, wspace=0.06)
    save(fig, "09", "fig09-03")
    print("n", n, "tris", len(tris), "nnz", int(nnz.sum()), "band", bw)


if __name__ == "__main__":
    fig_9_1()
    fig_9_2()
    fig_9_3()
